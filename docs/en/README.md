<!-- (Automatically translated via ChatGPT.) -->

<p align='center'>
    <a href='..\..\README.md'>RU</a> • <b>EN</b> • <a href='..\zh\README.md'>ZH</a>
</p>
<p align='center'>
    <b>Main</b> • 
    <a href='settings.md'>Documentation</a> • <a href='how_it_works.md'>How does it work?</a> • <a href='qa.md'>Questions</a>
</p>

# Main Features
* Full text translation from `.xml` files of modifications (including comments).
* Automatic creation of `.loc2` files and addition to the mod.
* Selection of various translators (GoogleTranslate, DeepL, and API LLM models).
* Ability to translate modifications with text in multiple languages.
* Replacement of `.loc2` files for a specific language.

# Installation
To download the repository and run the script, you need:
* **Python** (download from [official website](https://www.python.org/downloads/));
* **git** (download from [official website](https://git-scm.com/downloads)).

1. Navigate to the folder where you want to install `DDMT`.
2. Clone the repository:
```bash
git clone %repository_link%
```
3. Create and activate a virtual environment:
```bash
python -m venv venv

source venv/bin/activate # On Linux
venv\Scripts\activate # On Windows
```
4. Install dependencies:
```bash
pip install -r requirements.txt
```

Optionally, for more convenient viewing of `.xml` files, you can install [Notepad++](https://notepad-plus-plus.org/downloads/) (it highlights syntax).

# Usage
This is an approximate plan of actions to translate a single mod.

1. Find the **mod folder** you want to translate.
   > **Example:** `G:\SteamLibrary\steamapps\workshop\content\262060\2200558948`

2. Copy the mod to the `mods` folder (local mods folder) in the Darkest Dungeon directory.
   > **Example path to local mods folder:** `G:\SteamLibrary\steamapps\common\DarkestDungeon\mods`
   >
   > **How to find the game folder:** Right-click the game icon in Steam > Manage > Browse local files

3. Check the number of `.xml` files in the `localization` folder. It’s recommended to keep only one `.xml` file for translation. If needed, you can merge translations from multiple `.xml` files.

4. Select the source language for translation and ensure all strings in the corresponding language tag in the `.xml` file match that language (for translation settings and language detection).

5. Copy the path to the mod folder you just copied.
   > **Example:** `G:\SteamLibrary\steamapps\common\DarkestDungeon\mods\2200558948`

6. Paste the mod path into the settings (specify the value for the `mod_folder_path` key).
7. Configure other parameters as desired.
8. Run the script file using Python:
```bash
python main.py
```
9. Wait until the message `"Translation completed!"` appears.