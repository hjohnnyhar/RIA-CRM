from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time

db = SQLAlchemy()


class Household(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    people = db.relationship("Person", backref="household", lazy=True, cascade="all, delete-orphan")
    accounts = db.relationship("Account", backref="household", lazy=True, cascade="all, delete-orphan")
    tasks = db.relationship("Task", backref="household", lazy=True, cascade="all, delete-orphan")
    meetings = db.relationship("Meeting", backref="household", lazy=True, cascade="all, delete-orphan")

    @property
    def total_aum(self):
        return sum(a.balance for a in self.accounts)

    @property
    def primary_contact(self):
        for p in self.people:
            if p.is_primary:
                return p
        return self.people[0] if self.people else None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "notes": self.notes,
            "total_aum": self.total_aum,
            "primary_contact": self.primary_contact.to_dict() if self.primary_contact else None,
            "people_count": len(self.people),
            "accounts_count": len(self.accounts),
            "created_at": self.created_at.isoformat(),
        }


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), default="")
    phone = db.Column(db.String(50), default="")
    role = db.Column(db.String(50), default="Client")  # Client, Spouse, Beneficiary, Trustee, etc.
    is_primary = db.Column(db.Boolean, default=False)
    household_id = db.Column(db.Integer, db.ForeignKey("household.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    meeting_attendees = db.relationship("MeetingAttendee", backref="person", lazy=True, cascade="all, delete-orphan")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_primary": self.is_primary,
            "household_id": self.household_id,
            "created_at": self.created_at.isoformat(),
        }


ACCOUNT_TYPES = [
    "Brokerage", "IRA", "Roth IRA", "401(k)", "SEP IRA",
    "Trust", "529 Plan", "Annuity", "Insurance", "Other"
]


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)
    custodian = db.Column(db.String(200), default="")
    account_number = db.Column(db.String(100), default="")
    balance = db.Column(db.Float, default=0.0)
    household_id = db.Column(db.Integer, db.ForeignKey("household.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "account_type": self.account_type,
            "custodian": self.custodian,
            "account_number": self.account_number,
            "balance": self.balance,
            "household_id": self.household_id,
            "created_at": self.created_at.isoformat(),
        }


TASK_STATUSES = ["Open", "In Progress", "Done"]
TASK_PRIORITIES = ["Low", "Medium", "High"]


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="Open")
    priority = db.Column(db.String(10), default="Medium")
    due_date = db.Column(db.Date, nullable=True)
    assigned_to = db.Column(db.String(100), default="")  # team member name
    household_id = db.Column(db.Integer, db.ForeignKey("household.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "assigned_to": self.assigned_to,
            "household_id": self.household_id,
            "household_name": self.household.name if self.household else None,
            "created_at": self.created_at.isoformat(),
        }


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    meeting_date = db.Column(db.Date, nullable=False)
    meeting_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    location = db.Column(db.String(200), default="")
    notes = db.Column(db.Text, default="")
    household_id = db.Column(db.Integer, db.ForeignKey("household.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendees = db.relationship("MeetingAttendee", backref="meeting", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "meeting_date": self.meeting_date.isoformat(),
            "meeting_time": self.meeting_time.strftime("%H:%M"),
            "duration_minutes": self.duration_minutes,
            "location": self.location,
            "notes": self.notes,
            "household_id": self.household_id,
            "household_name": self.household.name if self.household else None,
            "attendees": [a.person.to_dict() for a in self.attendees],
            "created_at": self.created_at.isoformat(),
        }


class MeetingAttendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meeting.id"), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=False)
