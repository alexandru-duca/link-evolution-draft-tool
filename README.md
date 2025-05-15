# Link Evolution Draft Tool

This tool is intended to be used with [Yu-Gi-Oh! Legacy of the Duelist : Link Evolution](https://store.steampowered.com/app/1150640/YuGiOh_Legacy_of_the_Duelist__Link_Evolution/) (not [Yu-Gi-Oh! Legacy of the Duelist](https://store.steampowered.com/app/480650/YuGiOh_Legacy_of_the_Duelist/)). Its purpose is to make the game's deck builder only feature cards from your `.ydk` files, e.g. cards drafted with the [Yu-Gi-Oh! Pack Simulator](https://ygoprodeck.com/pack-sim/).

**This tool will erase your game progress! All your cards will be replaced with the content of your `.ydk` files!**

Two additional Python scripts are provided to establish an environment suitable for drafting:
- `remove-initial-decks.py`: Cards from starter decks are always available in the deck builder. This script removes all starter decks.
- `remove-banlist.py`: The game has a ["custom Forbidden and Limited list"](https://yugipedia.com/wiki/Yu-Gi-Oh!_Legacy_of_the_Duelist:_Link_Evolution#Cards). This script removes the banlist.

# Preliminaries

- Buy [Yu-Gi-Oh! Legacy of the Duelist : Link Evolution](https://store.steampowered.com/app/1150640/YuGiOh_Legacy_of_the_Duelist__Link_Evolution/) on [Steam](https://store.steampowered.com/about/) and start the game at least once.
- Install the newest version of [Python](https://www.python.org/downloads/).

# Use

1. Run `remove-initial-decks.py` and `remove-banlist.py` in the folder of the game's executable (`YuGiOh.exe`). You can find this folder by right-clicking the game in your Steam library and selecting "Manage > Browse local files".

2. Move `draft-tool.py` and `passcode.csv` into the folder of the game's save file (`savegame.dat`).

    - Windows: `\path\to\steam\userdata\<User-ID>\1150640\remote`
    - Debian: `~/.steam/debian-installation/userdata/<User-ID>/1150640/remote`
      
    In it, create a new folder named `draft` containing your `.ydk` files. Finally, run `draft-tool.py`.
