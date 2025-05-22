# 🏠 Real Estate Web Application
This is a full-stack real estate web application built using Flask, MySQL, and Socket.IO that enables users to buy, sell, and rent properties. It features a user-friendly dashboard for buyers and sellers, live chat functionality, property listings, and secure user authentication.

🚀 Features
🧑‍💼 User Authentication: Register and log in as a Buyer or Seller

🏘 Property Management: Add, view, and manage property listings

💰 Transaction Processing: Simulate buying and renting of properties

💬 Real-Time Chat: Chat system for buyers and sellers (WhatsApp-style)

🔍 Search & Filter: Filter listings by availability status

📷 Image Upload Support (optional in deployment)

🗂 Project Structure

real-estate-app/

├── app.py                 # Main Flask application

├── templates/             # HTML templates

├── static/                # Static assets (CSS, js, uploads)

├── real_estate_schema.sql             # Database schema

├──requirements.txt

🧑‍💻 Tech Stack

Backend: Flask (Python), Flask-SocketIO

Database: MySQL

Frontend: HTML, CSS (Jinja templates)

Libraries: mysql-connector-python, werkzeug, flask-socketio

🛠 Database Schema

Run the following SQL commands to create the required schema.

🧪 Setup Instructions

1. Clone the Repository

git clone https://github.com/your-username/real-estate-app.git

cd real-estate-app

2. Install Dependencies

pip install -r requirements.txt

3. Configure MySQL

Ensure your MySQL server is running. Update credentials in app.py:

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="real_estate",
    port=3306
)

Then run the schema script manually via MySQL client or a GUI like phpMyAdmin.

4. Run the Application

python app.py

Then visit http://localhost:5000 in your browser.

💡 How It Works

🔑 Authentication

Users can register as a buyer or seller.

Secure password hashing using werkzeug.security.

🏠 Buyer Dashboard

View all available properties (For Sale, For Rent)

Confirm purchase or rental with transaction record insertion

🧾 Seller Dashboard

Add new property listings with details

View properties uploaded by the seller

💬 Real-Time Chat

Socket.IO powered messaging between buyers and sellers

Property-specific chat rooms with timestamped messages

📌 TODO / Improvements

Add admin panel for moderation

Integrate Google Maps for property location

Add pagination and search for listings

Include user reviews and ratings for sellers

🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

🛡 Security Notice

Use environment variables or a .env file to secure secrets like secret_key and database credentials before deploying.

Change default credentials and key before production.
