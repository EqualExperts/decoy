SELECT
    range as id,
    xeger('[0-9]{4}-[A-Z]{4,6}-[1-9]+') as identifier,
    xeger('\(\+0[0-9]{2}\) 07[0-9]{3} [0-9]{6}') as tel,
    mimesis_en('person.email'),
    mimesis_en('person.name')
FROM range(20);