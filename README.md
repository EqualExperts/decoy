# decoy

Synthetic data generation with DuckDB

## Requirements

- Python 3.10+

## Python setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

OR

```pip install --editable .```

## Unit tests

```bash
PYTHONPATH=. pytest
```

## Command line tools

Run a sql file

```bash
./cli exec examples/basic.sql
```

Use the SQL REPL

```bash
./cli repl
```

Register as a jupyter kernel

```bash
./cli kernel-install
jupyter lab
```

Parse A SQL Schema Definition

```bash
./cli sqlparse './examples/test_schema.sql' './examples/schema_parse_output.sql' 5

./cli exec ./examples/schema_parse_output.sql
```

** At the moment the kernel only works if the notebook is in the root of this project. Something needs fixing with the kernel path.

## Data generation functions

The python Faker library is exposed for the en-GB locale, the registration function can easily be modified to include more locales.

```sql
select faker_name() from range(20);
```

The python Mimesis library is exposed for the en-GB locale, the registration function can easily be modified to include more locales.

```sql
select mimesis_person_full_name() from range(20);
```

There is a reverse regex function for generating text patterns.

```sql
SELECT xeger('\(\+0[0-9]{2}\) 07[0-9]{3} [0-9]{6}') as tel FROM range(20);
```

Functions are also available for intra-table sampling, column shuffling, oversampling from other tables.

```sql
-- Create a names table
CREATE TABLE name_table AS SELECT range as id, faker_name() as name FROM range(1000);

-- Select 10k names randomly from the name table.
SELECT oversample('name_table', 'name') from range(10000);

SELECT name, shuffle(name) as name_shuffled, intratable_sample(name) as name_sampled FROM name_table;
```
