-- ============================================================================
-- HEALTHCARE DATA ANALYSIS - DATABASE SETUP
-- ============================================================================
-- Purpose : Create the database structure required to hold the cleaned
--           healthcare dataset used throughout this project.
-- Engine  : Written in standard ANSI SQL, compatible with MySQL / PostgreSQL
--           / SQLite (minor syntax differences noted in comments).
-- ============================================================================

-- Create the database (MySQL / PostgreSQL syntax; omit/adjust for SQLite)
CREATE DATABASE IF NOT EXISTS healthcare_analysis;
USE healthcare_analysis;

-- ----------------------------------------------------------------------------
-- Table: patients
-- Stores one row per hospital admission record, matching the structure of
-- Data/cleaned_healthcare_data.csv produced by Notebook/healthcare_eda.py
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS patients;

CREATE TABLE patients (
    record_id            INT AUTO_INCREMENT PRIMARY KEY,   -- surrogate key (not in source data)
    name                  VARCHAR(255)   NOT NULL,
    age                   INT            NOT NULL,
    gender                VARCHAR(10)    NOT NULL,
    blood_type            VARCHAR(5)     NOT NULL,
    medical_condition     VARCHAR(50)    NOT NULL,
    date_of_admission     DATE           NOT NULL,
    doctor                VARCHAR(255)   NOT NULL,
    hospital              VARCHAR(255)   NOT NULL,
    insurance_provider    VARCHAR(50)    NOT NULL,
    billing_amount        DECIMAL(12, 2) NOT NULL,
    room_number           INT            NOT NULL,
    admission_type        VARCHAR(20)    NOT NULL,
    discharge_date        DATE           NOT NULL,
    medication             VARCHAR(50)    NOT NULL,
    test_results           VARCHAR(20)    NOT NULL,
    length_of_stay         INT            NOT NULL,          -- derived: discharge_date - date_of_admission
    admission_year          INT            NOT NULL,
    admission_month         INT            NOT NULL
);

-- Helpful indexes for the analytical queries in healthcare_analysis.sql
CREATE INDEX idx_patients_condition        ON patients (medical_condition);
CREATE INDEX idx_patients_admission_type   ON patients (admission_type);
CREATE INDEX idx_patients_hospital         ON patients (hospital);
CREATE INDEX idx_patients_insurance        ON patients (insurance_provider);
CREATE INDEX idx_patients_admission_date   ON patients (date_of_admission);

-- ----------------------------------------------------------------------------
-- Load data from the cleaned CSV file.
-- Adjust the file path and LOAD syntax to match your SQL engine:
--
-- MySQL example:
--   LOAD DATA LOCAL INFILE '../Data/cleaned_healthcare_data.csv'
--   INTO TABLE patients
--   FIELDS TERMINATED BY ','
--   OPTIONALLY ENCLOSED BY '"'
--   LINES TERMINATED BY '\n'
--   IGNORE 1 ROWS
--   (name, age, gender, blood_type, medical_condition, date_of_admission,
--    doctor, hospital, insurance_provider, billing_amount, room_number,
--    admission_type, discharge_date, medication, test_results, length_of_stay,
--    admission_year, admission_month);
--
-- PostgreSQL example:
--   COPY patients (name, age, gender, blood_type, medical_condition,
--                  date_of_admission, doctor, hospital, insurance_provider,
--                  billing_amount, room_number, admission_type, discharge_date,
--                  medication, test_results, length_of_stay, admission_year,
--                  admission_month)
--   FROM '../Data/cleaned_healthcare_data.csv'
--   DELIMITER ',' CSV HEADER;
--
-- SQLite example (from the sqlite3 CLI):
--   .mode csv
--   .import ../Data/cleaned_healthcare_data.csv patients_import
-- ----------------------------------------------------------------------------
