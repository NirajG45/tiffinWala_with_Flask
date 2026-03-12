# 🍱 TiffinWala – Homemade Food Social Platform

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?logo=flask)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green)

## 📌 About The Project

**TiffinWala** is a Flask-based web application designed to connect people who provide homemade food (tiffin services) with users who want to discover and interact with those services.

This platform works like a **social network for food**, where users can share their homemade meals, upload images, explore food posts, and interact with other users.

---

## 🚀 Features

### 👤 User System
- User Registration
- Login and Logout
- Secure Password Hashing
- User Profile Page

### 🍲 Food Posting
- Upload Homemade Food Posts
- Add Description to Meals
- Upload Food Images

### ❤️ Social Interaction
- Like Food Posts
- Comment on Posts
- Explore Food Feed

### 🔐 Security
- Password Hashing using Werkzeug
- Session Management with Flask-Login

---

## 🛠 Tech Stack

| Technology | Purpose |
|------------|--------|
| Python | Backend Programming |
| Flask | Web Framework |
| SQLite | Database |
| SQLAlchemy | ORM |
| HTML | Structure |
| CSS | Styling |
| JavaScript | Client Interaction |

---

## 📂 Project Structure
tiffin_flask/
│
├── app.py
├── database.db
├── requirements.txt
│
├── templates/
│ ├── base.html
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ ├── profile.html
│ └── post.html
│
├── static/
│ ├── css/
│ │ └── style.css
│ ├── js/
│ └── uploads/
│
└── README.md


---

## ⚙️ Installation Guide

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/tiffinwala.git
cd tiffinwala
2️⃣ Create Virtual Environment
python -m venv .venv

Activate the virtual environment

Windows

.venv\Scripts\activate

Linux / Mac

source .venv/bin/activate
3️⃣ Install Dependencies
pip install flask flask_sqlalchemy flask_login werkzeug

OR

pip install -r requirements.txt
4️⃣ Run the Application
python app.py

Open browser and visit:

http://127.0.0.1:5000
🗄 Database

The project uses SQLite Database.

The database file will be automatically created when the application runs for the first time.

database.db
📸 Screenshots

You can add screenshots of the application here.

screenshots/
│
├── homepage.png
├── profile.png
└── post.png
🧭 Future Improvements

Online food ordering system

Payment gateway integration

Chat system between users

Rating and review system

Mobile responsive improvements

Cloud deployment

🤝 Contributing

Contributions are welcome.

Steps to contribute:

Fork the repository

Create a new branch

Commit your changes

Push the branch

Open a Pull Request

📜 License

This project is licensed under the MIT License.

👨‍💻 Author

Subh

BCA Student | Python Developer | Machine Learning Enthusiast

GitHub: https://github.com/yourusername


Agar chaho to main **aur bhi advanced README.md bana sakta hoon** jisme:

- ⭐ project preview images  
- 📊 GitHub stats  
- 🎥 demo section  
- 🚀 deployment guide (Render / Railway / AWS)

jo **GitHub par project ko aur professional bana deta hai**.
