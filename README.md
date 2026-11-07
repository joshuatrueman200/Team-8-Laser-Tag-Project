# Team 8 Laser Tag

## Set up and run on Debian

Requirements:

- Debian with a graphical desktop, Python 3.9 or newer, and Git.
- The existing PostgreSQL `photon` database and `public.players` table.

Clone the GitHub repository and run the setup script:

```bash
sudo apt update
sudo apt install -y git
mkdir -p ~/laser-tag
cd ~/laser-tag
git clone https://github.com/joshuatrueman200/Team-8-Laser-Tag-Project.git
cd Team-8-Laser-Tag-Project
bash setup_vm.sh
```

`setup_vm.sh` checks for Pygame and the PostgreSQL Python driver, then installs Debian's `python3-pygame` and `python3-psycopg2` packages if needed. Your account may need `sudo` access. It does not create a virtual environment, install PostgreSQL, or create or change the database or tables.

Check that PostgreSQL is running and the expected player table is available:

```bash
pg_isready
psql -d photon -c "SELECT id, codename FROM public.players ORDER BY id;"
```

Run the game from the project directory:

```bash
python3 main.py
```

To disable music, run `python3 main.py --music_off`. To update an existing clone, run `git pull origin main` from the repository directory, then run `bash setup_vm.sh` to ensure the runtime dependencies are installed.

## View saved players

To print the saved player IDs and codenames from the VM terminal:

```bash
psql -d photon -c "SELECT id, codename FROM public.players ORDER BY id;"
```

## How to use the player entry screen

Each team has 15 rows. Every row has an ID box and a codename box. The yellow border marks the box that receives typing.

| Key                    | What it does                                                                      |
| ---------------------- | --------------------------------------------------------------------------------- |
| Digits                 | Type the player ID in the ID box                                                  |
| `Enter` (ID box)       | Look up the ID. If it exists, its codename appears; otherwise type a new codename |
| `Enter` (codename box) | Open the hardware ID popup; Enter there saves and transmits the equipment ID    |
| `Tab`                  | Switch between the ID box and the codename box                                    |
| `.` (dot)              | Switch between the red and green team                                             |
| `Up` / `Down`          | Move to another row of the current team                                           |
| `Del`                  | Delete the selected player from the database (asks `Y` / `N`)                     |
| `F5`                   | Start with at least one player on each team; begin play after the 30-second countdown |
| `F9`                   | Change the destination IP used for UDP transmissions                              |
| `F12`                  | Clear both team lists. Players stay saved in the database                         |

An ID that is already in a team cannot be added again. The screen shows "ID already in use". Player IDs and codenames are not reserved; enter whichever ID and name you want to use.

## UDP network (updated)

The game listens on `0.0.0.0:7501`, meaning **every IPv4 address on this VM**, regardless of which network you transmit to. The receiving address does not need to be edited and is no longer on the F9 screen.

Press **F9** on the player entry screen, edit **Transmit to IP**, then press **Enter** to save (**Esc** to cancel). By default, transmissions go to `127.0.0.1:7500` for a local test. Enter a different computer's IPv4 address or its network broadcast address (for example, `192.168.1.255`) to transmit over a network. Outgoing UDP broadcasts have `SO_BROADCAST` enabled. `0.0.0.0` is not a valid destination. The game no longer requires source and destination addresses to both be localhost or both be non-local.

After confirming a player's hardware ID, the game sends **that equipment/hardware ID** to the configured destination at port `7500`. PostgreSQL still stores the player's ID and codename; hardware IDs are kept in the current team roster. The same hardware ID cannot be used by two players in one game.

For remote testing, the VM's network adapter and firewalls must allow UDP between the computers. VirtualBox **Bridged Adapter** or an appropriately configured **Host-only Adapter** is often easier for LAN testing than NAT. The network you are using determines the correct broadcast address.

## Play Action and network events

Press **F5** with at least one fully registered player on each team to open the Play Action window. It shows a 30-second countdown, then sends start code `202` to the configured IP at port `7500` and starts the six-minute timer, shown in both the Play Action and player-entry windows. Pressing F5 again focuses the existing Play Action window.

The optional test traffic generator is `tools/python_trafficgenarator_v2.py`. It is **not started automatically** when the game launches; start it yourself in a second terminal if you want simulated hits. The generator needs two players on each team, each with a unique hardware ID, and sends to `127.0.0.1:7501` by default. Start the generator and enter those four hardware IDs before pressing F5 in the game; it waits for the game's `202` start code after the 30-second countdown. For real equipment or a separate sender, send UDP packets to port `7501` in the format `attacker_hardware_id:victim_hardware_id` (optionally followed by a NUL byte). The game matches hardware IDs to the current teams and recognizes base targets `43` and `53`:

```text
Opus --> BigFoot
Pal --> Opus
Opus --> Green Base
BigFoot --> Red Base
```

The left name is the shooter; the right name is the player tagged or base hit. Base labels default to **Green Base (43)** and **Red Base (53)**. If your hardware uses different base IDs, update `BASE_TARGETS` in `play_actions.py`. Hardware IDs `43` and `53` are reserved and cannot be assigned to players.

The Play Action window shows team and individual scores. An opposing-player hit earns the attacker 10 points; friendly fire costs both players 10 points; scoring an opposing base earns the attacker 100 points. The leading team's score flashes. Well-formed hit packets receive `201` on UDP port `7500` (two acknowledgments for friendly fire). When six minutes expire, the game sends `221` three times, freezes the Play Action display, and stops processing hit updates. Closing the Play Action window or pressing **Esc** in it also sends `221` three times if play has started.

To run the optional generator from the project directory:

```bash
python3 tools/python_trafficgenarator_v2.py
```

The generator is a separate, manually started process; launching `main.py` does not launch it.

## Team members

| GitHub username    | Real name           |
| ------------------ | ------------------- |
| `xXJ02HXx`         | Joshua Rivas        |
| `leduarcev17`      | Eduardo Arce Vargas |
| `ChillMark`        | Mark Freeman        |
| `ajd035776`        | Alex D'Agostino     |
| `JoshuaTrueman200` | Joshua Trueman      |
