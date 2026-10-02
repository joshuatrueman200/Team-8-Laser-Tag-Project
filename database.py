import os
from contextlib import closing

import psycopg2


class PlayerDatabaseError(Exception):
    pass


class PlayerDatabase:
    # Use one path for every database call so errors and cleanup stay the same.
    def _query(self, query, parameters=(), fetch_all=False):
        database_name = os.environ.get("PGDATABASE", "photon")
        try:
            with closing(psycopg2.connect(dbname=database_name)) as connection:
                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute(query, parameters)
                        if fetch_all:
                            return cursor.fetchall()
                        return cursor.fetchone()
        except psycopg2.Error as error:
            raise PlayerDatabaseError(str(error)) from error

    # Read all saved players, in ID order.
    def get_players(self):
        return self._query(
            "SELECT id, codename FROM public.players ORDER BY id;",
            fetch_all=True,
        )

    # Look up one player's current codename by ID.
    def get_player(self, player_id):
        return self._query(
            "SELECT id, codename FROM public.players WHERE id = %s;",
            (player_id,),
        )

    # Save one new player and return the saved row.
    def add_player(self, player_id, codename):
        return self._query(
            """
            INSERT INTO public.players (id, codename)
            VALUES (%s, %s)
            RETURNING id, codename;
            """,
            (player_id, codename),
        )

    # Change a saved player's codename without changing their ID.
    def update_codename(self, player_id, codename):
        return self._query(
            "UPDATE public.players SET codename = %s WHERE id = %s RETURNING id, codename;",
            (codename, player_id),
        )

    # Clear names while preserving every saved player ID.
    def clear_codenames(self):
        return self._query(
            "UPDATE public.players SET codename = '' RETURNING id;",
            fetch_all=True,
        )

    # Delete one player and return the row that got deleted.
    def delete_player(self, player_id):
        return self._query(
            "DELETE FROM public.players WHERE id = %s RETURNING id, codename;",
            (player_id,),
        )