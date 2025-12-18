from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models import Lead, Deal, WorkPackage, BiddingPackage

def auto_assign_lowest_bidder():
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()

        # Fetch active work packages whose bidding is still open
        work_packages = (
            db.query(WorkPackage)
            .join(Deal, Deal.id == WorkPackage.deal_id)
            .join(Lead, Lead.id == Deal.lead_id)
            .filter(
                WorkPackage.bidding_status != "closed",
                Lead.triple_positive_timestamp.isnot(None)
            )
            .all()
        )

        for wp in work_packages:
            lead = wp.deal.lead

            bidding_end_time = (
                lead.triple_positive_timestamp +
                timedelta(days=wp.bidding_duration_days)
            )

            if now < bidding_end_time:
                continue

            # Get lowest bid
            lowest_bid = (
                db.query(BiddingPackage)
                .filter(BiddingPackage.work_package_id == wp.id)
                .order_by(BiddingPackage.bidding_amount.asc())
                .first()
            )

            if not lowest_bid:
                continue  # No bids received

            # Assign technician
            wp.assigned_technician_id = lowest_bid.technician_id
            wp.bidding_status = "closed"

            # Optional but recommended: assign technician to lead also
            lead.assigned_technician_id = lowest_bid.technician_id

            db.add(wp)
            db.add(lead)

        db.commit()

    except Exception as e:
        db.rollback()
        print("Auto assignment error:", e)

    finally:
        print(
            "Bidding scheduler executed at:",
            datetime.now(timezone.utc)
        )
        db.close()
