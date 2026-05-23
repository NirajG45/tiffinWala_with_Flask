from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User.query.filter_by(email="nirajkumar9945111@gmail.com").first()
    if admin:
        admin.is_admin = True
        print(f"User {admin.username} promoted to admin")
    else:
        admin = User(
            username="Niraj Kumar",
            email="nirajkumar9945111@gmail.com",
            phone="9155658081",
            address="Jamui",
            password_hash=generate_password_hash("niraj@123"),
            is_admin=True
        )
        db.session.add(admin)
        print("New admin user created")
    db.session.commit()
    print("Done!")