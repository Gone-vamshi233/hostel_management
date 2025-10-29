from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from models import db, User, Room, Allocation, Complaint
from forms import LoginForm, SignupForm, RoomForm, ComplaintForm, AllocateForm
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------- DASHBOARD -----------------
@app.route("/")
@login_required
def index():
    if current_user.role == "admin":
        rooms = Room.query.all()
        students = User.query.filter_by(role="student").all()
        return render_template("dashboard.html", rooms=rooms, students=students)
    elif current_user.role == "warden":
        rooms = Room.query.all()
        complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
        return render_template("dashboard.html", rooms=rooms, complaints=complaints)
    else:
        allocation = current_user.allocation
        return render_template("dashboard.html", allocation=allocation)

# ----------------- AUTH -----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(request.args.get("next") or url_for("index"))
        flash("Invalid credentials.", "danger")
    return render_template("login_page.html", form=form)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = SignupForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(email=form.email.data.lower(), name=form.name.data, password_hash=hashed, role=form.role.data)
        db.session.add(user)
        try:
            db.session.commit()
            flash("Signup successful. Please login.", "success")
            return redirect(url_for("login"))
        except IntegrityError:
            db.session.rollback()
            flash("Email already registered.", "danger")
    return render_template("signup_page.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

# ----------------- ROOMS -----------------
@app.route("/rooms", methods=["GET", "POST"])
@login_required
def rooms():
    if current_user.role not in ["admin", "warden"]:
        flash("Access denied.", "danger")
        return redirect(url_for("index"))
    form = RoomForm()
    if form.validate_on_submit():
        room = Room(room_no=form.room_no.data.upper(), capacity=form.capacity.data, block=form.block.data)
        db.session.add(room)
        try:
            db.session.commit()
            flash("Room added.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Room number already exists.", "danger")
        return redirect(url_for("rooms"))
    rooms = Room.query.order_by(Room.room_no).all()
    return render_template("rooms_page.html", rooms=rooms, form=form)

@app.route("/rooms/delete/<int:room_id>", methods=["POST"])
@login_required
def delete_room(room_id):
    if current_user.role not in ["admin", "warden"]:
        flash("Access denied.", "danger")
        return redirect(url_for("index"))
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    flash("Room deleted.", "info")
    return redirect(url_for("rooms"))

@app.route("/availability")
@login_required
def check_availability():
    rooms = Room.query.order_by(Room.room_no).all()
    return render_template("availability_page.html", rooms=rooms)

# ----------------- ALLOCATION -----------------
@app.route("/allocate", methods=["GET", "POST"])
@login_required
def allocate_room():
    if current_user.role not in ["admin", "warden"]:
        flash("Access denied.", "danger")
        return redirect(url_for("index"))
    form = AllocateForm()
    if form.validate_on_submit():
        student = User.query.filter_by(email=form.student_email.data.lower(), role="student").first()
        room = Room.query.filter_by(room_no=form.room_no.data.upper()).first()
        if not student:
            flash("Student not found.", "danger")
            return redirect(url_for("allocate_room"))
        if not room:
            flash("Room not found.", "danger")
            return redirect(url_for("allocate_room"))
        if room.occupants >= room.capacity:
            flash("Room is full.", "danger")
            return redirect(url_for("allocate_room"))
        if student.allocation and student.allocation.active:
            flash("Student already allocated. Deallocate first.", "warning")
            return redirect(url_for("allocate_room"))
        allocation = Allocation(student_id=student.id, room_id=room.id, active=True)
        room.occupants += 1
        db.session.add(allocation)
        db.session.commit()
        flash(f"Allocated {student.email} to {room.room_no}.", "success")
        return redirect(url_for("rooms"))
    return render_template("allocate_page.html", form=form)

@app.route("/deallocate/<int:alloc_id>", methods=["POST"])
@login_required
def deallocate(alloc_id):
    if current_user.role not in ["admin", "warden"]:
        flash("Access denied.", "danger")
        return redirect(url_for("index"))
    allocation = Allocation.query.get_or_404(alloc_id)
    if allocation.active:
        allocation.active = False
        allocation.room.occupants = max(0, allocation.room.occupants - 1)
        db.session.commit()
        flash("Student deallocated.", "info")
    return redirect(url_for("rooms"))

# ----------------- STUDENTS -----------------
@app.route("/students")
@login_required
def students():
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("index"))
    all_students = User.query.filter_by(role="student").all()
    return render_template("students_page.html", students=all_students)

# ----------------- COMPLAINTS -----------------
@app.route("/complaints", methods=["GET", "POST"])
@login_required
def complaints():
    form = ComplaintForm()
    if form.validate_on_submit():
        c = Complaint(user_id=current_user.id, subject=form.subject.data, message=form.message.data)
        db.session.add(c)
        db.session.commit()
        flash("Complaint submitted.", "success")
        return redirect(url_for("complaints"))

    if current_user.role in ["admin", "warden"]:
        complaints_list = Complaint.query.order_by(Complaint.created_at.desc()).all()
    else:
        complaints_list = Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.created_at.desc()).all()

    return render_template("complaints_page.html", form=form, complaints=complaints_list)

@app.route("/complaints/toggle/<int:c_id>", methods=["POST"])
@login_required
def toggle_complaint(c_id):
    if current_user.role not in ["admin", "warden"]:
        flash("Access denied.", "danger")
        return redirect(url_for("complaints"))
    c = Complaint.query.get_or_404(c_id)
    c.status = "resolved" if c.status == "open" else "open"
    db.session.commit()
    flash("Complaint status updated.", "info")
    return redirect(url_for("complaints"))

# ----------------- RUN APP -----------------
if __name__ == "__main__":
    app.run(debug=True)
