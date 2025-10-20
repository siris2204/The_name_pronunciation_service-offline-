from sqlalchemy.orm import Session
from sqlalchemy import func
from .db import engine, SessionLocal, Base
from . import models

# ---- Original names (keep yours here; trimmed for brevity; you can paste your full previous list) ----
NAMES_BASE = [
    "Aarav","Aadya","Advait","Aisha","Akshay","Alia","Amara","Amish","Ananya","Anika",
    "Anirudh","Anita","Arjun","Arvind","Ashwin","Avani","Bhavya","Chetan","Chitra","Daksha",
    "Dev","Diya","Divya","Farhan","Gaurav","Harini","Hrithik","Ishaan","Ira","Ishika",
    "Jahnavi","Jaspreet","Jay","Jiya","Kabir","Kaira","Karthik","Khushi","Krishna","Lakshmi",
    "Lavanya","Madhav","Mahima","Manish","Meera","Mira","Mithun","Mohit","Namrata","Neeraj",
    "Neha","Nikhil","Nisha","Om","Pallavi","Parth","Pranav","Prisha","Priya","Raghav",
    "Rahul","Raj","Rakesh","Raman","Rhea","Rishabh","Riya","Rohit","Saisha","Sakshi",
    "Samarth","Sameer","Sana","Sanjana","Sanya","Sara","Sarika","Shanaya","Shiv","Shruti",
    "Shreya","Sid","Simran","Sneha","Soham","Sumit","Tanmay","Tara","Tanishq","Tanya",
    "Tarun","Uma","Urvi","Vaibhav","Ved","Veer","Veera","Vikram","Vikrant","Vinay",
    "Vishal","Yash","Zara","Zoya","Aditya","Abhinav","Abhishek","Amruta","Anusha","Bhavana",
    "Charan","Deepak","Indira","Jyothi","Keerthi","Lalitha","Mounika","Naveen","Praveen","Suresh",
    "Teja","Varun","Vamsi","Hemanth","Siri","Pendyala"
]

# ---- Your extra names to include (ignore if already present) ----
EXTRA_NAMES = [
    "Aarav", "Bodhi", "Chloe", "Diya", "Ethan", "Fatima", "Gael", "Hana", "Ivan", "Jasmine", "Kenji",
    "Luna", "Marco", "Nyla", "Omar", "Priya", "Quinn", "Rohan", "Sofia", "Tenzin", "Umi", "Vikas", "Wei",
    "Xena", "Yara", "Zain", "Ananya", "Caleb", "Elara", "Felix", "Giselle", "Hector", "Iris", "Jamal", "Kai",
    "Layla", "Mateo", "Noa", "Orla", "Pablo", "Rhea", "Samuel", "Tara", "Uri", "Vera", "Wyatt", "Zoe"
]

def _order_preserving_ci_union(base: list[str], extra: list[str]) -> list[str]:
    """Case-insensitive, order-preserving union (first occurrence wins)."""
    seen = set()
    out = []
    for nm in base + extra:
        key = nm.casefold()
        if key not in seen:
            seen.add(key)
            out.append(nm)
    return out

def seed():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Build final unique list (case-insensitive)
    names = _order_preserving_ci_union(NAMES_BASE, EXTRA_NAMES)

    db: Session = SessionLocal()
    added = 0
    try:
        for nm in names:
            # case-insensitive existence check:
            exists = db.query(models.Name.id).filter(
                func.lower(models.Name.name) == nm.lower()
            ).first()
            if exists:
                continue
            db.add(models.Name(name=nm, audio_path=None))
            added += 1

        if added:
            db.commit()

        total = db.query(models.Name).count()
        print(f"Added {added} new names. Total rows now: {total}.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
