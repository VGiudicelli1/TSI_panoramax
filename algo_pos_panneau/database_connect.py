from configparser import ConfigParser
import psycopg2
import pandas as pd

__path__ = "/".join(__file__.split("/")[:-1])

###############################################################################
##  Database connection                                                      ##
###############################################################################

def _load_config(filename=__path__ + "/database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    
    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return config

def _connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def df_to_insert(df, df_keys, struct, pg_table, pg_columns):
    data = df.loc[:, df_keys].values
    values = ",".join([struct.format(*line) for line in list(data)]).replace("'None'", "NULL").replace("'nan'", "NULL").replace("nan", "NULL").replace("None", "NULL")
    return f'''
        INSERT INTO {pg_table} ({",".join(pg_columns)})
        VALUES {values}'''

###############################################################################
##  Start                                                                    ##
###############################################################################

_config = _load_config()
conn = _connect(_config)
