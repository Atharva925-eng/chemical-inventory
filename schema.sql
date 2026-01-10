CREATE DATABASE IF NOT EXISTS lab_inventory_db;
USE lab_inventory_db;

-- Table for storage locations (e.g., Cabinet A, Fridge 1)
CREATE TABLE IF NOT EXISTS locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    room_number VARCHAR(20),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for the chemicals
CREATE TABLE IF NOT EXISTS chemicals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cas_number VARCHAR(50) NOT NULL, -- Unique identifier for chemicals
    name VARCHAR(200) NOT NULL,
    formula VARCHAR(100),
    
    -- Inventory details
    quantity DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    unit VARCHAR(10) NOT NULL, -- e.g., 'g', 'ml', 'L', 'kg'
    
    -- Foreign Key to Location
    location_id INT,
    
    -- Safety & Meta
    expiry_date DATE,
    safety_notes TEXT, -- GHS codes or hazard info
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

INSERT INTO locations (name, room_number) VALUES 
('Flammables Cabinet', '101'),
('Refrigerator A', '102'),
('General Shelf 3', '101'),
('Chemical Storage Room', 'Basement');

-- Table for the equipment
CREATE TABLE IF NOT EXISTS equipments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    model_number VARCHAR(100),
    serial_number VARCHAR(100),
    manufacturer VARCHAR(100),
    quantity INT NOT NULL DEFAULT 1,
    location_id INT,
    purchase_date DATE,
    last_maintenance_date DATE,
    next_maintenance_date DATE,
    status ENUM('Working', 'Maintenance', 'Broken', 'Retired') DEFAULT 'Working',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

-- Table for resource bookings (Lab Rooms & Instruments)
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('Lab', 'Instrument') NOT NULL,
    resource_name VARCHAR(200) NOT NULL,
    researcher_name VARCHAR(200) NOT NULL,
    booking_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Table for users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('admin', 'staff') DEFAULT 'staff',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
