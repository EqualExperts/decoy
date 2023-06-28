SELECT
  decoy_en('name') as name,
  decoy_en('address') as address
FROM range(100);

---

SELECT
  decoy_en('first_name') as first_name,
  decoy_en('last_name') as last_name,
  decoy_en('address') as address
FROM range(100);