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

## View players

```bash
psql -P pager=off -d photon -c "SELECT id, codename FROM public.players ORDER BY id;"
```

## Player entry controls

Each team has 15 rows with a player ID and codename field. The yellow border marks the selected field. For example:

```text
RED TEAM                    GREEN TEAM
[ID] CODENAME               ID  CODENAME
 12   Opus                  24  BigFoot
```

| Key | Action |
| --- | --- |
| Digits | Type the player ID in the selected ID field. |
| `Enter` (ID field) | Look up the ID. If it is saved, its codename appears; otherwise, enter a new codename. |
| `Tab` | Switch between the ID and codename fields. |
| `Enter` (codename field) | Open the hardware ID prompt. Enter the equipment ID and press `Enter` to save the player. |
| `.` | Switch between the red and green teams. |
| `Up` / `Down` | Move to another row on the current team. |
| `Del` | Delete the selected saved player. Press `Y` to confirm or `N` to cancel. |
| `F5` | Start the game when each team has at least one player. |
| `F6` | After the game ends, close Play Action and return to player entry. |
| `F9` | Change the UDP destination IP. |
| `F12` | Clear both team lists. Saved players remain in the database. |

Player IDs cannot be duplicated in the teams. Player IDs and codenames can be chosen freely.

## Test traffic generator

Start it separately from the project directory:

```bash
python3 tools/python_trafficgenarator_v2.py
```

## Team members

| GitHub username | Name |
| --- | --- |
| `xXJ02HXx` | Joshua Rivas |
| `leduarcev17` | Eduardo Arce Vargas |
| `ChillMark` | Mark Freeman |
| `ajd035776` | Alex D'Agostino |
| `JoshuaTrueman200` | Joshua Trueman |
