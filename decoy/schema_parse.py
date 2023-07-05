def get_tablename(sql_query):
    return sql_query.split('CREATE TABLE ')[1].split('(')[0]


def get_table_fields(sql_query):
    fields = sql_query.split('(')[1].split(')')[0]
    return [x for x in fields.split(', ')]


def convert_fields_to_generator(fields):
    column_statement = ''
    len_fields = len(fields) - 1
    for i in enumerate(fields):
        name, dtype = i[1].split(' ')
        column_statement += f'{dtype} as {name},'
        if i[0] < len_fields:
            column_statement += '\n'
    return column_statement


def construct_sql_generator(sql_query, nrows):
    table_name = get_tablename(sql_query)
    fields = get_table_fields(sql_query)
    col_statement = convert_fields_to_generator(fields)
    return f"""CREATE OR REPLACE TABLE {table_name} AS 
(SELECT\n{col_statement} 
FROM range({nrows}));
"""


def parse_full_sql_schema(input_filename, output_filename, nrows):
    with open(input_filename, 'r') as f:
        with open(output_filename, 'w+') as filehandle:
            for line in f.readlines():
                filehandle.write(construct_sql_generator(line, nrows))
