# Database Schema Proposal

## Core Tables

### device_make
- id: SERIAL PRIMARY KEY
- code: VARCHAR(20) NOT NULL UNIQUE  -- Manufacturer code (e.g., 'SAM' for Samsung)
- text: VARCHAR(100) NOT NULL        -- Manufacturer name (e.g., 'Samsung')

### device_model
- id: SERIAL PRIMARY KEY
- make_id: INTEGER REFERENCES device_make(id)
- code: VARCHAR(20) NOT NULL         -- Model code (e.g., 'A12')
- text: VARCHAR(100) NOT NULL        -- Model name (e.g., 'Galaxy A12')
- UNIQUE(make_id, code)              -- Ensures unique code per manufacturer

### phones
- id: SERIAL PRIMARY KEY
- make_id: INTEGER REFERENCES device_make(id)
- model_id: INTEGER REFERENCES device_model(id)
- serial_number: VARCHAR(100) UNIQUE NOT NULL
- buying_price: DECIMAL(10,2)
- status: VARCHAR(20) NOT NULL DEFAULT 'INSTOCK'  -- INSTOCK, ISSUED, TERMINATED
- note: TEXT
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

## Supporting Tables

### users
- id: SERIAL PRIMARY KEY
- employee_id: VARCHAR(20) UNIQUE NOT NULL
- first_name: VARCHAR(100) NOT NULL
- last_name: VARCHAR(100) NOT NULL
- email: VARCHAR(120)
- position: VARCHAR(100)
- state: VARCHAR(20) DEFAULT 'active'

### phone_assignments
- id: SERIAL PRIMARY KEY
- phone_id: INTEGER REFERENCES phones(id)
- user_id: INTEGER REFERENCES users(id)
- assigned_date: DATE NOT NULL
- returned_date: DATE
- note: TEXT
- protocol_number: VARCHAR(50)
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

## Key Features:
1. Make-Model relationship enforced through foreign keys
2. Unique constraints on manufacturer codes and model codes within manufacturers
3. Complete device history tracking through assignments
4. Support for handover protocols with protocol numbers
5. State tracking for both devices and users

Please validate this structure before we proceed with creation.
