select
    range as id,
    faker_address() as address,
    mimesis_person_full_name() as name
from range(10)