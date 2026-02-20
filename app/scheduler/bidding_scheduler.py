from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from app.database import SessionLocal
from app.models import Lead, Deal, WorkPackage
from app.models.bidding_package import BiddingPackage


def make_utc_aware(dt):
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def auto_assign_lowest_bidder():
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)

        # EAGER LOAD deal + lead to avoid N+1 queries
        work_packages = (
            db.query(WorkPackage)
            .options(
                joinedload(WorkPackage.deal).joinedload(Deal.lead)
            )
            .filter(
                or_(
                    WorkPackage.bidding_status.is_(None),
                    WorkPackage.bidding_status != "Closed"
                ),
                Deal.lead.has(Lead.triple_positive_timestamp.isnot(None))
            )
            .all()
        )

        affected_deal_ids = set()
        extended_deals_today = set()  # avoid multiple extensions per run

        for wp in work_packages:
            deal = wp.deal
            lead = deal.lead

            lead_ts = make_utc_aware(lead.triple_positive_timestamp)
            bidding_end_time = lead_ts + timedelta(days=wp.bidding_duration_days)

            # Skip if bidding still active
            if now < bidding_end_time:
                continue

            # get lowest bid directly (no loading all)
            lowest_bid = (
                db.query(BiddingPackage.technician_id, BiddingPackage.bidding_amount)
                .filter(BiddingPackage.work_package_id == wp.id)
                .order_by(BiddingPackage.bidding_amount.asc())
                .limit(1)
                .first()
            )

            if lowest_bid:
                wp.assigned_technician_id = lowest_bid.technician_id
                wp.bidding_status = "Closed"
                affected_deal_ids.add(deal.id)

                print(
                    f"Assigned technician {lowest_bid.technician_id} "
                    f"to work_package {wp.id}"
                )

            else:
                if wp.bidding_status != "Reopen":
                    wp.bidding_status = "Reopen"
                    print(f"No bids. Work_package {wp.id} marked as Reopen")

                # DEADLINE EXTENSION (only once per deal per run)
                if deal.id not in extended_deals_today and deal.expected_end_date_or_deadline:
                    deal_deadline = make_utc_aware(deal.expected_end_date_or_deadline)

                    if deal_deadline.date() == now.date():
                        max_duration_hours = (deal.max_duration or 0) * 24

                        if max_duration_hours > 0:
                            new_deadline = deal_deadline + timedelta(hours=max_duration_hours)
                            deal.expected_end_date_or_deadline = new_deadline

                            extended_deals_today.add(deal.id)

                            print(
                                f"Deal {deal.id} deadline extended to {new_deadline} "
                                f"(+{max_duration_hours} hrs)"
                            )

        # DEAL AUTO CLOSE (batch check per deal)
        if affected_deal_ids:
            unassigned_map = (
                db.query(WorkPackage.deal_id)
                .filter(
                    WorkPackage.deal_id.in_(affected_deal_ids),
                    WorkPackage.assigned_technician_id.is_(None)
                )
                .distinct()
                .all()
            )
            unassigned_deal_ids = {d[0] for d in unassigned_map}

            # deals that have no unassigned WPs
            closable_deals = affected_deal_ids - unassigned_deal_ids

            if closable_deals:
                deals_to_close = (
                    db.query(Deal)
                    .filter(
                        Deal.id.in_(closable_deals),
                        Deal.deal_close_date.is_(None)
                    )
                    .all()
                )

                for deal in deals_to_close:
                    deal.deal_close_date = now
                    print(f"Deal {deal.id} closed successfully.")

        db.commit()

    except Exception as e:
        db.rollback()
        print("Auto assignment error:", e)

    finally:
        print("Bidding scheduler executed at:", datetime.now(timezone.utc))
        db.close()