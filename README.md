# Team 8 Laser Tag: VM Quick Start

## Before you start

- Debian Linux VM with a graphical desktop and Python 3.9 or newer.
- VirtualBox Guest Additions, for shared folders.
- The existing PostgreSQL `photon` database and `public.players` table.
- GitHub access on the Windows host. Git is not needed inside the VM.

The VM account is `student` with password `student`.

## Set up the shared folder once

1. On the Windows host, download the `main` branch ZIP into a folder you can find.
2. Shut down the VM. In VirtualBox, open **Settings > Shared Folders** and add the Windows folder that contains the ZIP.
3. In the **Name** field, enter a simple name such as `FolderName`. Check **Auto-mount** and **Make Permanent**.

   **Remember the Name exactly.** The Windows folder path is selected in VirtualBox; you do not type that path in the VM. In the VM, a share named `FolderName` appears at `/media/sf_FolderName`. For example, if you named yours `VMzip`, its VM path is `/media/sf_VMzip`.

4. Start the VM. In the VM terminal, check that the share and ZIP are visible. Replace `FolderName` with the Name you chose in VirtualBox:

```bash
ls -lh /media/sf_FolderName
```

You should see `Team-8-Laser-Tag-Project-main.zip` in the output.

### If you see "Permission denied"

Run this once in the VM terminal:

```bash
sudo usermod -aG vboxsf student
```

When prompted, enter the VM account password `student` manually; the characters will not appear as you type. The password prompt cannot be safely automated here. Then log out of the VM desktop and log back in (or reboot) so the new group membership takes effect. Try the `ls` check again. If the `vboxsf` group does not exist, VirtualBox Guest Additions may not be installed or running.

## Extract, install, and run

In the commands below, replace `FolderName` with the exact VirtualBox **Name** you remembered above. For your share named `VMzip`, use `/media/sf_VMzip`.

Run these commands in the VM terminal, one at a time:

```bash
mkdir -p ~/laser-tag
cp /media/sf_FolderName/Team-8-Laser-Tag-Project-main.zip ~/laser-tag/
python3 -m zipfile -e ~/laser-tag/Team-8-Laser-Tag-Project-main.zip ~/laser-tag
cd ~/laser-tag/Team-8-Laser-Tag-Project-main
bash setup_vm.sh
python3 main.py
```

`setup_vm.sh` checks for Pygame and the PostgreSQL Python driver. If either is missing, it installs Debian packages `python3-pygame` and `python3-psycopg2`; your VM account may need `sudo` access. The script does not install PostgreSQL or change its database or tables. The game uses the existing `photon` database by default.

## View saved players

To print the saved player IDs and codenames from the VM terminal:

```bash
psql -d photon -c "SELECT id, codename FROM public.players ORDER BY id;"
```

## Later ZIP downloads

Put the new ZIP in the same Windows folder. It will appear in the VM shared folder automatically; you do not need to shut down the VM again.

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
| `F5`                   | Open a second Play Action window and send `202` to start the traffic generator     |
| `F9`                   | Change the destination IP used for UDP transmissions                              |
| `F12`                  | Clear both team lists. Players stay saved in the database                         |

An ID that is already in a team cannot be added again. The screen shows "ID already in use". Player 1 (`Opus`) is always created in the database if it is missing.

## UDP network (updated)

The game listens on `0.0.0.0:7501`, meaning **every IPv4 address on this VM**, regardless of which network you transmit to. The receiving address does not need to be edited and is no longer on the F9 screen.

Press **F9** on the player entry screen, edit **Transmit to IP**, then press **Enter** to save (**Esc** to cancel). By default, transmissions go to `127.0.0.1:7500` for a local test. Enter a different computer's IPv4 address or its network broadcast address (for example, `192.168.1.255`) to transmit over a network. Outgoing UDP broadcasts have `SO_BROADCAST` enabled. `0.0.0.0` is not a valid destination. The game no longer requires source and destination addresses to both be localhost or both be non-local.

