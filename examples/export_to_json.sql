-- Example showing how to export decoy medical records as JSON documents
-- This uses DuckDB's built-in JSON functions to transform rows into JSON documents

-- Export all patient records as JSON documents
SELECT json_object(
    'patient_id', patient_id,
    'name', patient_name,
    'date_of_birth', date_of_birth,
    'gender', gender,
    'contact', json_object(
        'address', address,
        'phone', phone,
        'email', email
    )
)
FROM patients;

-- Export a more complex view with nested data as JSON
WITH patient_complete AS (
    SELECT 
        p.patient_id,
        p.patient_name,
        p.date_of_birth,
        p.gender,
        p.address,
        p.phone,
        p.email,
        d.doctor_name as primary_doctor,
        list(json_object(
            'condition_name', mc.condition_name,
            'icd_10_code', mc.icd_10_code,
            'diagnosis_date', pc.diagnosis_date,
            'status', pc.status
        )) as conditions,
        list(DISTINCT json_object(
            'medication_name', m.medication_name,
            'typical_dose', m.typical_dose,
            'prescribed_date', pr.prescribed_date,
            'status', pr.status,
            'refills_remaining', pr.refills_remaining,
            'prescribing_doctor', pd.doctor_name
        )) as prescriptions,
        list(json_object(
            'datetime', v.visit_datetime,
            'type', v.visit_type,
            'doctor', vd.doctor_name,
            'duration_minutes', v.duration_minutes,
            'status', v.status,
            'vitals', CASE 
                WHEN vs.visit_id IS NOT NULL THEN json_object(
                    'systolic_bp', vs.systolic_bp,
                    'diastolic_bp', vs.diastolic_bp,
                    'heart_rate', vs.heart_rate,
                    'temperature', vs.temperature,
                    'oxygen_saturation', vs.oxygen_saturation,
                    'respiratory_rate', vs.respiratory_rate
                )
                ELSE NULL
            END
        )) as visits
    FROM patients p
    LEFT JOIN doctors d ON p.primary_doctor_id = d.doctor_id
    LEFT JOIN patient_conditions pc ON p.patient_id = pc.patient_id
    LEFT JOIN medical_conditions mc ON pc.condition_id = mc.condition_id
    LEFT JOIN prescriptions pr ON p.patient_id = pr.patient_id
    LEFT JOIN medications m ON pr.medication_id = m.medication_id
    LEFT JOIN doctors pd ON pr.prescribing_doctor_id = pd.doctor_id
    LEFT JOIN visits v ON p.patient_id = v.patient_id
    LEFT JOIN doctors vd ON v.doctor_id = vd.doctor_id
    LEFT JOIN vital_signs vs ON v.visit_id = vs.visit_id
    GROUP BY p.patient_id, p.patient_name, p.date_of_birth, p.gender, 
             p.address, p.phone, p.email, d.doctor_name
)
SELECT json_object(
    'patient_id', patient_id,
    'name', patient_name,
    'date_of_birth', date_of_birth,
    'gender', gender,
    'contact', json_object(
        'address', address,
        'phone', phone,
        'email', email
    ),
    'primary_doctor', primary_doctor,
    'conditions', conditions,
    'prescriptions', prescriptions,
    'visits', visits
)
FROM patient_complete;

-- Export specific patients matching certain criteria
SELECT json_object(
    'patient_id', patient_id,
    'name', patient_name,
    'date_of_birth', date_of_birth,
    'gender', gender,
    'contact', json_object(
        'address', address,
        'phone', phone,
        'email', email
    )
)
FROM patients
WHERE gender = 'F';

-- To save all patient records to a single file:
COPY (
    SELECT json_object(
        'patient_id', patient_id,
        'name', patient_name,
        'date_of_birth', date_of_birth,
        'gender', gender,
        'contact', json_object(
            'address', address,
            'phone', phone,
            'email', email
        )
    )
    FROM patients
) TO 'patients.json';

-- Export each patient's complete medical record to a separate JSON file
-- Files will be named like: patient_1.json, patient_2.json, etc.
COPY (
    WITH patient_data AS (
        SELECT 
            p.patient_id,
            p.patient_name,
            p.date_of_birth,
            p.gender,
            p.address,
            p.phone,
            p.email,
            d.doctor_name as primary_doctor,
            list(json_object(
                'condition_name', mc.condition_name,
                'icd_10_code', mc.icd_10_code,
                'diagnosis_date', pc.diagnosis_date,
                'status', pc.status
            )) as conditions,
            list(DISTINCT json_object(
                'medication_name', m.medication_name,
                'typical_dose', m.typical_dose,
                'prescribed_date', pr.prescribed_date,
                'status', pr.status,
                'refills_remaining', pr.refills_remaining,
                'prescribing_doctor', pd.doctor_name
            )) as prescriptions,
            list(json_object(
                'datetime', v.visit_datetime,
                'type', v.visit_type,
                'doctor', vd.doctor_name,
                'duration_minutes', v.duration_minutes,
                'status', v.status,
                'vitals', CASE 
                    WHEN vs.visit_id IS NOT NULL THEN json_object(
                        'systolic_bp', vs.systolic_bp,
                        'diastolic_bp', vs.diastolic_bp,
                        'heart_rate', vs.heart_rate,
                        'temperature', vs.temperature,
                        'oxygen_saturation', vs.oxygen_saturation,
                        'respiratory_rate', vs.respiratory_rate
                    )
                    ELSE NULL
                END
            )) as visits
        FROM patients p
        LEFT JOIN doctors d ON p.primary_doctor_id = d.doctor_id
        LEFT JOIN patient_conditions pc ON p.patient_id = pc.patient_id
        LEFT JOIN medical_conditions mc ON pc.condition_id = mc.condition_id
        LEFT JOIN prescriptions pr ON p.patient_id = pr.patient_id
        LEFT JOIN medications m ON pr.medication_id = m.medication_id
        LEFT JOIN doctors pd ON pr.prescribing_doctor_id = pd.doctor_id
        LEFT JOIN visits v ON p.patient_id = v.patient_id
        LEFT JOIN doctors vd ON v.doctor_id = vd.doctor_id
        LEFT JOIN vital_signs vs ON v.visit_id = vs.visit_id
        GROUP BY p.patient_id, p.patient_name, p.date_of_birth, p.gender, 
                 p.address, p.phone, p.email, d.doctor_name
    )
    SELECT json_object(
        'patient_id', patient_id,
        'name', patient_name,
        'date_of_birth', date_of_birth,
        'gender', gender,
        'contact', json_object(
            'address', address,
            'phone', phone,
            'email', email
        ),
        'primary_doctor', primary_doctor,
        'conditions', conditions,
        'prescriptions', prescriptions,
        'visits', visits
    )
    FROM patient_data
) TO 'patient_{{patient_id}}.json'
  (FORMAT JSON);

-- Cleanup
DROP TABLE patients;
DROP TABLE visits;
DROP TABLE medications; 