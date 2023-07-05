SELECT
  faker_en('name') as name,
  faker_en('address') as address
FROM range(1000);
