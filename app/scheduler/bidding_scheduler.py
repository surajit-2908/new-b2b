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

        for wp in work_packages:
            lead = wp.deal.lead

            lead_ts = make_utc_aware(lead.triple_positive_timestamp)

            bidding_end_time = (
                lead_ts + timedelta(days=wp.bidding_duration_days)
            )

            if now < bidding_end_time:
                continue

            lowest_bid = (
                db.query(BiddingPackage)
                .filter(BiddingPackage.work_package_id == wp.id)
                .order_by(BiddingPackage.bidding_amount.asc())
                .first()
            )

            if not lowest_bid:
                print(f"No bids for work_package {wp.id}")
                continue

            wp.assigned_technician_id = lowest_bid.technician_id
            wp.bidding_status = "Closed"

            print(
                f"Assigned technician {lowest_bid.technician_id} "
                f"to work_package {wp.id}"
            )

        db.commit()

    except Exception as e:
        db.rollback()
        print("Auto assignment error:", e)

    finally:
        print("Bidding scheduler executed at:", datetime.now(timezone.utc))
        db.close()
