# 🏏 CricketDB: Cricket Database Management System

A full-stack database project to manage cricket teams, players, matches, tournaments, and performance analytics with a modern Streamlit GUI and robust MySQL backend.

---

## 🚀 Features

- **User Management:** Admin/User roles with login, hashed passwords, and role-based access  
- **CRUD Operations:** Create, read (filter/sort), update, delete on all tables via GUI  
- **Advanced Queries:** Nested, join, and aggregate queries, all with user interface  
- **Triggers, Procedures, Functions:** Demonstrated via interactive components  
- **Dashboard:** Team/player statistics, recent matches  
- **Security:** SHA256 password hashing, parameterized queries, session handling  
- **Error Handling:** Friendly feedback for all failed operations  
- **Documentation:** Complete setup and code explanations

---

## 📦 Project Structure

├── cricket_db_app_final.py # Streamlit frontend app (GUI)
├── cricket_db_complete.sql # MySQL DDL + DML setup (fixed, ready to load)
├── requirements.txt # Python dependencies
├── README.md # Project documentation (you are here)
└── .streamlit/
└── secrets.toml # Streamlit MySQL config (user-provided)

---

## ⚡ Quick Start

1. **Install Dependencies**
pip install streamlit mysql-connector-python pandas

2. **Setup Database**
mysql -u root -p < cricket_db_complete.sql

3. **Configure Streamlit Secrets**

Create `.streamlit/secrets.toml` in your project root (edit credentials as needed):
[mysql]
host = "localhost"
port = 3306
database = "CricketDB"
user = "root"
password = "your_password"

4. **Run the Application**
streamlit run cricket_db_app_final.py

5. **Login Credentials**

- **Admin:** `admin` / `admin123`
- **User:**  `user`  / `user123`

---

## 📊 Usage

- **Dashboard**: View player/team/match/tournament stats, latest matches.
- **CRUD**: Create new players (admin), read (with filters/sort), update, and delete.
- **Queries**: Explore advanced queries (Nested, Join, Aggregate) from the UI.
- **Database Objects**:
    - Procedures, Functions called & displayed via GUI
    - Triggers automatically managed in the DB
- **Role-based Access**: Admin = all features; User = read-only.

---

## 🛡️ Security & Best Practices

- Passwords are stored securely using SHA256 hashing.
- All database queries use parameterized queries to prevent SQL injection.
- Role-based privileges for sensitive operations.
- Full error handling with user feedback.

---

## 👏 Credits

Developed by:
SUHITH REDDY C PES2UG23CS617

THILAK URS V   PES2UG23CS654

SRAJAN SHETTY  PES2UG23CS596

PES University - Database Project (2025)

---


## 💡 Notes

- Sample data covers 4 international teams, 68 players, matches, awards, and trainers.
- Tested on MySQL 8.0+, Python 3.8+, Streamlit 1.x+.

---

**Happy coding!** 🏏




