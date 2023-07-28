# Decoy - A Synthetic Data Generator

Synthetic data generation with DuckDB

Decoy is a Synthetic Data Generator using DuckDB at it's core. The main aim of the project is to reduce the overhead in creating synthetic data and provide all the tools to easily test your synthetic data queries.

It has integrated well known Python based synthetic data generators such as [Faker](https://faker.readthedocs.io/en/master/), [Mimesis](https://mimesis.name/en/master/) and [Random](https://python.readthedocs.io/en/stable/library/random.html).

The power of this application comes from the ability to write scripts to repeatably generate data, to use interactive tools to test your queries and the ability to create tables which interact, allowing for the creation of full relational databases.

## Requirements & Setup

```bash
#Requires Python 3.10+
pip install --editable .
```
OR
```bash
#Requires Python 3.10+
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## Data Generation Tools

Decoy exposes multiple command line tools to generate data and test generating data 

### Generate Data From a .sql File

The main core of decoy is the ability to repeatibly generate synthetic data from a .sql file. 

```bash
decoy exec examples/basic.sql
```
There are multiple examples in the `./examples` folder.

### Interactive Testing Playgrounds

In addtion to a CLI to run .sql files. Decoy also provides an interactive environment to easily build your queries and quickly test that they are working correctly.

#### Jupyter Lab Kernel

[Jupyter Lab](https://jupyter.org/) is a web-based interactive repl for which we have created a decoy kernel allowing you to run decoy SQL queries and quickly observe their output

```bash
#install the kernel for first-time use
decoy kernel-install

#Running the Jupyter lab web server
jupyter lab
```
Then select `decoy` as the kernel when starting a new notebook instance.

Some of the files in `./examples` are in the `*.ipynb`, these are to be read using the Jupyter kernel. Jupyter also integrates markdown too - so if required for documentation, you can also explain though processes.

#### Use the SQL REPL

Decoy also includes a command-line REPL too which provides the same interactive testing environment but on the command line.

```bash
decoy repl
```
Please not that the query must end with a `;` and to execute the query select `<Alt/Opt><Enter>` as multiline queires are supported.


### Parse A SQL Schema Definition

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

You can also generate imperfect data by using some of the data messer functions which will either add `NULL` or junk data. These are currently hardcoded and the functions are in `./decoy/udf_arrow.py`
```sql
CREATE OR REPLACE TABLE names_full AS (
    SELECT
        faker_name() as full_name,
    FROM range(30)
);

UPDATE names_full SET full_name = messy_data_nullifier(full_name);
``` 

### Exporting Data

DuckDB handles multiple [export functions](https://duckdb.org/docs/guides/import/parquet_export). Including CSV and Parquet
```sql
COPY (SELECT faker_name() FROM range(5)) TO 'export_test.csv' WITH (HEADER 1, DELIMITER ',');

COPY (SELECT faker_name() FROM range(5)) TO 'export_parquet.parquet';
```


## Unit tests

```bash
PYTHONPATH=. pytest
```