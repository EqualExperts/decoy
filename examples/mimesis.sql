SELECT
  range as id,
  mimesis_en('person.username') as username,
  mimesis_en('person.full_name') as name,
  mimesis_en('person.email') as email
FROM range(100);