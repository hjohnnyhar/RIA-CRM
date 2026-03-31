from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from models import db, Household, Person, Account, Task, Meeting, MeetingAttendee, User
from models import ACCOUNT_TYPES, TASK_STATUSES, TASK_PRIORITIES, USER_ROLES
from datetime import datetime, date, time
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

_db_url = os.getenv("DATABASE_URL", "sqlite:///ria_crm.db")
# Heroku/some platforms set postgres:// which SQLAlchemy 2.x requires as postgresql://
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = _db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")

db.init_app(app)

with app.app_context():
    db.create_all()


# ── Dashboard ──────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"db": app.config["SQLALCHEMY_DATABASE_URI"][:30] + "..."})


@app.route("/")
def dashboard():
    households = Household.query.all()
    total_aum = sum(h.total_aum for h in households)
    open_tasks = Task.query.filter(Task.status != "Done").count()
    upcoming_meetings = Meeting.query.filter(Meeting.meeting_date >= date.today()).order_by(
        Meeting.meeting_date, Meeting.meeting_time
    ).limit(5).all()
    recent_tasks = Task.query.filter(Task.status != "Done").order_by(Task.due_date.asc().nullslast()).limit(5).all()
    return render_template(
        "dashboard.html",
        households=households,
        total_aum=total_aum,
        household_count=len(households),
        people_count=Person.query.count(),
        open_tasks=open_tasks,
        upcoming_meetings=upcoming_meetings,
        recent_tasks=recent_tasks,
    )


# ── Households ─────────────────────────────────────────────────────────────────

@app.route("/households")
def household_list():
    households = Household.query.order_by(Household.name).all()
    return render_template("households.html", households=households)


@app.route("/households/new", methods=["GET", "POST"])
def household_new():
    if request.method == "POST":
        h = Household(name=request.form["name"], notes=request.form.get("notes", ""))
        db.session.add(h)
        db.session.commit()
        flash(f"Household '{h.name}' created.", "success")
        return redirect(url_for("household_detail", id=h.id))
    return render_template("household_form.html", household=None)


@app.route("/households/<int:id>")
def household_detail(id):
    h = Household.query.get_or_404(id)
    return render_template(
        "household_detail.html",
        household=h,
        account_types=ACCOUNT_TYPES,
        task_statuses=TASK_STATUSES,
        task_priorities=TASK_PRIORITIES,
    )


@app.route("/households/<int:id>/edit", methods=["GET", "POST"])
def household_edit(id):
    h = Household.query.get_or_404(id)
    if request.method == "POST":
        h.name = request.form["name"]
        h.notes = request.form.get("notes", "")
        db.session.commit()
        flash(f"Household '{h.name}' updated.", "success")
        return redirect(url_for("household_detail", id=h.id))
    return render_template("household_form.html", household=h)


@app.route("/households/<int:id>/delete", methods=["POST"])
def household_delete(id):
    h = Household.query.get_or_404(id)
    name = h.name
    db.session.delete(h)
    db.session.commit()
    flash(f"Household '{name}' deleted.", "success")
    return redirect(url_for("household_list"))


# ── People ─────────────────────────────────────────────────────────────────────

@app.route("/households/<int:hid>/people/add", methods=["POST"])
def person_add(hid):
    Household.query.get_or_404(hid)
    p = Person(
        first_name=request.form["first_name"],
        last_name=request.form["last_name"],
        email=request.form.get("email", ""),
        phone=request.form.get("phone", ""),
        role=request.form.get("role", "Client"),
        is_primary="is_primary" in request.form,
        household_id=hid,
    )
    db.session.add(p)
    db.session.commit()
    flash(f"Added {p.full_name}.", "success")
    return redirect(url_for("household_detail", id=hid))


@app.route("/people/<int:id>/edit", methods=["POST"])
def person_edit(id):
    p = Person.query.get_or_404(id)
    p.first_name = request.form["first_name"]
    p.last_name = request.form["last_name"]
    p.email = request.form.get("email", "")
    p.phone = request.form.get("phone", "")
    p.role = request.form.get("role", "Client")
    p.is_primary = "is_primary" in request.form
    db.session.commit()
    flash(f"Updated {p.full_name}.", "success")
    return redirect(url_for("household_detail", id=p.household_id))


@app.route("/people/<int:id>/delete", methods=["POST"])
def person_delete(id):
    p = Person.query.get_or_404(id)
    hid = p.household_id
    db.session.delete(p)
    db.session.commit()
    flash("Person removed.", "success")
    return redirect(url_for("household_detail", id=hid))


# ── Accounts ───────────────────────────────────────────────────────────────────

