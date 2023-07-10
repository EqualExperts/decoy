CREATE OR REPLACE TABLE companies AS (
    SELECT
        range as id,
        faker_company() as company_name,
        faker_catch_phrase() as description
    FROM range(10)
);
CREATE OR REPLACE TABLE people AS (
    SELECT
        range as id,
        oversample('companies', 'id') as company_id,
        faker_name() as full_name,
        faker_date_of_birth() as dob,
        faker_passport_number() as passport_number,
    FROM range(100)
);
COPY (SELECT * FROM companies ) TO 'export_company.csv' WITH (HEADER 1, DELIMITER ',');
COPY (SELECT * FROM people JOIN companies on people.company_id = companies.id ) TO 'export_people.csv' WITH (HEADER 1, DELIMITER ',');
