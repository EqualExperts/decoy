CREATE OR REPLACE TABLE names_full AS (
    SELECT
        faker_name() as full_name,
    FROM range(30)
);

---

UPDATE names_full SET full_name = messy_data_junkadder(full_name);