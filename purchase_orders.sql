USE lab_inventory_db;

-- Table for Purchase Orders
CREATE TABLE IF NOT EXISTS purchase_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    po_number VARCHAR(50) NOT NULL UNIQUE,  -- e.g., PO-2023-089
    supplier VARCHAR(100) NOT NULL,
    order_date DATE NOT NULL,
    items TEXT NOT NULL,                    -- JSON or comma-separated list of items
    total_cost DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status ENUM('Pending', 'Shipped', 'Received', 'Cancelled') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Optional: Insert some dummy data to match the UI mockups
INSERT INTO purchase_orders (po_number, supplier, order_date, items, total_cost, status) VALUES 
('PO-2023-089', 'Motewar Chemicals', '2023-11-15', 'Acetone (5L), Ethanol (2L)', 0.00, 'Received'),
('PO-2023-090', 'Bobade Acids', '2023-11-20', 'Sulfuric Acid (500ml)', 0.00, 'Shipped'),
('PO-2023-091', 'Renuka pharma', '2023-11-22', 'Glassware Set', 0.00, 'Pending');
