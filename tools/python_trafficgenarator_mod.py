"""Simulate live Photon Laser Tag hits over UDP (ports 7501 -> 7500).

Event distribution defaults to 70% opposing-team hits, 20% friendly fire,
10% base hits. Base hits can occur repeatedly from ANY player on either team.
"""

import random
import socket
import time

BUFFER_SIZE = 1024
SERVER_ADDRESS_PORT = ("0.0.0.0", 7500)
CLIENT_ADDRESS_PORT = ("127.0.0.1", 7501)
BASE_IDS = {"43", "53"}
CONTROL_CODES = {"201", "202", "221"}


def choose_hit(red_players, green_players, rng=random):
    """Return (packet, is_friendly_fire), choosing a new event each time."""
    teams = {"red": red_players, "green": green_players}
    if not red_players or not green_players:
        raise ValueError("Both teams must have at least one equipment ID")

    event_type = rng.choices(
        ["opponent", "friendly", "base"], weights=[70, 20, 10], k=1
    )[0]
    # Friendly fire requires two distinct people on the same team.
    friendly_teams = [team for team, players in teams.items() if len(players) >= 2]
    if event_type == "friendly" and friendly_teams:
        team = rng.choice(friendly_teams)
        attacker, victim = rng.sample(teams[team], 2)
        return f"{attacker}:{victim}", True

    attacker_team = rng.choice(["red", "green"])
    attacker = rng.choice(teams[attacker_team])
    if event_type == "base":
        # Red shoots green base 43; green shoots red base 53.
        enemy_base = "43" if attacker_team == "red" else "53"
        return f"{attacker}:{enemy_base}", False

    other_team = "green" if attacker_team == "red" else "red"
    victim = rng.choice(teams[other_team])
    return f"{attacker}:{victim}", False


def receive_feedback(sock, expected_acks):
    """Wait for 201 ACKs, ignoring raw equipment shutdown transmissions.

    Returns False if game software sends 221 to stop the game.
    """
    while expected_acks:
        data, _ = sock.recvfrom(BUFFER_SIZE)
        message = data.decode("utf-8").rstrip("\x00")
        if message == "221":
            print("Game stop received (221)")
            return False
        if message == "201":
            expected_acks -= 1
            print("Received hit ACK: 201")
        elif message.isdecimal() and message not in CONTROL_CODES:
            print(f"Received equipment shutdown ID: {message}")
        else:
            print(f"Ignoring unrelated UDP message: {message!r}")
    return True


def ask_extra_equipment(team):
    value = input(f"Additional {team} equipment IDs (comma-separated, or Enter): ").strip()
    return [item.strip() for item in value.split(",") if item.strip()]


def main():
    print("This program generates opposing hits, random friendly fire, and base hits.")
    print("Use the equipment IDs entered on the game's player entry screen.")
    red_players = [
        input("Enter equipment id of red player 1 ==> ").strip(),
        input("Enter equipment id of red player 2 ==> ").strip(),
    ]
    green_players = [
        input("Enter equipment id of green player 1 ==> ").strip(),
        input("Enter equipment id of green player 2 ==> ").strip(),
    ]
    red_players += ask_extra_equipment("red")
    green_players += ask_extra_equipment("green")

    all_ids = red_players + green_players
    if any(not code.isdecimal() or code in BASE_IDS | CONTROL_CODES for code in all_ids):
        raise ValueError("Equipment IDs must be numeric and not 43, 53, 201, 202 or 221")
    if len(all_ids) != len(set(all_ids)):
        raise ValueError("Each player must have a distinct equipment ID")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver, \
         socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as transmitter:
        receiver.bind(SERVER_ADDRESS_PORT)
        print("Waiting for game start (202) from game software...")
        while True:
            message = receiver.recvfrom(BUFFER_SIZE)[0].decode("utf-8").rstrip("\x00")
            if message == "202":
                break
            # Player entry sends one raw ID per player to turn their equipment on.
            if message.isdecimal() and message not in CONTROL_CODES:
                print(f"Received equipment activation ID: {message}")
            else:
                print(f"Ignoring while waiting for start: {message!r}")

        print("Game started. Sending events... (Ctrl+C to quit)")
        try:
            while True:
                event, friendly_fire = choose_hit(red_players, green_players)
                print(f"Transmitting {'FRIENDLY FIRE' if friendly_fire else 'hit'}: {event}")
                transmitter.sendto((event + "\0").encode("utf-8"), CLIENT_ADDRESS_PORT)
                if not receive_feedback(receiver, 2 if friendly_fire else 1):
                    break
                time.sleep(random.randint(1, 3))
        except KeyboardInterrupt:
            print("Traffic generator interrupted")
    print("Program complete")


if __name__ == "__main__":
    main()
