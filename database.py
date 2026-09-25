import os
from contextlib import closing

import psycopg2


class PlayerDatabaseError(Exception):
    pass


class PlayerDatabase:
    def get_players(self):
        database_name = os.environ.get("PGDATABASE", "photon")
        try:
            with closing(psycopg2.connect(dbname=database_name)) as connection:
                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT id, codename FROM public.players ORDER BY id;"
                        )
                        return cursor.fetchall()
        except psycopg2.Error as error:
            raise PlayerDatabaseError(str(error)) from error

    def add_player(self, player_id, codename):
        database_name = os.environ.get("PGDATABASE", "photon")
        try:
            with closing(psycopg2.connect(dbname=database_name)) as connection:
                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            INSERT INTO public.players (id, codename)
                            VALUES (%s, %s)
                            RETURNING id, codename;
                            """,
                            (player_id, codename),
                        )
                        return cursor.fetchone()
        except psycopg2.Error as error:
            raise PlayerDatabaseError(str(error)) from error

    def delete_player(self, player_id):
        database_name = os.environ.get("PGDATABASE", "photon")
        try:
            with closing(psycopg2.connect(dbname=database_name)) as connection:
                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "DELETE FROM public.players WHERE id = %s RETURNING id, codename;",
                            (player_id,),
                        )
                        return cursor.fetchone()
        except psycopg2.Error as error:
            raise PlayerDatabaseError(str(error)) from error