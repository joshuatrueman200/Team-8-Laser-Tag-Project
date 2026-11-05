"""Generate simulated tag events for the local laser-tag game."""

import json
import random
import socket
import time


BUFFER_SIZE = 1024
MAX_TEAM_SIZE = 15
RESERVED_IDS = {"43", "53"}
SERVER_ADDRESS = ("0.0.0.0", 7500)
CLIENT_ADDRESS = ("127.0.0.1", 7501)
ROSTER_REQUEST = b"ROSTER?"
ROSTER_ATTEMPTS = 5


def parse_roster_response(data):
    try:
        roster = json.loads(data.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("The game returned an invalid roster response.") from error

    if not isinstance(roster, dict):
        raise ValueError("The game returned an invalid roster response.")

    players = {}
    seen_ids = set()
    for team in ("red", "green"):
        team_ids = roster.get(team)
        if not isinstance(team_ids, list) or not all(
            isinstance(player_id, str)
            and player_id.isdecimal()
            and player_id not in RESERVED_IDS
            for player_id in team_ids
        ):
            raise ValueError(f"The game returned invalid {team} hardware IDs.")
        if seen_ids.intersection(team_ids):
            raise ValueError("The game returned duplicate player hardware IDs.")
        seen_ids.update(team_ids)
        players[team] = team_ids

    if not players["red"] or not players["green"]:
        raise ValueError("Add at least one player to each team before testing.")
    if any(len(team_ids) > MAX_TEAM_SIZE for team_ids in players.values()):
        raise ValueError(f"The game supports up to {MAX_TEAM_SIZE} players per team.")
    return players["red"], players["green"]


def fetch_roster(receive_socket, attempts=ROSTER_ATTEMPTS):
    receive_socket.settimeout(2)
    try:
        for attempt in range(attempts):
            receive_socket.sendto(ROSTER_REQUEST, CLIENT_ADDRESS)
            try:
                data, _ = receive_socket.recvfrom(BUFFER_SIZE)
            except socket.timeout:
                if attempt + 1 == attempts:
                    raise RuntimeError(
                        "Could not read the roster. Start the game and register "
                        "players on both teams, then try again."
                    )
                continue
            return parse_roster_response(data)
        raise RuntimeError("Could not read the roster from the game.")
    finally:
        receive_socket.settimeout(None)


def create_test_event(red_players, green_players, counter):
    """Return one simulated packet and whether it is friendly fire."""
    if counter == 5:
        teams_with_multiple_players = [
            players for players in (red_players, green_players)
            if len(players) > 1
        ]
        if teams_with_multiple_players:
            team = random.choice(teams_with_multiple_players)
            attacker = random.choice(team)
            target = random.choice([player for player in team if player != attacker])
            return f"{attacker}:{target}", True

    if counter == 10:
        return f"{random.choice(red_players)}:43", False
    if counter == 20:
        return f"{random.choice(green_players)}:53", False

    red_player = random.choice(red_players)
    green_player = random.choice(green_players)
    if random.choice((True, False)):
        return f"{red_player}:{green_player}", False
    return f"{green_player}:{red_player}", False


def main():
    print("This program generates test tag traffic for the game.")

    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    transmit_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        receive_socket.bind(SERVER_ADDRESS)
        try:
            red_players, green_players = fetch_roster(receive_socket)
        except (RuntimeError, ValueError) as error:
            print(f"Could not get player hardware IDs: {error}")
            return
        print(f"Loaded {len(red_players)} red and {len(green_players)} green players.")
        print("\nWaiting for start from game_software")

        while True:
            received_data, _ = receive_socket.recvfrom(BUFFER_SIZE)
            received_data = received_data.decode("utf-8").rstrip("\0")
            print(f"Received from game software: {received_data}")
            if received_data == "202":
                break

        counter = 0
        while True:
            message, friendly_fire = create_test_event(
                red_players, green_players, counter
            )
            print(f"\nTransmitting to game: {message}")
            transmit_socket.sendto(
                (message + "\0").encode("utf-8"), CLIENT_ADDRESS
            )

            received_data, _ = receive_socket.recvfrom(BUFFER_SIZE)
            received_data = received_data.decode("utf-8").rstrip("\0")
            print(f"Received from game software: {received_data}")

            if friendly_fire:
                received_data, _ = receive_socket.recvfrom(BUFFER_SIZE)
                received_data = received_data.decode("utf-8").rstrip("\0")
                print(f"Received second friendly-fire reply: {received_data}")

            if received_data == "221":
                break
            counter += 1
            time.sleep(random.randint(1, 3))

        print("Program complete")
    finally:
        receive_socket.close()
        transmit_socket.close()


if __name__ == "__main__":
    main()
