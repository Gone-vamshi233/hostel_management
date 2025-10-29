from app import app
from models import db, User, Room
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()
    # create default admin if not exists
    admin_email = "gonevamshi201@gmail.com"
    if not User.query.filter_by(email=admin_email).first():
        hashed = bcrypt.generate_password_hash("adminpass").decode("utf-8")
        admin = User(email=admin_email, name="Admin", password_hash=hashed, role="admin")
        db.session.add(admin)
    # sample rooms
    if not Room.query.first():
        r1 = Room(room_no="A101", capacity=2, block="A")
        r2 = Room(room_no="A102", capacity=1, block="A")
        db.session.add_all([r1, r2])
    db.session.commit()
    print("DB initialized.")
