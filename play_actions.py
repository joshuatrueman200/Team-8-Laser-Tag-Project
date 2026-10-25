"""Convert hardware hit events into player and base names (no graphics dependencies)."""

from dataclasses import dataclass


# The traffic generator sends red players to 43 and green players to 53.
# Treat those as the opposing teams' bases, not equipment belonging to players.
# Change the labels here if the actual equipment uses different base names.
BASE_TARGETS = {
    "43": "Green Base",
    "53": "Red Base",
}


@dataclass(frozen=True)
class Hit:
    attacker: str
    target: str
    friendly_fire: bool
    base_hit: bool = False

    @property
    def label(self):
        return f"{self.attacker} --> {self.target}"


def roster_by_hardware(model):
    """Use the hardware IDs entered for THIS game, not the database player IDs."""
    players = {}
    for team, rows in (("red", model.red_rows), ("green", model.green_rows)):
        for row in rows:
            if row["id"] and row["hardware_id"] and row["codename"]:
                players[row["hardware_id"]] = (row["codename"], team)
    return players


def decode_hit(packet, players):
    """Parse generator packets: attacker_hardware_id:victim_hardware_id + NUL."""
    try:
        payload = packet.decode("utf-8").rstrip("\x00")
    except UnicodeDecodeError:
        return None
    parts = payload.split(":")
    if len(parts) != 2 or not all(part.isdecimal() for part in parts):
        return None
    attacker = players.get(parts[0])
    if attacker is None:
        # Never show unrecognized shooter hardware IDs.
        return None

    if parts[1] in BASE_TARGETS:
        # Base hits display a readable name and get a single 201 acknowledgment.
        return Hit(attacker[0], BASE_TARGETS[parts[1]], False, base_hit=True)

    target = players.get(parts[1])
    if target is None:
        return None
    return Hit(attacker[0], target[0], attacker[1] == target[1])
