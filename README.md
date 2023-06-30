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

## Data generation functions

The python Faker library is exposed for the en-GB locale, the registration function can easily be modified to include more locales.

```sql
select faker_en('name') from range(20);
```

Custom functions are available for intra-table sampling, column shuffling, oversampling from other tables.

```sql
-- Create a names table
CREATE TABLE name_table AS SELECT range as id, faker_en('name') as name FROM range(1000);

-- Select 10k names randomly from the name table.
SELECT oversample('name_table', 'name') from range(10000);

SELECT name, shuffle(name) as name_shuffled, intratable_sample(name) as name_sampled FROM name_table;
```
