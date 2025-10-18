import pandas as pd
from psycopg import sql, connect
from typing import Optional


class PostgresClient:

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        db_port: int,
        db_name: str,
    ):

        try:

            uri = f'postgresql://{username}:{password}@{host}:{db_port}/{db_name}?sslmode=require'
            self._conn = connect(uri)

        except Exception as e:
            raise Exception(e)

    @staticmethod
    def format_query(text: str, params: dict) -> str:
        def wrap(v):
            if isinstance(v, (int, float)):
                return sql.SQL(str(v))
            if pd.isna(v):
                return sql.SQL("NULL")
            # for placeholders
            if isinstance(v, (sql.SQL, sql.Identifier)):
                return v
            return sql.Literal(v)

        return sql.SQL(text).format(**{k: wrap(v) for k, v in params.items()}).as_string(None)

    def query(
        self,
        query,
        params: Optional[tuple] = None
    ):

        try:
            cols = None
            rows = None

            with self._conn.transaction():
                with self._conn.cursor() as cur:
                    if params:
                        cur.execute(query, params)
                    else:
                        cur.execute(query)

                        # return rows in a df if there are any
                        if cur.description:
                            cols = [desc[0] for desc in cur.description]
                            if cols:
                                rows = cur.fetchall()

            if cols:
                return pd.DataFrame(
                    data=rows,
                    columns=cols
                )

            else:
                return None

        except Exception as e:
            raise Exception(e)
