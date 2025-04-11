```
                  ________                             ______     _           __         
                 / ____/ /_  ____ __________ ____     / ____/____(_)___  ____/ /__  _____
                / /   / __ \/ __ `/ ___/ __ `/ _ \   / / __/ ___/ / __ \/ __  / _ \/ ___/
               / /___/ / / / /_/ / /  / /_/ /  __/  / /_/ / /  / / / / / /_/ /  __/ /    
               \____/_/ /_/\__,_/_/   \__, /\___/   \____/_/  /_/_/ /_/\__,_/\___/_/     
                                     /____/
```

# ChargeGrinder
**ChargeGrinder** is a Limbus Company bot that charges through MD5 for you


**Automated Mirror Dungeon Runs:** Only the number of dungeons to grind needs to be specified, everything else is handled by the bot.

<span style="font-size: 110%;">**Speed:** </span> Usually each floor takes no more than 5 minutes, so 1 MD5 run lasts between **20-25 minutes.**

---
### Usage:
- **User Input:** The program will prompt you to enter the number of Mirror Dungeons to grind, and it will start running a few seconds after your response (You must switch to Limbus Company window, main screen). It is not recommended to move mouse while bot is running, but you can Alt+Tab to new window for bot to pause (or crash, depends on the odds).
- **In-Game Requirements:** 
    - You must leave the Limbus Company window open and in fullscreen mode while the bot runs. Mouse interactions in the game will be controlled by the bot.
    - If you close the Limbus Company window, the bot will automatically pause.
- **The bot:**
    - Uses default (burn) team
    - Avoids a few Booster Packs with long fights
    - Tries to find the best next node (minimizing time)
    - Selects Burn Ego gifts and tries to fuse an overpowered burn build in shops
    - Winrates focused encounters and chains skills 1 and 2 for human encounters (Skill 3 animations are too long)
- **Limitations:** ChargeGrinder still needs additional features, testing, and bug fixes. However, it can successfully grind a few easy dungeons while you are sleeping.

--- 

### Requirements  
#### Option 1: Run the Prebuilt Executable  
Simply launch **CGrinder.exe** from the `dist` folder—no additional files required.  

#### Option 2: Run with Python  
Ensure you have **Python 3** installed and the following dependencies:  
```bash
pip install numpy opencv-python-headless pyscreeze pyautogui Pillow torchfree-ocr
```
Or manually install:  
- `numpy`  
- `opencv-python-headless`  
- `pyscreeze`  
- `pyautogui`  
- `Pillow`  
- `torchfree-ocr`  

### Setup Instructions:

1. **Team Setup:** 
   - ChargeGrinder is currently tested with an Uptie 4 burn team (the fastest team for easy MD)
   - Team members: Don, Ishmael, Gregor, Sinclair, YiSang and Rodion
# ![team.png](team.png)
   - The team is inspired by this MD5 speedrun: 
# [![Watch on YouTube](https://img.youtube.com/vi/dCUUHMLDWkY/0.jpg)](https://www.youtube.com/watch?v=dCUUHMLDWkY)

2. **Game Settings:**
   - Set the game resolution to Full HD (1920 x 1080) in fullscreen mode.
   - Pre-select your burn team (members should also be pre-selected)
   - Start Bot.py in project folder, input number and immediately switch to Limbus window on the main game screen.
   - if you have multiple languages in keyboard layout, make sure you have ENG selected before starting the bot

3. **Recommended Team:** 
   - Currently, only burn team is tested.
   - Ensure the team and all 6 sinners are selected before starting the bot. The game usually remembers previously used sinners.

---

### TODO List:
- Add support for different team builds??? idk why though if burn is the fastest
- Implement more natural mouse movements for the bot? game doesn't really track mouse movements though
- Improve abnormality fights (coin targeting instead of winrate, may be useful for Hard MD bot)
- Create a bot UI using PyQt6