@app.route("/households/<int:hid>/accounts/add", methods=["POST"])
def account_add(hid):
    Household.query.get_or_404(hid)
    a = Account(
        name=request.form["name"],
        account_type=request.form["account_type"],
        custodian=request.form.get("custodian", ""),
        account_number=request.form.get("account_number", ""),
        balance=float(request.form.get("balance", 0)),
        household_id=hid,
    )
    db.session.add(a)
    db.session.commit()
    flash(f"Account '{a.name}' added.", "success")
    return redirect(url_for("household_detail", id=hid))


@app.route("/accounts/<int:id>/edit", methods=["POST"])
def account_edit(id):
    a = Account.query.get_or_404(id)
    a.name = request.form["name"]
    a.account_type = request.form["account_type"]
    a.custodian = request.form.get("custodian", "")
    a.account_number = request.form.get("account_number", "")
    a.balance = float(request.form.get("balance", 0))
    db.session.commit()
    flash(f"Account '{a.name}' updated.", "success")
    return redirect(url_for("household_detail", id=a.household_id))


@app.route("/accounts/<int:id>/delete", methods=["POST"])
def account_delete(id):
    a = Account.query.get_or_404(id)
    hid = a.household_id
    db.session.delete(a)
    db.session.commit()
    flash("Account removed.", "success")
    return redirect(url_for("household_detail", id=hid))


# ── Users (internal staff) ────────────────────────────────────────────────────

@app.route("/users")
def user_list():
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template("users.html", users=users, roles=USER_ROLES)


@app.route("/users/new", methods=["POST"])
def user_new():
    u = User(
        first_name=request.form["first_name"],
        last_name=request.form["last_name"],
        email=request.form.get("email", ""),
        role=request.form.get("role", "Advisor"),
        is_active=True,
    )
    db.session.add(u)
    db.session.commit()
    flash(f"{u.full_name} added.", "success")
    return redirect(url_for("user_list"))


@app.route("/users/<int:id>/edit", methods=["POST"])
def user_edit(id):
    u = User.query.get_or_404(id)
    u.first_name = request.form["first_name"]
    u.last_name = request.form["last_name"]
    u.email = request.form.get("email", "")
    u.role = request.form.get("role", "Advisor")
    u.is_active = request.form.get("is_active") == "on"
    db.session.commit()
    flash(f"{u.full_name} updated.", "success")
    return redirect(url_for("user_list"))


@app.route("/users/<int:id>/delete", methods=["POST"])
def user_delete(id):
    u = User.query.get_or_404(id)
    db.session.delete(u)
    db.session.commit()
    flash("User removed.", "success")
    return redirect(url_for("user_list"))


# ── Tasks ──────────────────────────────────────────────────────────────────────

@app.route("/tasks")
def task_list():
    status_filter = request.args.get("status", "")
    query = Task.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    tasks = query.order_by(Task.due_date.asc().nullslast()).all()
    return render_template(
        "tasks.html",
        tasks=tasks,
        statuses=TASK_STATUSES,
        priorities=TASK_PRIORITIES,
        households=Household.query.order_by(Household.name).all(),
        users=User.query.filter_by(is_active=True).order_by(User.last_name).all(),
        current_status=status_filter,
    )


@app.route("/tasks/new", methods=["POST"])
def task_new():
    due = request.form.get("due_date")
    t = Task(
        title=request.form["title"],
        description=request.form.get("description", ""),
        status=request.form.get("status", "Open"),
        priority=request.form.get("priority", "Medium"),
        due_date=date.fromisoformat(due) if due else None,
        assigned_to=request.form.get("assigned_to", ""),
        household_id=int(request.form["household_id"]) if request.form.get("household_id") else None,
    )
    db.session.add(t)
    db.session.commit()
    flash(f"Task '{t.title}' created.", "success")
    referrer = request.form.get("referrer", "")
    if referrer == "household" and t.household_id:
        return redirect(url_for("household_detail", id=t.household_id))
    if referrer == "calendar":
        return redirect(url_for("calendar_view"))
    return redirect(url_for("task_list"))


@app.route("/tasks/<int:id>/edit", methods=["POST"])
def task_edit(id):
    t = Task.query.get_or_404(id)
    due = request.form.get("due_date")
    t.title = request.form["title"]
    t.description = request.form.get("description", "")
    t.status = request.form.get("status", "Open")
    t.priority = request.form.get("priority", "Medium")
    t.due_date = date.fromisoformat(due) if due else None
    t.assigned_to = request.form.get("assigned_to", "")
    t.household_id = int(request.form["household_id"]) if request.form.get("household_id") else None
    db.session.commit()
    flash(f"Task '{t.title}' updated.", "success")
    return redirect(url_for("task_list"))


@app.route("/tasks/<int:id>/status", methods=["POST"])
def task_status(id):
    t = Task.query.get_or_404(id)
    t.status = request.form["status"]
    db.session.commit()
    return redirect(request.referrer or url_for("task_list"))


