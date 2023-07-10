SELECT
  faker_name() as name,
  faker_address() as address
FROM range(100);

---

SELECT
  faker_first_name() as first_name,
  faker_last_name() as last_name,
  faker_address() as address
FROM range(100);
