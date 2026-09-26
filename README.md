# 💰 Personal Finance Tracker

A web-based Personal Finance Tracker built with **Python Flask** and **SQLite** to help users manage their income, expenses, budgets, financial goals, and transactions from a single dashboard.

## 📌 Project Overview

Personal Finance Tracker is designed to make personal money management simple and organized.

Users can record their income and expenses, manage transactions, create budgets, set financial goals, and view financial reports through an easy-to-use web interface.

---

## ✨ Features

- 🏠 **Dashboard**
  - Overview of financial activity
  - Total income
  - Total expenses
  - Current balance

- 💳 **Transaction Management**
  - Add income
  - Add expenses
  - Edit transactions
  - Delete transactions
  - View transaction history
  - Category management
  - Payment method tracking

- 📊 **Budget Management**
  - Create budgets
  - Track budget usage
  - Monitor spending limits

- 🎯 **Financial Goals**
  - Create financial goals
  - Set target amounts
  - Track goal progress
  - Monitor target dates

- 📈 **Reports**
  - View financial reports
  - Analyze income and expenses
  - Filter financial information

- ⚙️ **Settings**
  - Manage profile information
  - Application preferences

- 🔐 **Authentication**
  - User registration
  - User login
  - Password reset functionality
  - Protected user pages

---

## 🛠️ Technologies Used

### Frontend

- HTML5
- CSS3
- Bootstrap
- JavaScript

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login

### Database

- SQLite

### Development Tools

- Visual Studio Code
- Git
- GitHub

---

## 📂 Project Structure

```text
Personal-Finance-Tracker/
│
├── models/
│   ├── transaction.py
│   └── user.py
│
├── routes/
│   ├── auth.py
│   ├── budgets.py
│   ├── dashboard.py
│   ├── goals.py
│   ├── reports.py
│   ├── settings.py
│   └── transactions.py
│
├── static/
│   ├── css/
│   │   ├── dark-mode.css
│   │   └── style.css
│
├── templates/
│   ├── auth/
│   ├── budgets/
│   ├── dashboard/
│   ├── goals/
│   ├── reports/
│   ├── settings/
│   ├── transactions/
│   └── home.html
│
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
├── .gitignore
└── README.md
