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

You should see `Team-8-Laser-Tag-Project-Joshua.zip` in the output.

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
cp /media/sf_FolderName/Team-8-Laser-Tag-Project-Joshua.zip ~/laser-tag/
python3 -m zipfile -e ~/laser-tag/Team-8-Laser-Tag-Project-Joshua.zip ~/laser-tag
cd ~/laser-tag/Team-8-Laser-Tag-Project-Joshua
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
| `Enter` (codename box) | Save the player to the database, add them to the team, and send the UDP message   |
| `Tab`                  | Switch between the ID box and the codename box                                    |
| `.` (dot)              | Switch between the red and green team                                             |
| `Up` / `Down`          | Move to another row of the current team                                           |
| `Del`                  | Delete the selected player from the database (asks `Y` / `N`)                     |
| `F5`                   | Start the game screen                                                             |
| `F9`                   | Open the UDP network settings                                                     |
| `F12`                  | Clear both team lists. Players stay saved in the database                         |

An ID that is already in a team cannot be added again. The screen shows "ID already in use". Player 1 (`Opus`) is always created in the database if it is missing.

## UDP network

After a player is saved, the game sends that player's ID as text to port `7500` of the destination IP. The default source and destination are both `127.0.0.1`. The game also listens on port `7501` and prints anything it receives.

To use a different network, press `F9` on the player entry screen:

- `Tab` switches between the **Source IP** and **Destination/Broadcast IP** fields.
- `Enter` saves the change and `Esc` cancels.
- Source and destination must both be `127.x.x.x`, or both be non-local addresses.

## Team members

| GitHub username    | Real name           |
| ------------------ | ------------------- |
| `xXJ02HXx`         | Joshua Rivas        |
| `leduarcev17`      | Eduardo Arce Vargas |
| `ChillMark`        | Mark Freeman        |
| `ajd035776`        | Alex D'Agostino     |
| `JoshuaTrueman200` | Joshua Trueman      |
