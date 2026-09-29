# Team 8 Laser Tag System

## Project Description

This project is a laser tag system that allows users to enter players, assign them to Red or Green teams, and communicate with laser tag equipment using UDP networking.

The system includes:

* Splash screen
* Player ID and codename entry
* Red and Green teams with up to 15 players each
* UDP communication for equipment codes
* Configurable UDP source and destination IP addresses
* Game screen
* Optional background music

## Contributors

* "joshuatrueman200" - Joshua Trueman
* "xXJ02HXx" - Joshua Rivas
* "leduarcev17" - Eduardo Arce Vargas
* "ChillMark" - Mark Freeman
* "ajd035776" - Alex D'Agostino

## Requirements

* Python3
* Pygame


This runs off the assumption that the files is on the virtual machine somehow (We used a shared folder) and is in the home folder wherever you like.

Open a terminal in the project folder containing `main.py` and
`requirements.txt`.

1. Install virtual environment support:

   ```bash
   sudo apt update
   sudo apt install python3-venv
   ```

2. Create the virtual environment in your home folder:

   ```bash
   python3 -m venv ~/laser-tag-venv
   ```


3. Activate the environment:

   ```bash
   source ~/laser-tag-venv/bin/activate
   ```

4. Install the project dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

## Run the Game

From the project folder, activate the environment and start the game:

```bash
source ~/laser-tag-venv/bin/activate
python main.py
```

To run without music:

```bash
python main.py --music_off
```

Activate the environment whenever you open a new terminal.
The setup and dependency installation steps only need to be completed
once unless you recreate the environment or update the dependencies.

To exit the virtual environment:

```bash
deactivate
```

Make sure the `Asset` folder is in the project directory and contains:

```text
Asset/
├── logo.jpg
└── photon_tracks_Track01.mp3
```

## Controls

 Key     |   Function                      
 --------------------------------------
* `ENTER` - Confirm Player ID or Codename 
* `.`     - Switch teams                  
* `F5`    - Start game                    
* `F9`    - Open UDP network settings     
* `F12`   - Clear player entries          
* `TAB`   - Switch network field          
* `ESC`   - Cancel network settings       

## UDP Networking

The program uses UDP to send equipment codes.

Port   |  Purpose             
----------------------------
`7500` - Send equipment codes 
`7501` - Receive UDP messages 

The default network settings are:

```text
Source:      127.0.0.1
Destination: 127.0.0.1
```

Press `F9` to change the source and destination IP addresses.

For local testing, use:

```text
127.0.0.1 -> 127.0.0.1
```

## Project Files

File               |  Purpose                              
------------------  ------------------------------------
* `main.py`          - Starts and runs the program          
* `controller.py`    - Handles user input and program logic 
* `model.py`         - Stores player information           
* `view.py`          - Displays the graphical interface     
* `udp_manager.py`   - Handles UDP communication            
* `player.sql`       - SQLite player table schema
* `players.db`       - Player database created automatically on first run
* `requirements.txt` - Install script for required libraries    
* `.gitignore`       - Ignores Python cache files           

## Current Status

The project currently supports player entry, team selection, UDP equipment-code transmission, network configuration, and the basic game screen.

Player IDs and codenames are saved in `players.db` when the codename is confirmed. Entering a returning player's ID fills in the saved codename; press ENTER again to add them to the team and send their equipment code. Entering a new codename for an existing ID updates its saved name. Player IDs cannot appear twice on the teams, and a codename already assigned to another ID is rejected. F12 clears the current teams but keeps saved players for later games. The full laser tag game functionality is still being developed.
