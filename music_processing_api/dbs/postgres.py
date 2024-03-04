import os
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from functools import wraps
from dotenv import load_dotenv


load_dotenv(override=True)

class Postgres:

    def __init__(self,
                 LOG: bool = True,
                 DEBUG: bool = True,
                 db_url_raw: str = 'postgresql+psycopg2://%(user)s:%(passwd)s@%(host)s:%(port)s/%(db)s'
                 ):
        if LOG:
            self.echo = True
        else:
            self.echo = False
        self.DEBUG = DEBUG
        self._check_env_variables()
        self.db_params = self._get_db_params()
        self.db_url_raw = db_url_raw
        self.engine = self.create_engine()

    def _check_env_variables(self):
        if self.DEBUG:
            variable_keys = [
                'LOCAL_DB_HOST',
                'LOCAL_DB_PORT',
                'LOCAL_DB_USER',
                'LOCAL_DB_PWD',
                'LOCAL_DB_NAME'
            ]
        else:
            variable_keys = [
                'DB_HOST',
                'DB_PORT',
                'DB_USER',
                'DB_PWD',
                'DB_NAME'
            ]
        for key in variable_keys:
            assert key in os.environ.keys(
            ), f'Environment variable \'{key}\' was not provided'

    def _get_db_params(self):
        if self.DEBUG:
            db_param = dict(
                host=str(os.getenv("LOCAL_DB_HOST")),
                port=int(os.getenv("LOCAL_DB_PORT")),
                user=str(os.getenv("LOCAL_DB_USER")),
                passwd=str(os.getenv("LOCAL_DB_PWD")),
                db=str(os.getenv("LOCAL_DB_NAME"))
            )
        else:
            db_param = dict(
                host=str(os.environ["DB_HOST"]),
                port=int(os.environ["DB_PORT"]),
                user=str(os.environ["DB_USER"]),
                passwd=(os.environ["DB_PWD"]),
                db=str(os.environ["DB_NAME"])
            )
        return db_param

    def create_engine(self):
        db_url = self.db_url_raw % self.db_params
        engine = create_engine(
            db_url,
            connect_args={'connect_timeout': 10000},
            poolclass=QueuePool,
            pool_size=5,
            isolation_level="AUTOCOMMIT",
            echo=self.echo,
            max_overflow=0,
            pool_pre_ping=True
        )
        return engine

    def execute_with_params(self, query: str, fetch_result: bool, params):
        with self.engine.connect() as conn:
            if fetch_result:
                result = conn.exec_driver_sql(query, params)
                returned_data = result.fetchall()
            else:
                conn.exec_driver_sql(query, params)
                returned_data = None

        return returned_data

    def get_column_values(self, table: str, returning_column: str, condition_column: str, condition_column_value):
        query = f"""
            SELECT {returning_column}
            FROM {table}
            WHERE {condition_column} = %s;
        """
        result = self.execute_with_params(query=query, fetch_result=True, params=[(condition_column_value,)])
        column_values = [val[0] for val in result]
        return column_values

    def create_insert_query(self, table: str, columns: list, returning_columns: list = None):
        columns_str = ', '.join(columns)
        s_string = ', '.join(['%s'] * len(columns))
        query = f"""
            INSERT INTO {table} ({columns_str})
            VALUES ({s_string})
        """
        if returning_columns:
            returning_columns_str = ', '.join(returning_columns)
            query += f' RETURNING {returning_columns_str}'
        query += ';'
        return query

    def insert_data(self, table: str, columns: list, values: list, returning_columns: list = None):
        insert_query = self.create_insert_query(
            table=table,
            returning_columns=returning_columns,
            columns=columns
        )
        generated_data = self.execute_with_params(insert_query, bool(returning_columns), tuple(values))
        if generated_data:
            generated_data = dict(zip(returning_columns, generated_data[0]))
        return generated_data


    def get_id(self, table: str, column: str, column_value):
        ids = self.get_column_values(
            table=table,
            returning_column='id',
            condition_column=column,
            condition_column_value=column_value
        )
        if ids:
            id = ids[0]
        else:
            generated_data = self.insert_data(
                table=table,
                columns=[column],
                values=[(column_value,)],
                returning_columns=['id']
            )
            id = generated_data.get('id')
        return id

    def update_db(self, data):
        artist_id = self.get_id(
            table='artists',
            column='name',
            column_value=data.get('artist_name')
        )

        data.pop('artist_name')
        data['artist_id'] = artist_id

        album_id = self.get_id(
            table='albums',
            column='title',
            column_value=data.get('album_name')
        )

        data.pop('album_name')
        data['album_id'] = album_id

        data['title'] = data.get('song_title')
        data.pop('song_title')

        insert_columns, insert_values = zip(*data.items())

        self.insert_data(
            table='song_response_history',
            columns=insert_columns,
            values=insert_values
        )

    def insert_to_db(self):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                data = func(*args, **kwargs)
                self.update_db(data.copy())
                return data
            return wrapper
        return decorator


postgres = Postgres()
