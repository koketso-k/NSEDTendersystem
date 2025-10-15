-- Create database
CREATE DATABASE IF NOT EXISTS tender_hub;
USE tender_hub;


USE tender_hub;

-- Check what tables actually exist
SHOW TABLES;

-- Check the current state of key tables
SELECT * FROM teams;
SELECT * FROM users; 
SELECT * FROM tenders;
SELECT * FROM workspace_tenders;

-- Check the AUTO_INCREMENT values for each table
SELECT TABLE_NAME, AUTO_INCREMENT 
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'tender_hub';

-- Show the structure of workspace_tenders to see the foreign key
SHOW CREATE TABLE workspace_tenders;



-- In MySQL Workbench
DROP DATABASE IF EXISTS tender_hub;
CREATE DATABASE tender_hub;
USE tender_hub;

DROP TABLE IF EXISTS ` workspace_tenders`;

-- Create the table with correct name (no space)
CREATE TABLE `workspace_tenders` (
    `id` int NOT NULL AUTO_INCREMENT,
    `team_id` int NOT NULL,
    `tender_id` int NOT NULL,
    `status` varchar(50) NOT NULL,
    `match_score` float DEFAULT NULL,
    `last_updated_by` int NOT NULL,
    `last_updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `notes` text,
    PRIMARY KEY (`id`),
    KEY `team_id` (`team_id`),
    KEY `tender_id` (`tender_id`),
    KEY `last_updated_by` (`last_updated_by`),
    CONSTRAINT `workspace_tenders_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`),
    CONSTRAINT `workspace_tenders_ibfk_2` FOREIGN KEY (`tender_id`) REFERENCES `tenders` (`id`),
    CONSTRAINT `workspace_tenders_ibfk_3` FOREIGN KEY (`last_updated_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;




-- teams table
CREATE TABLE teams (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- users table  
CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    team_id INT NOT NULL,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- company_profiles table
CREATE TABLE company_profiles (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    registration_number VARCHAR(100),
    cidb_grade VARCHAR(20),
    turnover_bracket VARCHAR(50),
    team_id INT NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- tenders table
CREATE TABLE tenders (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    issuing_authority VARCHAR(255),
    category VARCHAR(100),
    estimated_value DECIMAL(15,2),
    submission_deadline DATETIME,
    site_meeting_date DATETIME,
    cidb_requirement VARCHAR(20),
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- workspace_tenders table (CORRECT NAME - no space)
CREATE TABLE workspace_tenders (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    tender_id INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    match_score FLOAT,
    last_updated_by INT NOT NULL,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (tender_id) REFERENCES tenders(id),
    FOREIGN KEY (last_updated_by) REFERENCES users(id)
);

USE tender_hub;
SHOW TABLES;

-- Should show tables without spaces:
-- teams, users, company_profiles, tenders, workspace_tenders

DESCRIBE workspace_tenders;
-- Should show proper structure without space in table name
USE tender_hub;

-- Drop the incorrectly named table (with space)
DROP TABLE IF EXISTS ` workspace_tenders`;

-- Let SQLAlchemy recreate it with the correct name
-- Your database.py will automatically create it when you run the app



DROP DATABASE IF EXISTS tender_hub;
CREATE DATABASE tender_hub;
USE tender_hub;



-- Create a new user (safer than using root)
CREATE USER 'tender_user'@'localhost' IDENTIFIED BY 'tenderpass123';

-- Grant privileges to the new user
GRANT ALL PRIVILEGES ON tender_hub.* TO 'tender_user'@'localhost';

-- Apply the changes
FLUSH PRIVILEGES;

SHOW TABLES;


-- Check if tender_user exists and has privileges
SELECT user, host FROM mysql.user WHERE user = 'tender_user';

-- Check database exists
SHOW DATABASES LIKE 'tender_hub';

-- Test connection with the user
USE tender_hub;
SELECT 'Connection successful' as status;

-- In MySQL Workbench
DROP DATABASE tender_hub;
CREATE DATABASE tender_hub;
USE tender_hub;

SHOW TABLES;
SELECT * FROM teams LIMIT 3;
SELECT * FROM users LIMIT 3; 
SELECT * FROM tenders LIMIT 5;