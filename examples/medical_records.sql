-- Create a table of medical conditions that can be referenced
CREATE OR REPLACE TABLE medical_conditions AS (
    SELECT 
        range + 1 as condition_id,
        UNNEST([
            'Hypertension', 'Type 2 Diabetes', 'Asthma', 'Arthritis', 
            'Anxiety', 'Depression', 'Migraine', 'Allergies',
            'GERD', 'Lower Back Pain', 'High Cholesterol', 'Insomnia',
            'Sinusitis', 'Bronchitis', 'Vitamin D Deficiency'
        ]) as condition_name,
        UNNEST([
            'I10', 'E11', 'J45', 'M15',
            'F41', 'F33', 'G43', 'J30',
            'K21', 'M54.5', 'E78', 'G47',
            'J01', 'J20', 'E55'
        ]) as icd_10_code
    FROM range(15)
);

-- Create a table of medications
CREATE OR REPLACE TABLE medications AS (
    SELECT 
        range + 1 as medication_id,
        UNNEST([
            'Lisinopril', 'Metformin', 'Albuterol', 'Ibuprofen',
            'Sertraline', 'Fluoxetine', 'Sumatriptan', 'Cetirizine',
            'Omeprazole', 'Cyclobenzaprine', 'Atorvastatin', 'Zolpidem',
            'Amoxicillin', 'Azithromycin', 'Ergocalciferol'
        ]) as medication_name,
        UNNEST([
            '10mg', '500mg', '90mcg', '400mg',
            '50mg', '20mg', '50mg', '10mg',
            '20mg', '10mg', '40mg', '5mg',
            '500mg', '250mg', '50000IU'
        ]) as typical_dose
    FROM range(15)  -- 15 medications
);

-- Create doctors
CREATE OR REPLACE TABLE doctors AS (
    SELECT 
        range + 1 as doctor_id,
        faker_name() as doctor_name,
        UNNEST([
            'Family Medicine', 'Internal Medicine', 'Pediatrics', 
            'Family Medicine', 'Internal Medicine', 'Geriatrics',
            'Family Medicine', 'Internal Medicine', 'Family Medicine',
            'Internal Medicine'
        ]) as specialty
    FROM range(10)  -- 10 doctors
);

-- Create patients
CREATE OR REPLACE TABLE patients AS (
    SELECT 
        range + 1 as patient_id,
        faker_name() as patient_name,
        faker_date_of_birth() as date_of_birth,
        faker_address() as address,
        faker_phone_number() as phone,
        faker_email() as email,
        CASE random_randint(1, 2) 
            WHEN 1 THEN 'M' 
            ELSE 'F' 
        END as gender,
        random_randint(1, 10) as primary_doctor_id
    FROM range(10000)  -- 10000 patients
);

-- Create patient conditions (some patients have multiple conditions)
CREATE OR REPLACE TABLE patient_conditions AS (
    SELECT 
        range + 1 as record_id,
        oversample('patients', 'patient_id') as patient_id,
        oversample('medical_conditions', 'condition_id') as condition_id,
        mimesis_datetime_date() as diagnosis_date,
        CASE random_randint(1, 4) 
            WHEN 1 THEN 'Resolved'
            ELSE 'Active'
        END as status
    FROM range(15000)  -- 15000 condition records
);

-- Create prescriptions
CREATE OR REPLACE TABLE prescriptions AS (
    SELECT 
        range + 1 as prescription_id,
        oversample('patient_conditions', 'patient_id') as patient_id,
        oversample('medications', 'medication_id') as medication_id,
        oversample('doctors', 'doctor_id') as prescribing_doctor_id,
        mimesis_datetime_date() as prescribed_date,
        random_randint(0, 11) as refills_remaining,
        CASE random_randint(1, 10) 
            WHEN 1 THEN 'Discontinued'
            ELSE 'Active'
        END as status
    FROM range(20000)  -- 20000 prescriptions
);

-- Create visits (medical appointments)
CREATE OR REPLACE TABLE visits AS (
    SELECT 
        range + 1 as visit_id,
        oversample('patients', 'patient_id') as patient_id,
        oversample('doctors', 'doctor_id') as doctor_id,
        mimesis_datetime_datetime() as visit_datetime,
        UNNEST([
            'Annual Physical', 'Follow-up', 'Acute Care', 
            'Chronic Disease Management', 'Preventive Care',
            'Vaccination', 'Lab Review', 'Prescription Renewal'
        ])[random_randint(1, 8)] as visit_type,
        random_randint(1, 5) * 15 as duration_minutes,
        CASE random_randint(1, 20) 
            WHEN 1 THEN 'Cancelled'
            WHEN 2 THEN 'No Show'
            ELSE 'Completed'
        END as status
    FROM range(30000)  -- 30000 visits
);

-- Create vital signs recorded during visits
CREATE OR REPLACE TABLE vital_signs AS (
    SELECT 
        visit_id,
        random_randint(90, 180) as systolic_bp,
        random_randint(60, 100) as diastolic_bp,
        random_randint(60, 100) as heart_rate,
        random_randint(95, 100) as oxygen_saturation,
        random_randint(960, 995) / 10.0 as temperature,
        random_randint(12, 20) as respiratory_rate
    FROM visits 
    WHERE status = 'Completed'
);

-- Example query to get a patient's complete medical record
CREATE OR REPLACE VIEW patient_medical_record AS (
    SELECT 
        p.patient_id,
        p.patient_name,
        p.date_of_birth,
        p.gender,
        d.doctor_name as primary_doctor,
        mc.condition_name,
        pc.diagnosis_date,
        pc.status as condition_status,
        m.medication_name,
        m.typical_dose,
        pr.prescribed_date,
        pr.status as prescription_status,
        v.visit_datetime,
        v.visit_type,
        v.status as visit_status,
        vs.systolic_bp,
        vs.diastolic_bp,
        vs.heart_rate,
        vs.temperature
    FROM patients p
    LEFT JOIN doctors d ON p.primary_doctor_id = d.doctor_id
    LEFT JOIN patient_conditions pc ON p.patient_id = pc.patient_id
    LEFT JOIN medical_conditions mc ON pc.condition_id = mc.condition_id
    LEFT JOIN prescriptions pr ON p.patient_id = pr.patient_id
    LEFT JOIN medications m ON pr.medication_id = m.medication_id
    LEFT JOIN visits v ON p.patient_id = v.patient_id
    LEFT JOIN vital_signs vs ON v.visit_id = vs.visit_id
    ORDER BY p.patient_id, v.visit_datetime DESC
); 