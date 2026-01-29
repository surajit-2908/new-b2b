from app.database import SessionLocal
from app.models.lead import Lead

lead_statuses = [
    {"old_name" : "new", "new_name": "New"},
    {"old_name" : "Not interested", "new_name": "Not Interested"}
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
    print("Update Lead statuses seeded successfully!")