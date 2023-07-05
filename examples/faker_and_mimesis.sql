select 
    range as id, 
    faker_en('address') as address, 
    mimesis_en('person.full_name') as name 
from range(10)