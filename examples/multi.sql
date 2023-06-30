SELECT
  faker_en('name') as name,
  faker_en('address') as address
FROM range(100);

---

SELECT
  faker_en('first_name') as first_name,
  faker_en('last_name') as last_name,
  faker_en('address') as address
FROM range(100);
