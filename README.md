# link-evolution-draft-tool
Link Evolution Draft Tool

This tool is intended to be used with "Yu-Gi-Oh! Legacy of the Duelist : Link Evolution".
It's purpose is to enable deckbuilding after a completed draft, by making only cards from a set of `.ydk` files available in the in-game deck-builder.

# Preliminaries

You need Python 3.10 or higher installed. Also you need to have the game installed. Explanations bellow assume that you installed it through steam.

# Use

To use the tool follow these steps:

- Execute `remove-starter-decks-and-banlist.py` in the folder where the games  executable is located. 
  You can find this in steam by right-clicking the game and selecting "Manage > Browse local files".

- Copy `draft-tool.py` and `passcode.csv` to the location of your save file.
  
  Under Windows this usually is:
  ```
  \path\to\steam\userdata\<User-ID>\1150640\remote
  ```
  Under Linux it may depend on your distribution, using Debian it is:
  ```
  ~/.steam/debian-installation/userdata/<User-ID>/1150640/remote
  ```
  Next create a directory `draft` there and place your `.ydk` files into it.
  Finally execute `draft-tool.py`.