After confirming a player's hardware ID, the game sends **that equipment/hardware ID** to the configured destination at port `7500`. PostgreSQL still stores the player's ID and codename; hardware IDs are kept in the current team roster. The same hardware ID cannot be used by two players in one game.

For remote testing, the VM's network adapter and firewalls must allow UDP between the computers. VirtualBox **Bridged Adapter** or an appropriately configured **Host-only Adapter** is often easier for LAN testing than NAT. The network you are using determines the correct broadcast address.

## Play Action window and traffic generator

The play-action feature uses the new `play_action_display.py` and `play_actions.py` files. Press **F5** after registering players to open a **second** Pygame window; the original player-entry window stays open. F5 sends the traffic generator's required start code (`202`) to the configured IP at port `7500`. The game continues listening on UDP port `7501` while both windows are open.

Packets from the traffic generator have the format `attacker_hardware_id:victim_hardware_id` (with an optional trailing NUL byte). The game looks up player hardware IDs in the **current teams** and shows their codenames. It also recognizes base target IDs `43` and `53` and shows named bases instead of raw IDs:

```text
Opus --> BigFoot
Pal --> Opus
Opus --> Green Base
BigFoot --> Red Base
```

The left name is the shooter; the right name is the player tagged or base hit. The supplied generator sends red-player hits to base `43` and green-player hits to base `53`, so the labels default to **Green Base (43)** and **Red Base (53)**. If your actual hardware assigns those colors differently, change `BASE_TARGETS` in `play_actions.py`. Hardware IDs `43` and `53` are reserved for bases and cannot be assigned to players.

Friendly fire is included. Packets with unrecognized shooter/target hardware IDs are not displayed. All well-formed generator events get a `201` reply on UDP port `7500`; a same-team player hit gets the **two replies** expected by the provided generator, while a base hit gets one. Closing the additional window or pressing **Esc** while focused on it sends `221` to stop the generator. The main roster window stays open.

### Run the supplied traffic generator

1. Launch the game from the project directory with `python3 main.py` (or `python3 main.py --music_off`). Register at least **two red players and two green players**, giving each a unique hardware ID.
2. In another terminal on the same machine, run `python3 tools/python_trafficgenarator_v2.py`. Enter the **hardware IDs** from those four roster entries, in red1, red2, green1, green2 order. If the generator is running elsewhere, set F9 to that machine's IP/broadcast address and update `clientAddressPort` in the generator to the game VM's reachable IP.
3. Wait for the generator to print `waiting for start from game_software`. Then press **F5** in the game. The new window shows the countdown images for 30 seconds, followed by the live tag feed.
4. Close the Play Action window to end the generator session. The game itself remains open.

### Countdown integration

The teammate's `game_timer.py` and `countdown_images/countdown0.jpg` through `countdown30.jpg` are now integrated **inside the second Play Action window**. When F5 is pressed, that window shows the 30-second sequence, then the usual live tag list. The main player-entry window is not replaced.

As before, F5 immediately sends the traffic generator's `202` start message; any UDP hits arriving during the countdown are acknowledged right away and saved for display once the images finish. This keeps the existing traffic-generator handshake unchanged. Closing the Play Action window sends `221` to stop it. The teammate's extra `alert.jpg` and `countdown.jpg` assets are included unchanged, although the original countdown implementation does not use them.

To run the protocol / parsing tests (no PostgreSQL or Pygame needed):

```bash
python3 -m unittest -v test_play_actions.py
```

## Team members

| GitHub username    | Real name           |
| ------------------ | ------------------- |
| `xXJ02HXx`         | Joshua Rivas        |
| `leduarcev17`      | Eduardo Arce Vargas |
| `ChillMark`        | Mark Freeman        |
| `ajd035776`        | Alex D'Agostino     |
| `JoshuaTrueman200` | Joshua Trueman      |
