from app.database import SessionLocal
from app.models.lead import Lead

lead_statuses = [
    {"old_name" : "Positive lead", "new_name": "Qualified Lead"},
    {"old_name" : "Double Positive", "new_name": "Active Lead"},
    {"old_name" : "Triple Positive", "new_name": "Fulfillment Stage"},
]


def seed_lead_statuses():
    db = SessionLocal()
    for status in lead_statuses:
        db.query(Lead).filter(
            Lead.lead_status == status["old_name"]
        ).update(
            {Lead.lead_status: status["new_name"]},
            synchronize_session=False
        )

    db.commit()
    
    
if __name__ == "__main__":
    seed_lead_statuses()
    print("Lead statuses seeded successfully!")