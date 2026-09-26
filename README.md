# Team 8 Laser Tag: VM Quick Start

## Software needed

- Debian Linux VM with a graphical desktop and Python 3.9 or newer.
- The existing PostgreSQL `photon` database and `public.players` table.
- VirtualBox Guest Additions for shared folders.
- GitHub access on the Windows host to download the project ZIP. Git is not needed inside the VM.

## One-time shared folder setup

1. Download the `Joshua` branch ZIP on the host computer into a folder you choose.
2. Shut down the VM for this one-time setup. In VirtualBox, open **Settings > Shared Folders**.
3. Add the host folder containing the ZIP. Name it `repo-share`; check **Auto-mount** and **Make Permanent**.
4. Start the VM. If the shared folder says permission denied, run this once and reboot:

```bash
sudo usermod -aG vboxsf student
sudo reboot
```

## Install and run

Paste this into the VM terminal. The shared folder is `/media/sf_repo-share`:

```bash
mkdir -p ~/laser-tag
cp /media/sf_repo-share/Team-8-Laser-Tag-Project-Joshua.zip ~/laser-tag/
python3 -m zipfile -e ~/laser-tag/Team-8-Laser-Tag-Project-Joshua.zip ~/laser-tag
cd ~/laser-tag/Team-8-Laser-Tag-Project-Joshua
bash setup_vm.sh
python3 main.py
```

`setup_vm.sh` checks for Pygame and the PostgreSQL Python driver. If missing, it installs Debian packages `python3-pygame` and `python3-psycopg2`. It does not install PostgreSQL or change its database or tables. The game defaults to the `photon` database, so no separate `psql` command or `PGDATABASE` setting is needed just to launch it.

If the downloaded ZIP does not contain `setup_vm.sh`, download a fresh ZIP after that script has been pushed to GitHub.

For later ZIP downloads, put the new ZIP in the same host folder. It appears in the VM's shared folder automatically; you do not need to shut down the VM again.

