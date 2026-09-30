CREATE DATABASE IF NOT EXISTS university_support;
USE university_support;

CREATE TABLE IF NOT EXISTS faculty (
 faculty_id VARCHAR(40) PRIMARY KEY,
 name VARCHAR(180) NOT NULL,
 designation VARCHAR(120),
 department VARCHAR(120),
 data_status ENUM('OFFICIAL_PUBLIC','DEMO_SYNTHETIC') NOT NULL,
 source VARCHAR(1000),
 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS faculty_seating (
 seating_id BIGINT AUTO_INCREMENT PRIMARY KEY,
 faculty_id VARCHAR(40) NOT NULL,
 block VARCHAR(120),
 floor VARCHAR(40),
 cabin VARCHAR(80),
 office_hours VARCHAR(120),
 appointment_required BOOLEAN,
 landmark VARCHAR(255),
 location_status ENUM('OFFICIAL','DEMO_SYNTHETIC') NOT NULL,
 source VARCHAR(1000),
 FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
);

CREATE TABLE IF NOT EXISTS knowledge_documents (
 document_id VARCHAR(120) PRIMARY KEY,
 title VARCHAR(255) NOT NULL,
 source_type ENUM('OFFICIAL_PUBLIC','OFFICIAL_PRIVATE','DEMO_SYNTHETIC') NOT NULL,
 source VARCHAR(1000),
 version VARCHAR(80),
 effective_date DATE,
 review_date DATE,
 status VARCHAR(60),
 access_level VARCHAR(80),
 tags JSON
);

CREATE INDEX idx_faculty_department ON faculty(department);
CREATE INDEX idx_seating_location ON faculty_seating(block,floor,cabin);
