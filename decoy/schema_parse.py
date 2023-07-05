default_generators = {
    'BIGINT': "faker_en('random_int')",
    'VARCHAR': "xeger('[a-zA-Z0-9]{6,}')",
    'UNKNOWN': "xeger('[a-zA-Z0-9]{6,}')",
}


def get_tablename(sql_query):
    return sql_query.split('CREATE TABLE ')[1].split('(')[0]


def get_table_fields(sql_query):
    fields = sql_query.split('(')[1].split(')')[0]
    return [x for x in fields.split(', ')]


def convert_sqltype_to_generator(default_generators, dtype):
    try:
        return default_generators[dtype]
    except:
        return default_generators['UNKNOWN']


def convert_fields_to_generator(default_generators, fields):
    column_statement = ''
    len_fields = len(fields) - 1
    for i in enumerate(fields):
        name, dtype = i[1].split(' ')
        dtype = convert_sqltype_to_generator(default_generators, dtype)
        column_statement += f'{dtype} as {name},'
        if i[0] < len_fields:
            column_statement += '\n'
    return column_statement


def construct_sql_generator(default_generators, sql_query, nrows):
    table_name = get_tablename(sql_query)
    fields = get_table_fields(sql_query)
    col_statement = convert_fields_to_generator(default_generators, fields)
    return f"""CREATE OR REPLACE TABLE {table_name} AS 
(SELECT\n{col_statement} 
FROM range({nrows}));
"""


def parse_full_sql_schema(input_filename, output_filename, nrows, default_generators=default_generators,):
    with open(input_filename, 'r') as input_f:
        with open(output_filename, 'w+') as output_f:
            for line in input_f.readlines():
                output_f.write(construct_sql_generator(
                    default_generators, line, nrows))
