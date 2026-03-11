import os
from datetime import date, timedelta
from db import SessionLocal, Case, Judge, Lawyer, Hearing, Verdict, CaseStatusEnum, HearingStatusEnum, create_tables

def seed_db():
    db = SessionLocal()

    # Create Tables if they don't exist
    create_tables()

    # Check if there's already data
    if db.query(Judge).count() > 0:
        print("Database already contains data, proceeding anyway...")

    # Clear existing data just in case
    db.query(Hearing).delete()
    db.query(Verdict).delete()
    db.query(Case).delete()
    db.query(Judge).delete()
    db.query(Lawyer).delete()
    db.commit()

    # Create Judges
    j1 = Judge(name="Hon. Alan Turing", court_room="Room 101")
    j2 = Judge(name="Hon. Grace Hopper", court_room="Room 102")
    db.add_all([j1, j2])
    db.commit()
    db.refresh(j1)
    db.refresh(j2)

    # Create Lawyers
    l1 = Lawyer(name="Ada Lovelace", bar_id="BAR1001")
    l2 = Lawyer(name="Charles Babbage", bar_id="BAR1002")
    db.add_all([l1, l2])
    db.commit()
    db.refresh(l1)
    db.refresh(l2)

    # Create Cases
    c1 = Case(case_number="CASE-2023-001", type="Civil", status=CaseStatusEnum.FILED, filed_date=date.today() - timedelta(days=30))
    c2 = Case(case_number="CASE-2023-002", type="Criminal", status=CaseStatusEnum.ONGOING, filed_date=date.today() - timedelta(days=60))
    c3 = Case(case_number="CASE-2023-003", type="Corporate", status=CaseStatusEnum.CLOSED, filed_date=date.today() - timedelta(days=90))
    db.add_all([c1, c2, c3])
    db.commit()
    db.refresh(c1)
    db.refresh(c2)
    db.refresh(c3)

    # Create Hearings
    h1 = Hearing(case_id=c1.id, judge_id=j1.id, hearing_date=date.today() + timedelta(days=5), status=HearingStatusEnum.SCHEDULED)
    h2 = Hearing(case_id=c2.id, judge_id=j2.id, hearing_date=date.today() - timedelta(days=5), status=HearingStatusEnum.COMPLETED)
    db.add_all([h1, h2])
    db.commit()

    # Create Verdict
    v1 = Verdict(case_id=c3.id, decision="Guilty on all counts", decision_date=date.today() - timedelta(days=10))
    db.add(v1)
    db.commit()

    print("Seed data added successfully.")
    db.close()

if __name__ == "__main__":
    seed_db()
