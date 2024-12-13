-- Device Manufacturer table
CREATE TABLE device_make (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,  -- Manufacturer code
    text VARCHAR(100) NOT NULL         -- Manufacturer name/text
);

-- Device Model table
CREATE TABLE device_model (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL,         -- Model code
    text VARCHAR(100) NOT NULL,        -- Model name/text
    make_id INTEGER NOT NULL REFERENCES device_make(id),
    UNIQUE(make_id, code)              -- Ensure unique code per manufacturer
);

-- Phone table (main device table)
CREATE TABLE phones (
    id SERIAL PRIMARY KEY,
    make_id INTEGER NOT NULL REFERENCES device_make(id),
    model_id INTEGER NOT NULL REFERENCES device_model(id),
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    buying_price DECIMAL(10,2),
    status VARCHAR(20) NOT NULL DEFAULT 'INSTOCK',  -- INSTOCK, ISSUED, TERMINATED
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table (for device assignment)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(120),
    position VARCHAR(100),
    state VARCHAR(20) DEFAULT 'active'
);

-- Phone Assignment table (for tracking device history)
CREATE TABLE phone_assignments (
    id SERIAL PRIMARY KEY,
    phone_id INTEGER NOT NULL REFERENCES phones(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    assigned_date DATE NOT NULL,
    returned_date DATE,
    note TEXT,
    protocol_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data for device manufacturers
INSERT INTO device_make (code, text) VALUES
    ('SAM', 'Samsung'),
    ('APP', 'Apple'),
    ('HUA', 'Huawei'),
    ('XIA', 'Xiaomi');

-- Sample data for device models
INSERT INTO device_model (make_id, code, text) VALUES
    (1, 'A12', 'Galaxy A12'),
    (1, 'S21', 'Galaxy S21'),
    (2, 'IP13', 'iPhone 13'),
    (2, 'IP14', 'iPhone 14');
