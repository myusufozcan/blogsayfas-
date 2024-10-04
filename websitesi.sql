-- Veritabanı oluşturma
CREATE DATABASE websitesi CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- Veritabanını kullan
USE websitesi;

-- Users tablosunu oluşturma
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    city VARCHAR(100)
);

-- Blogs tablosunu oluşturma
CREATE TABLE blogs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(100) NOT NULL,
    image VARCHAR(255),
    created_at VARCHAR(100)
);
