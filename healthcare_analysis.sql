-- ============================================================================
-- HEALTHCARE DATA ANALYSIS - SQL ANALYSIS QUERIES
-- ============================================================================
-- Table used: patients  (see healthcare_database.sql for the schema)
-- Column names below match the cleaned dataset exactly (in snake_case, as
-- created in the patients table).
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1. BASIC EXPLORATION
-- ----------------------------------------------------------------------------

-- 1.1 Total number of patient records
SELECT COUNT(*) AS total_records
FROM patients;

-- 1.2 Distinct medical conditions in the dataset
SELECT DISTINCT medical_condition
FROM patients
ORDER BY medical_condition;

-- 1.3 Preview the first 20 records, most recent admissions first
SELECT name, age, gender, medical_condition, date_of_admission, billing_amount
FROM patients
ORDER BY date_of_admission DESC
LIMIT 20;


-- ----------------------------------------------------------------------------
-- 2. PATIENT DEMOGRAPHICS
-- ----------------------------------------------------------------------------

-- 2.1 Patient count and average age by gender
SELECT
    gender,
    COUNT(*)        AS patient_count,
    ROUND(AVG(age), 1) AS avg_age
FROM patients
GROUP BY gender
ORDER BY patient_count DESC;

-- 2.2 Patient count by age group (CASE statement)
SELECT
    CASE
        WHEN age <= 18 THEN '0-18'
        WHEN age BETWEEN 19 AND 30 THEN '19-30'
        WHEN age BETWEEN 31 AND 45 THEN '31-45'
        WHEN age BETWEEN 46 AND 60 THEN '46-60'
        WHEN age BETWEEN 61 AND 75 THEN '61-75'
        ELSE '76+'
    END AS age_group,
    COUNT(*) AS patient_count
FROM patients
GROUP BY age_group
ORDER BY age_group;

-- 2.3 Blood type distribution
SELECT
    blood_type,
    COUNT(*) AS patient_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM patients), 2) AS pct_of_total
FROM patients
GROUP BY blood_type
ORDER BY patient_count DESC;


-- ----------------------------------------------------------------------------
-- 3. MEDICAL CONDITION ANALYSIS
-- ----------------------------------------------------------------------------

-- 3.1 Number of patients and average billing per medical condition
SELECT
    medical_condition,
    COUNT(*)                       AS patient_count,
    ROUND(AVG(billing_amount), 2)  AS avg_billing_amount,
    ROUND(AVG(length_of_stay), 1)  AS avg_length_of_stay
FROM patients
GROUP BY medical_condition
ORDER BY patient_count DESC;

-- 3.2 Most expensive medical condition on average, with rank (window function)
SELECT
    medical_condition,
    ROUND(AVG(billing_amount), 2) AS avg_billing_amount,
    RANK() OVER (ORDER BY AVG(billing_amount) DESC) AS cost_rank
FROM patients
GROUP BY medical_condition;

-- 3.3 Conditions where average billing exceeds the overall average (HAVING + subquery)
SELECT
    medical_condition,
    ROUND(AVG(billing_amount), 2) AS avg_billing_amount
FROM patients
GROUP BY medical_condition
HAVING AVG(billing_amount) > (SELECT AVG(billing_amount) FROM patients)
ORDER BY avg_billing_amount DESC;


-- ----------------------------------------------------------------------------
-- 4. ADMISSION & OUTCOME ANALYSIS
-- ----------------------------------------------------------------------------

-- 4.1 Admission type breakdown
SELECT
    admission_type,
    COUNT(*)                      AS patient_count,
    ROUND(AVG(billing_amount), 2) AS avg_billing_amount,
    ROUND(AVG(length_of_stay), 1) AS avg_length_of_stay
FROM patients
GROUP BY admission_type
ORDER BY patient_count DESC;

-- 4.2 Test result distribution by admission type
SELECT
    admission_type,
    test_results,
    COUNT(*) AS record_count
FROM patients
GROUP BY admission_type, test_results
ORDER BY admission_type, record_count DESC;

-- 4.3 Abnormal test result rate per medical condition (CASE + aggregate)
SELECT
    medical_condition,
    COUNT(*) AS total_cases,
    SUM(CASE WHEN test_results = 'Abnormal' THEN 1 ELSE 0 END) AS abnormal_cases,
    ROUND(100.0 * SUM(CASE WHEN test_results = 'Abnormal' THEN 1 ELSE 0 END) / COUNT(*), 2) AS abnormal_rate_pct
FROM patients
GROUP BY medical_condition
ORDER BY abnormal_rate_pct DESC;


