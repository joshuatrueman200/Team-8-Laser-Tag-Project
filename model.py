import sqlite3
from pathlib import Path


class Player:
    def __init__(self, id, code_name, team):
        self.id = id
        self.code_name = code_name
        self.team = team


class Model:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection or sqlite3.connect(Path(__file__).with_name("players.db"))
        self.db_connection.executescript(Path(__file__).with_name("player.sql").read_text())
        self.clear_teams()

    def clear_teams(self):
        self.red_rows = [{"id": "", "codename": ""} for _ in range(15)]
        self.green_rows = [{"id": "", "codename": ""} for _ in range(15)]

    def check_ID_DB(self, id):
        row = self.db_connection.execute(
            "SELECT codename FROM player WHERE id = ?", (int(id),)
        ).fetchone()
        return row[0] if row else None

    def check_Codename_DB(self, codename):
        row = self.db_connection.execute(
            "SELECT id FROM player WHERE codename = ? COLLATE NOCASE", (codename,)
        ).fetchone()
        return row[0] if row else None

    def save_player(self, id, codename):
        with self.db_connection:
            self.db_connection.execute(
                "INSERT INTO player (id, codename) VALUES (?, ?) "
                "ON CONFLICT(id) DO UPDATE SET codename = excluded.codename",
                (int(id), codename.strip()),
            )

    def close(self):
        self.db_connection.close()
