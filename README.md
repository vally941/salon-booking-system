# Vally's Divine Hair – Salon Booking System

A full-stack salon booking web application built with Flask, SQLAlchemy, and MySQL.

The system allows customers to book appointments online while administrators manage bookings, customers, messages, and portfolio items through a secure dashboard.

---

## 📌 Project Overview

This application demonstrates:

- Full-stack web development using Flask
- Relational database integration with MySQL
- Backend logic implementation with SQLAlchemy ORM
- User authentication and session management
- Role-based admin access control
- Secure password hashing
- CRUD operations across multiple models

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

The system connects to a MySQL database using:

mysql+pymysql://root:@localhost/hair_salon_db

The application uses:

- SQLAlchemy ORM
- Foreign key relationships
- Structured relational tables

### Database Tables

- Users
- Appointments
- Contact Messages
- Completed Jobs (Portfolio)

---

## 👤 Database Models

### User
- Secure authentication system
- Password hashing using Werkzeug
- Role-based access control (`is_admin` column)
- Admin badge logic

### Appointment
- Linked to users via foreign key
- Stores booking details and appointment status

### ContactMessage
- Stores customer inquiries
- Admin can mark messages as read

### CompletedJob
- Portfolio management system
- Featured items support
- Image storage via URL
- Automatic timestamp updates

---

## ✨ Key Features

### Customer Features
- User registration and login
- Secure password hashing
- Online appointment booking
- View personal appointments
- Contact form submission

### Admin Features
- Secure admin dashboard
- Appointment management
- Customer management
- Message monitoring
- Portfolio management
- Role-based route protection

---

## 🔐 Security Implementation

- Password hashing (Werkzeug)
- Flask-Login session management
- Role-based admin route protection
- Secure database relationships
- Environment variable support via python-dotenv

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

---

## 🌐 Running the Application

After starting the Flask development server:

python app.py

You should see output similar to:

Running on http://127.0.0.1:5000

Open your browser and navigate to:

http://127.0.0.1:5000

Note:
This is a local development server. The URL will only work after running the application on your own machine.

---

## 📄 Available Routes (After Running the App)

Public Pages:
- Home → /
- Services → /services
- Portfolio → /portfolio
- About → /about

Protected Pages (Login Required):
- Book Appointment → /book
- Dashboard → /dashboard

---

## 🔄 Database Reset Script

The project includes a database reset script that:

- Drops all existing tables
- Recreates all tables with the `is_admin` column
- Creates one default admin account

### Default Admin Login

Email: admin@vallys.com  
Password: Admin123  

(New registrations are not admins.)

---

## 📚 Purpose

This project demonstrates practical experience in:

- Designing relational database models
- Implementing authentication systems
- Creating secure admin role logic
- Managing CRUD operations
- Building a complete database-driven web application

---

## 👩🏽‍💻 Author

Alice Valencia Maseko  
IT Graduate | Software & Systems
