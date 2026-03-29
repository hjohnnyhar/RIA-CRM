"""Seed the CRM with realistic RIA firm data."""
from app import app, db
from models import Household, Person, Account, Task, Meeting, MeetingAttendee
from datetime import date, time, timedelta
import os

TODAY = date(2026, 3, 24)


def seed():
    # Wipe existing data
    db_path = os.path.join(app.instance_path, "ria_crm.db")
    with app.app_context():
        db.drop_all()
        db.create_all()

        # ── Household 1: The Martins ──────────────────────────────────
        h1 = Household(name="Martin Family", notes="High-net-worth retirees. Annual review in April. Prefer morning meetings. Snowbirds — in FL Nov-Mar.")
        db.session.add(h1)
        db.session.flush()

        p1a = Person(first_name="Robert", last_name="Martin", email="robert.martin@email.com", phone="(312) 555-0142", role="Client", is_primary=True, household_id=h1.id)
        p1b = Person(first_name="Linda", last_name="Martin", email="linda.martin@email.com", phone="(312) 555-0143", role="Spouse", household_id=h1.id)
        p1c = Person(first_name="James", last_name="Martin", email="james.martin@email.com", phone="(312) 555-0199", role="Beneficiary", household_id=h1.id)
        db.session.add_all([p1a, p1b, p1c])
        db.session.flush()

        db.session.add_all([
            Account(name="Martin Joint Brokerage", account_type="Brokerage", custodian="Charles Schwab", account_number="****4821", balance=1_250_000, household_id=h1.id),
            Account(name="Robert IRA", account_type="IRA", custodian="Charles Schwab", account_number="****4822", balance=875_000, household_id=h1.id),
            Account(name="Linda Roth IRA", account_type="Roth IRA", custodian="Charles Schwab", account_number="****4823", balance=340_000, household_id=h1.id),
            Account(name="Martin Family Trust", account_type="Trust", custodian="Charles Schwab", account_number="****4824", balance=2_100_000, household_id=h1.id),
        ])

        db.session.add_all([
            Task(title="Annual portfolio review", description="Review asset allocation, rebalance if needed. Discuss RMD strategy for Robert.", status="Open", priority="High", due_date=TODAY + timedelta(days=14), assigned_to="Sarah Chen", household_id=h1.id),
            Task(title="Update beneficiary designations", description="James needs to be added as contingent beneficiary on Roth IRA.", status="Open", priority="Medium", due_date=TODAY + timedelta(days=7), assigned_to="Mike Torres", household_id=h1.id),
            Task(title="RMD calculation for 2026", description="Calculate required minimum distribution for Robert's IRA.", status="In Progress", priority="High", due_date=TODAY + timedelta(days=21), assigned_to="Sarah Chen", household_id=h1.id),
        ])

        m1 = Meeting(title="Martin Annual Review", meeting_date=TODAY + timedelta(days=14), meeting_time=time(9, 30), duration_minutes=90, location="Conference Room A", notes="Bring updated financial plan. Discuss estate planning changes.", household_id=h1.id)
        db.session.add(m1)
        db.session.flush()
        db.session.add_all([MeetingAttendee(meeting_id=m1.id, person_id=p1a.id), MeetingAttendee(meeting_id=m1.id, person_id=p1b.id)])

        # ── Household 2: The Nguyens ─────────────────────────────────
        h2 = Household(name="Nguyen Family", notes="Dual income tech professionals. Aggressive growth allocation. Interested in ESG. Kids' education is top priority.")
        db.session.add(h2)
        db.session.flush()

        p2a = Person(first_name="David", last_name="Nguyen", email="david.nguyen@techcorp.com", phone="(415) 555-0287", role="Client", is_primary=True, household_id=h2.id)
        p2b = Person(first_name="Amy", last_name="Nguyen", email="amy.nguyen@biostart.com", phone="(415) 555-0288", role="Spouse", household_id=h2.id)
        db.session.add_all([p2a, p2b])
        db.session.flush()

        db.session.add_all([
            Account(name="Nguyen Joint Brokerage", account_type="Brokerage", custodian="Fidelity", account_number="****7731", balance=420_000, household_id=h2.id),
            Account(name="David 401(k)", account_type="401(k)", custodian="Fidelity", account_number="****7732", balance=385_000, household_id=h2.id),
            Account(name="Amy 401(k)", account_type="401(k)", custodian="Vanguard", account_number="****7733", balance=290_000, household_id=h2.id),
            Account(name="Nguyen 529 — Lily", account_type="529 Plan", custodian="Fidelity", account_number="****7734", balance=85_000, household_id=h2.id),
            Account(name="Nguyen 529 — Ethan", account_type="529 Plan", custodian="Fidelity", account_number="****7735", balance=62_000, household_id=h2.id),
        ])

        db.session.add_all([
            Task(title="Backdoor Roth conversion", description="Execute backdoor Roth for both David and Amy for 2026.", status="Open", priority="High", due_date=TODAY + timedelta(days=10), assigned_to="Sarah Chen", household_id=h2.id),
            Task(title="ESG portfolio transition", description="Research ESG-aligned ETFs to replace current large-cap holdings.", status="In Progress", priority="Medium", due_date=TODAY + timedelta(days=30), assigned_to="Mike Torres", household_id=h2.id),
            Task(title="529 contribution reminder", description="Remind Nguyens about annual 529 contribution before tax deadline.", status="Open", priority="Low", due_date=TODAY + timedelta(days=5), assigned_to="Sarah Chen", household_id=h2.id),
        ])

        m2 = Meeting(title="Nguyen Q1 Check-in", meeting_date=TODAY + timedelta(days=3), meeting_time=time(16, 0), duration_minutes=45, location="Zoom", notes="Quick portfolio check. Discuss backdoor Roth timing.", household_id=h2.id)
        db.session.add(m2)
        db.session.flush()
        db.session.add_all([MeetingAttendee(meeting_id=m2.id, person_id=p2a.id), MeetingAttendee(meeting_id=m2.id, person_id=p2b.id)])

        # ── Household 3: The Patels ──────────────────────────────────
        h3 = Household(name="Patel Family", notes="Business owners. Own a chain of dental practices. Complex tax situation. Looking at succession planning.")
        db.session.add(h3)
        db.session.flush()

        p3a = Person(first_name="Raj", last_name="Patel", email="raj@pateldental.com", phone="(214) 555-0391", role="Client", is_primary=True, household_id=h3.id)
        p3b = Person(first_name="Priya", last_name="Patel", email="priya@pateldental.com", phone="(214) 555-0392", role="Spouse", household_id=h3.id)
        p3c = Person(first_name="Anita", last_name="Patel", email="anita.patel@gmail.com", phone="(214) 555-0393", role="Beneficiary", household_id=h3.id)
        db.session.add_all([p3a, p3b, p3c])
        db.session.flush()

        db.session.add_all([
            Account(name="Patel Brokerage", account_type="Brokerage", custodian="TD Ameritrade", account_number="****1155", balance=780_000, household_id=h3.id),
            Account(name="Raj SEP IRA", account_type="SEP IRA", custodian="TD Ameritrade", account_number="****1156", balance=1_450_000, household_id=h3.id),
            Account(name="Priya IRA", account_type="IRA", custodian="TD Ameritrade", account_number="****1157", balance=520_000, household_id=h3.id),
            Account(name="Patel Dental Profit Sharing", account_type="Other", custodian="TD Ameritrade", account_number="****1158", balance=680_000, household_id=h3.id),
            Account(name="Patel Life Insurance", account_type="Insurance", custodian="Northwestern Mutual", account_number="****1159", balance=1_000_000, household_id=h3.id),
        ])

        db.session.add_all([
            Task(title="Business valuation update", description="Get updated valuation of Patel Dental for succession planning.", status="Open", priority="High", due_date=TODAY + timedelta(days=45), assigned_to="Mike Torres", household_id=h3.id),
            Task(title="SEP IRA contribution for 2025", description="Confirm max SEP contribution was made before tax filing.", status="Done", priority="High", due_date=TODAY - timedelta(days=10), assigned_to="Sarah Chen", household_id=h3.id),
            Task(title="Succession plan draft", description="Work with estate attorney on buy-sell agreement for dental practices.", status="In Progress", priority="High", due_date=TODAY + timedelta(days=60), assigned_to="Mike Torres", household_id=h3.id),
        ])

        m3 = Meeting(title="Patel Succession Planning", meeting_date=TODAY + timedelta(days=7), meeting_time=time(11, 0), duration_minutes=120, location="Patel Dental HQ", notes="Bring draft buy-sell agreement. CPA will attend.", household_id=h3.id)
        db.session.add(m3)
        db.session.flush()
        db.session.add_all([MeetingAttendee(meeting_id=m3.id, person_id=p3a.id), MeetingAttendee(meeting_id=m3.id, person_id=p3b.id)])

        # ── Household 4: Margaret Sullivan (single client) ───────────
        h4 = Household(name="Sullivan, Margaret", notes="Recent widow. Conservative allocation. Needs income strategy from late husband's accounts. Emotionally sensitive — be patient.")
        db.session.add(h4)
        db.session.flush()

        p4a = Person(first_name="Margaret", last_name="Sullivan", email="margaret.sullivan@email.com", phone="(617) 555-0544", role="Client", is_primary=True, household_id=h4.id)
        p4b = Person(first_name="Kevin", last_name="Sullivan", email="kevin.sullivan@email.com", phone="(617) 555-0545", role="Beneficiary", household_id=h4.id)
        db.session.add_all([p4a, p4b])
        db.session.flush()

        db.session.add_all([
            Account(name="Margaret Brokerage", account_type="Brokerage", custodian="Fidelity", account_number="****2201", balance=310_000, household_id=h4.id),
            Account(name="Inherited IRA (from Thomas)", account_type="IRA", custodian="Fidelity", account_number="****2202", balance=640_000, household_id=h4.id),
            Account(name="Margaret Annuity", account_type="Annuity", custodian="Jackson National", account_number="****2203", balance=250_000, household_id=h4.id),
        ])

        db.session.add_all([
            Task(title="Inherited IRA distribution plan", description="Set up 10-year distribution schedule for inherited IRA per SECURE Act.", status="Open", priority="High", due_date=TODAY + timedelta(days=14), assigned_to="Sarah Chen", household_id=h4.id),
            Task(title="Income needs analysis", description="Build cash flow plan — Margaret needs $5K/month from portfolio.", status="In Progress", priority="High", due_date=TODAY + timedelta(days=7), assigned_to="Sarah Chen", household_id=h4.id),
            Task(title="Annuity review", description="Review annuity fees and surrender schedule. Consider alternatives.", status="Open", priority="Medium", due_date=TODAY + timedelta(days=30), assigned_to="Mike Torres", household_id=h4.id),
        ])

        m4 = Meeting(title="Sullivan Income Planning", meeting_date=TODAY + timedelta(days=5), meeting_time=time(10, 0), duration_minutes=60, location="Office — Private Room", notes="Sensitive meeting. Bring income projection printout. Kevin may join by phone.", household_id=h4.id)
        db.session.add(m4)
        db.session.flush()
        db.session.add(MeetingAttendee(meeting_id=m4.id, person_id=p4a.id))

        # ── Household 5: The Johnsons ────────────────────────────────
        h5 = Household(name="Johnson Family", notes="Young professionals, just married. Starting to build wealth. Want to buy a house in 2 years. Need basic financial plan.")
        db.session.add(h5)
        db.session.flush()

        p5a = Person(first_name="Marcus", last_name="Johnson", email="marcus.johnson@gmail.com", phone="(404) 555-0672", role="Client", is_primary=True, household_id=h5.id)
        p5b = Person(first_name="Keisha", last_name="Johnson", email="keisha.johnson@gmail.com", phone="(404) 555-0673", role="Spouse", household_id=h5.id)
        db.session.add_all([p5a, p5b])
        db.session.flush()

        db.session.add_all([
            Account(name="Johnson Joint Brokerage", account_type="Brokerage", custodian="Vanguard", account_number="****8801", balance=45_000, household_id=h5.id),
            Account(name="Marcus Roth IRA", account_type="Roth IRA", custodian="Vanguard", account_number="****8802", balance=32_000, household_id=h5.id),
            Account(name="Keisha 401(k)", account_type="401(k)", custodian="Fidelity", account_number="****8803", balance=28_000, household_id=h5.id),
        ])

        db.session.add_all([
            Task(title="Financial plan — first draft", description="Build initial financial plan. Focus on house down payment timeline and emergency fund.", status="In Progress", priority="Medium", due_date=TODAY + timedelta(days=10), assigned_to="Mike Torres", household_id=h5.id),
            Task(title="Insurance review", description="Johnsons have no life or disability insurance. Get quotes.", status="Open", priority="Medium", due_date=TODAY + timedelta(days=20), assigned_to="Mike Torres", household_id=h5.id),
        ])

        m5 = Meeting(title="Johnson Plan Presentation", meeting_date=TODAY + timedelta(days=10), meeting_time=time(17, 30), duration_minutes=60, location="Zoom", notes="After-hours meeting. Present first draft of financial plan.", household_id=h5.id)
        db.session.add(m5)
        db.session.flush()
        db.session.add_all([MeetingAttendee(meeting_id=m5.id, person_id=p5a.id), MeetingAttendee(meeting_id=m5.id, person_id=p5b.id)])

        # ── Internal team tasks (no household) ───────────────────────
        db.session.add_all([
            Task(title="Q1 compliance review", description="Complete quarterly compliance checklist and file with CCO.", status="Open", priority="High", due_date=TODAY + timedelta(days=7), assigned_to="Sarah Chen"),
            Task(title="Update ADV Part 2 brochure", description="Annual update of Form ADV Part 2A. Due to SEC by March 31.", status="In Progress", priority="High", due_date=TODAY + timedelta(days=7), assigned_to="Mike Torres"),
            Task(title="CRM data cleanup", description="Audit all household records for completeness. Flag missing emails and phone numbers.", status="Open", priority="Low", due_date=TODAY + timedelta(days=30), assigned_to="Sarah Chen"),
            Task(title="Prepare quarterly newsletter", description="Draft Q1 market commentary and firm update for client distribution.", status="Open", priority="Medium", due_date=TODAY + timedelta(days=14), assigned_to="Mike Torres"),
        ])

        # ── Extra meetings this week/month ────────────────────────────
        m6 = Meeting(title="Team Standup", meeting_date=TODAY, meeting_time=time(8, 30), duration_minutes=15, location="Office", notes="Daily standup.")
        m7 = Meeting(title="Team Standup", meeting_date=TODAY + timedelta(days=1), meeting_time=time(8, 30), duration_minutes=15, location="Office", notes="Daily standup.")
        m8 = Meeting(title="Compliance Committee", meeting_date=TODAY + timedelta(days=2), meeting_time=time(14, 0), duration_minutes=60, location="Conference Room B", notes="Q1 compliance review. Bring updated policies.")
        m9 = Meeting(title="New Prospect: Williams Family", meeting_date=TODAY + timedelta(days=4), meeting_time=time(13, 0), duration_minutes=60, location="Conference Room A", notes="Referral from the Martins. $500K+ in assets. Looking for retirement planning.")
        db.session.add_all([m6, m7, m8, m9])

        db.session.commit()
        print("Seeded successfully!")
        print(f"  Households: {Household.query.count()}")
        print(f"  People:     {Person.query.count()}")
        print(f"  Accounts:   {Account.query.count()}")
        print(f"  Tasks:      {Task.query.count()}")
        print(f"  Meetings:   {Meeting.query.count()}")


if __name__ == "__main__":
    seed()
