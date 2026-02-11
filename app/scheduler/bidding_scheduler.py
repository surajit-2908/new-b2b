from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_
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

        work_packages = (
            db.query(WorkPackage)
            .join(Deal, Deal.id == WorkPackage.deal_id)
            .join(Lead, Lead.id == Deal.lead_id)
            .filter(
                or_(
                    WorkPackage.bidding_status.is_(None),
                    WorkPackage.bidding_status != "Closed"
                ),
                Lead.triple_positive_timestamp.isnot(None)
            )
            .all()
        )
        
        affected_deal_ids = set()

        for wp in work_packages:
            lead = wp.deal.lead
            lead_ts = make_utc_aware(lead.triple_positive_timestamp)

            bidding_end_time = lead_ts + timedelta(days=wp.bidding_duration_days)

            # Skip if bidding still active
            if now < bidding_end_time:
                continue

            lowest_bid = (
                db.query(BiddingPackage)
                .filter(BiddingPackage.work_package_id == wp.id)
                .order_by(BiddingPackage.bidding_amount.asc())
                .first()
            )

            # NEW LOGIC
            if lowest_bid:
                wp.assigned_technician_id = lowest_bid.technician_id
                wp.bidding_status = "Closed"

                affected_deal_ids.add(wp.deal_id)
                
                print(
                    f"Assigned technician {lowest_bid.technician_id} "
                    f"to work_package {wp.id}"
                )
            else:
                if wp.bidding_status != "Reopen":
                    wp.bidding_status = "Reopen"
                    print(f"No bids. Work_package {wp.id} marked as Reopen")

        # DEAL AUTO CLOSE LOGIC
        for deal_id in affected_deal_ids:

            # Check if any work package is still unassigned
            unassigned_wp = db.query(WorkPackage).filter(
                WorkPackage.deal_id == deal_id,
                WorkPackage.assigned_technician_id.is_(None)
            ).first()

            if not unassigned_wp:
                deal = db.query(Deal).filter(Deal.id == deal_id).first()

                if deal and deal.deal_close_date is None:
                    deal.deal_close_date = datetime.now(timezone.utc)
                    print(f"Deal {deal_id} closed successfully.")
                    
        db.commit()

    except Exception as e:
        db.rollback()
        print("Auto assignment error:", e)

    finally:
        print("Bidding scheduler executed at:", datetime.now(timezone.utc))
        db.close()
