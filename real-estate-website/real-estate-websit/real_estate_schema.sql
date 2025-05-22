CREATE DATABASE IF NOT EXISTS real_estate;
USE real_estate;

CREATE TABLE User (
    User_id INT AUTO_INCREMENT PRIMARY KEY,
    First_name VARCHAR(50),
    Last_name VARCHAR(50),
    Email VARCHAR(100) UNIQUE,
    Password VARCHAR(255)  -- Added this line for storing hashed passwords
);

CREATE TABLE User_contact_info (
    User_id INT,
    Contact_info VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES User(User_id),
    PRIMARY KEY(User_id, Contact_info)
);

CREATE TABLE Seller (
    User_id INT PRIMARY KEY,
    Acc_Status VARCHAR(20),
    Avg_prop_rating DECIMAL(3, 2),
    FOREIGN KEY (User_id) REFERENCES User(User_id)
);

CREATE TABLE Renter (
    User_id INT PRIMARY KEY,
    rent_duration VARCHAR(50),
    rent_budget_range VARCHAR(50),
    Preference VARCHAR(100),
    FOREIGN KEY (User_id) REFERENCES User(User_id)
);

CREATE TABLE Buyer (
    User_id INT PRIMARY KEY,
    Budget DECIMAL(15, 2),
    FOREIGN KEY (User_id) REFERENCES User(User_id)
);

CREATE TABLE Property (
    Prop_id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(20),
    size DECIMAL(10, 2),
    price DECIMAL(15, 2),
    location VARCHAR(255),
    amenities VARCHAR(50),
    status VARCHAR(20)
);

CREATE TABLE Registration (
    Reg_num INT AUTO_INCREMENT PRIMARY KEY,
    User_id INT,
    Reg_name VARCHAR(100),
    Reg_tax DECIMAL(10, 2),
    Reg_type VARCHAR(50),
    FOREIGN KEY (User_id) REFERENCES User(User_id)
);

CREATE TABLE Transactions (
    trans_id INT,
    Prop_id INT,
    User_id INT,
    Sale_Price DECIMAL(15, 2),
    mode VARCHAR(50),
    FOREIGN KEY (Prop_id) REFERENCES Property(Prop_id),
    FOREIGN KEY (User_id) REFERENCES User(User_id),
    PRIMARY KEY(trans_id, Prop_id)
);

CREATE TABLE manage (
    user_id INT,
    registration_id INT,
    transaction_id INT,
    property_id INT,
    FOREIGN KEY (user_id) REFERENCES User(User_id),
    FOREIGN KEY (registration_id) REFERENCES Registration(Reg_num),
    FOREIGN KEY (transaction_id) REFERENCES Transactions(trans_id),
    FOREIGN KEY (property_id) REFERENCES Property(Prop_id),
    PRIMARY KEY(user_id, registration_id, transaction_id, property_id)
);