@app.route("/tasks/<int:id>/delete", methods=["POST"])
def task_delete(id):
    t = Task.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    flash("Task deleted.", "success")
    return redirect(url_for("task_list"))


# ── Welcome Dashboard ────────────────────────────────────────────────────────

@app.route("/welcome")
def welcome():
    today = date.today()
    users = User.query.filter_by(is_active=True).order_by(User.last_name).all()
    meetings_today = Meeting.query.filter_by(meeting_date=today).order_by(Meeting.meeting_time).all()
    all_tasks = Task.query.filter(Task.status != "Done").order_by(Task.due_date.asc().nullslast()).all()
    return render_template(
        "welcome.html",
        users=users,
        meetings_today=meetings_today,
        all_tasks_json=[t.to_dict() for t in all_tasks],
        today=today,
        task_statuses=TASK_STATUSES,
        task_priorities=TASK_PRIORITIES,
        households=Household.query.order_by(Household.name).all(),
    )


# ── Calendar / Meetings ───────────────────────────────────────────────────────

@app.route("/calendar")
def calendar_view():
    meetings = Meeting.query.order_by(Meeting.meeting_date, Meeting.meeting_time).all()
    people = Person.query.order_by(Person.last_name).all()
    households = Household.query.order_by(Household.name).all()
    return render_template(
        "calendar.html",
        meetings=meetings,
        people=people,
        households=households,
        task_statuses=TASK_STATUSES,
        task_priorities=TASK_PRIORITIES,
        users=User.query.filter_by(is_active=True).order_by(User.last_name).all(),
    )


@app.route("/meetings/new", methods=["POST"])
def meeting_new():
    m = Meeting(
        title=request.form["title"],
        meeting_date=date.fromisoformat(request.form["meeting_date"]),
        meeting_time=time.fromisoformat(request.form["meeting_time"]),
        duration_minutes=int(request.form.get("duration_minutes", 60)),
        location=request.form.get("location", ""),
        notes=request.form.get("notes", ""),
        household_id=int(request.form["household_id"]) if request.form.get("household_id") else None,
    )
    db.session.add(m)
    db.session.commit()
    attendee_ids = request.form.getlist("attendee_ids")
    for pid in attendee_ids:
        db.session.add(MeetingAttendee(meeting_id=m.id, person_id=int(pid)))
    db.session.commit()
    flash(f"Meeting '{m.title}' scheduled.", "success")
    return redirect(url_for("calendar_view"))


@app.route("/meetings/<int:id>/edit", methods=["POST"])
def meeting_edit(id):
    m = Meeting.query.get_or_404(id)
    m.title = request.form["title"]
    m.meeting_date = date.fromisoformat(request.form["meeting_date"])
    m.meeting_time = time.fromisoformat(request.form["meeting_time"])
    m.duration_minutes = int(request.form.get("duration_minutes", 60))
    m.location = request.form.get("location", "")
    m.notes = request.form.get("notes", "")
    m.household_id = int(request.form["household_id"]) if request.form.get("household_id") else None
    MeetingAttendee.query.filter_by(meeting_id=m.id).delete()
    attendee_ids = request.form.getlist("attendee_ids")
    for pid in attendee_ids:
        db.session.add(MeetingAttendee(meeting_id=m.id, person_id=int(pid)))
    db.session.commit()
    flash(f"Meeting '{m.title}' updated.", "success")
    return redirect(url_for("calendar_view"))


@app.route("/meetings/<int:id>/delete", methods=["POST"])
def meeting_delete(id):
    m = Meeting.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    flash("Meeting deleted.", "success")
    return redirect(url_for("calendar_view"))


# ── API (JSON) for calendar widget ────────────────────────────────────────────

@app.route("/api/tasks")
def api_tasks():
    tasks = Task.query.filter(Task.due_date.isnot(None), Task.status != "Done").all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "due_date": t.due_date.isoformat(),
        "priority": t.priority,
        "status": t.status,
        "assigned_to": t.assigned_to or "",
        "household": t.household.name if t.household else "",
    } for t in tasks])


@app.route("/api/meetings")
def api_meetings():
    meetings = Meeting.query.all()
    events = []
    for m in meetings:
        attendee_names = ", ".join(a.person.full_name for a in m.attendees) if m.attendees else ""
        events.append({
            "id": m.id,
            "title": m.title,
            "start": f"{m.meeting_date.isoformat()}T{m.meeting_time.strftime('%H:%M')}",
            "duration": m.duration_minutes,
            "household": m.household.name if m.household else "",
            "location": m.location,
            "notes": m.notes,
            "attendees": attendee_names,
        })
    return jsonify(events)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
