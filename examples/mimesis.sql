SELECT
  range as id,
  mimesis_person_username() as username,
  mimesis_person_full_name() as name,
  mimesis_person_email() as email
FROM range(100);