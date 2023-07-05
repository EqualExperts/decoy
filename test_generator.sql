CREATE OR REPLACE TABLE companies AS 
(SELECT
BIGINT as id,
VARCHAR as company_name,
VARCHAR as description, 
FROM range(5));
CREATE OR REPLACE TABLE people AS 
(SELECT
BIGINT as id,
VARCHAR as company_id,
VARCHAR as full_name,
VARCHAR as dob,
VARCHAR as passport_number, 
FROM range(5));