-- ----------------------------------------------------------------------------
-- 5. FINANCIAL / BILLING ANALYSIS
-- ----------------------------------------------------------------------------

-- 5.1 Overall billing summary
SELECT
    COUNT(*)                       AS total_records,
    SUM(billing_amount)            AS total_billing,
    ROUND(AVG(billing_amount), 2)  AS avg_billing,
    MIN(billing_amount)            AS min_billing,
    MAX(billing_amount)            AS max_billing
FROM patients;

-- 5.2 Total and average billing by insurance provider
SELECT
    insurance_provider,
    COUNT(*)                      AS patient_count,
    SUM(billing_amount)           AS total_billing,
    ROUND(AVG(billing_amount), 2) AS avg_billing
FROM patients
GROUP BY insurance_provider
ORDER BY total_billing DESC;

-- 5.3 Top 10% highest-billed patients (subquery with percentile-style filter)
SELECT name, medical_condition, billing_amount
FROM patients
WHERE billing_amount >= (
    SELECT billing_amount
    FROM patients
    ORDER BY billing_amount DESC
    LIMIT 1 OFFSET (SELECT CAST(COUNT(*) * 0.10 AS INT) FROM patients)
)
ORDER BY billing_amount DESC;

-- 5.4 Running total of monthly billing using a window function (CTE)
WITH monthly_billing AS (
    SELECT
        DATE_FORMAT(date_of_admission, '%Y-%m') AS admission_month,
        SUM(billing_amount) AS monthly_total
    FROM patients
    GROUP BY DATE_FORMAT(date_of_admission, '%Y-%m')
)
SELECT
    admission_month,
    monthly_total,
    SUM(monthly_total) OVER (ORDER BY admission_month) AS running_total
FROM monthly_billing
ORDER BY admission_month;


-- ----------------------------------------------------------------------------
-- 6. HOSPITAL & PROVIDER ANALYSIS
-- ----------------------------------------------------------------------------

-- 6.1 Top 10 hospitals by patient volume
SELECT
    hospital,
    COUNT(*) AS patient_count,
    ROUND(AVG(billing_amount), 2) AS avg_billing
FROM patients
GROUP BY hospital
ORDER BY patient_count DESC
LIMIT 10;

-- 6.2 Top 10 doctors by number of patients treated
SELECT
    doctor,
    COUNT(*) AS patients_treated,
    ROUND(AVG(billing_amount), 2) AS avg_billing
FROM patients
GROUP BY doctor
ORDER BY patients_treated DESC
LIMIT 10;


-- ----------------------------------------------------------------------------
-- 7. TIME-BASED / TREND ANALYSIS
-- ----------------------------------------------------------------------------

-- 7.1 Admissions per year
SELECT
    admission_year,
    COUNT(*) AS total_admissions
FROM patients
GROUP BY admission_year
ORDER BY admission_year;

-- 7.2 Admissions per month across all years (seasonality check)
SELECT
    admission_month,
    COUNT(*) AS total_admissions
FROM patients
GROUP BY admission_month
ORDER BY admission_month;

-- 7.3 Year-over-year average length of stay (CTE + window function)
WITH yearly_los AS (
    SELECT
        admission_year,
        ROUND(AVG(length_of_stay), 2) AS avg_los
    FROM patients
    GROUP BY admission_year
)
SELECT
    admission_year,
    avg_los,
    avg_los - LAG(avg_los) OVER (ORDER BY admission_year) AS change_from_prev_year
FROM yearly_los
ORDER BY admission_year;


-- ----------------------------------------------------------------------------
-- 8. MEDICATION ANALYSIS
-- ----------------------------------------------------------------------------

-- 8.1 Medication usage frequency and associated average billing
SELECT
    medication,
    COUNT(*)                      AS times_prescribed,
    ROUND(AVG(billing_amount), 2) AS avg_billing
FROM patients
GROUP BY medication
ORDER BY times_prescribed DESC;

-- 8.2 Most frequently prescribed medication per medical condition
--     (CTE + window function to rank medications within each condition)
WITH med_counts AS (
    SELECT
        medical_condition,
        medication,
        COUNT(*) AS prescription_count,
        ROW_NUMBER() OVER (
            PARTITION BY medical_condition
            ORDER BY COUNT(*) DESC
        ) AS rn
    FROM patients
    GROUP BY medical_condition, medication
)
SELECT medical_condition, medication AS top_medication, prescription_count
FROM med_counts
WHERE rn = 1
ORDER BY medical_condition;

-- ============================================================================
-- END OF ANALYSIS QUERIES
-- ============================================================================
