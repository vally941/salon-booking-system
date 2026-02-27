# Vally's Divine Hair – Salon Booking System

A full-stack salon booking web application built with Flask, SQLAlchemy, and MySQL.

The system allows customers to book appointments online while administrators manage services, bookings, messages, and portfolio items through a secure dashboard.

---

## 📌 Project Overview

This application demonstrates:

- Full-stack web development with Flask
- Database modeling using SQLAlchemy ORM
- MySQL integration using PyMySQL
- User authentication and session management
- Role-based admin access control
- Secure password hashing
- Environment-based configuration

---

## 🛠️ Technologies Used

- Python 3
- Flask 3.1.2
- Flask-SQLAlchemy 3.1.1
- Flask-Login
- PyMySQL 1.1.0
- MySQL (XAMPP)
- Werkzeug (Password Hashing)
- Cryptography 41.0.7
- Python-dotenv 1.0.0
- HTML5
- CSS3
- JavaScript

---

## 🗄️ Database Configuration

The system connects to a MySQL database:

mysql+pymysql://root:@localhost/hair_salon_db

The application uses:

- SQLAlchemy ORM
- Relational database design
- Foreign key relationships
- Structured tables for:
  - Users
  - Appointments
  - Contact Messages
  - Completed Jobs (Portfolio)

---

## 👤 Database Models

### User
- Authentication system
- Password hashing using Werkzeug
- Role-based access (`is_admin` column)

### Appointment
- Linked to users via foreign key
- Stores booking details and status tracking

### ContactMessage
- Stores customer inquiries
- Admin can mark messages as read

### CompletedJob
- Portfolio management
- Featured items support
- Image storage via URL

---

## ✨ Key Features

### Customer Features
- User registration and login
- Secure password hashing
- Online appointment booking
- View personal appointments
- Contact form submission

### Admin Features
- Admin dashboard
- Service & booking management
- Customer management
- Appointment status tracking
- Portfolio management
- Message monitoring

---

## 🔐 Security Implementation

- Password hashing (Werkzeug)
- Flask-Login session management
- Role-based admin protection
- Environment variable support via python-dotenv
- Secure database structure with foreign keys

---

## 🚀 Installation Guide

1️⃣ Clone the repository:

git clone https://github.com/vally941/salon-booking-system.git  
cd salon-booking-system  

2️⃣ Install dependencies:

pip install -r requirements.txt  

3️⃣ Ensure MySQL (XAMPP) is running  

4️⃣ Create the database in MySQL:

hair_salon_db  

5️⃣ Run the application:

python app.py  

6️⃣ Open in your browser:

http://127.0.0.1:5000  

---

## 🔄 Database Reset Script

This project includes a database reset script that:

- Drops all existing tables
- Recreates tables with the `is_admin` column
- Creates one default admin account

Default Admin Login:

Email: admin@vallys.com  
Password: Admin123  

---

## 📚 Purpose

This project demonstrates practical experience in:

- Building a database-driven web application
- Designing relational database models
- Implementing authentication systems
- Creating secure admin role logic
- Managing full CRUD operations

---

## 👩🏽‍💻 Author

Alice Valencia Maseko  
IT Graduate 
