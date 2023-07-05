CREATE OR REPLACE TABLE companies AS 
(SELECT
faker_en('random_int') as id,
xeger('[a-zA-Z0-9]{6,}') as company_name,
xeger('[a-zA-Z0-9]{6,}') as description, 
FROM range(5));
CREATE OR REPLACE TABLE people AS 
(SELECT
faker_en('random_int') as id,
xeger('[a-zA-Z0-9]{6,}') as company_id,
xeger('[a-zA-Z0-9]{6,}') as full_name,
xeger('[a-zA-Z0-9]{6,}') as dob,
xeger('[a-zA-Z0-9]{6,}') as passport_number, 
FROM range(5));
