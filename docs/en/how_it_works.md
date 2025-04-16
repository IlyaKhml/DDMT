<!-- (Automatically translated via ChatGPT.) -->

<p align='center'>
    <a href='..\ru\how_it_works.md'>RU</a> • <b>EN</b> • <a href='..\zh\how_it_works.md'>ZH</a>
</p>
<p align='center'>
    <a href='README.md'>Main</a> • 
    <a href='settings.md'>Documentation</a> • <b>How does it work?</b> • <a href='qa.md'>Questions</a>
    <b></b>
</p>

# Explanation of Localization Files and Manual Translation
## Basics
First, ensure the mod has localization files (text displayed in the game). Check for a `localization` folder in the mod’s directory. If it contains `.loc2` and `.xml` files, the mod can be fully or partially translated into your language.

| File:   | Functions:                                                                                               | Guarantees:                                                             |
| ------- | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `.loc2` | Encoded text for the game, which cannot be translated directly.                                          | ✔️ Partial translation (Replaces blue text with the existing language)  |
| `.xml`  | Text strings used to create `.loc2` files. Text can be translated into other languages.                  | ✔️ Full mod translation                                                |

## File Naming
This information is mainly for those who want to translate manually.
> **Localization files have specific parts that should not be altered!**

| File:   | Example Name:             | Explanation:                                                                                                                                                                                                                   |
| ------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.loc2` | `2200558948_english.loc2` | The file name is automatically set by `localization.exe`.                                                                                                                                                                     |
| `.xml`  | `test.string_table.xml`   | `test` - Arbitrary name, not significant.<br>`.string_table` - Indicates that this file contains strings for translation to create `.loc2` files via `localization.exe` (without it, `.xml` files won’t be detected for translation). |

## Creating a Translation
Start by selecting the language for translation. Typically, there is one `.xml` file containing all languages, but some modders create separate `.xml` files for each language. In such cases, you can create a new translation file, copy an existing `.xml`, or add a new language tag to an existing `.xml`:
`<language id=[Language supported by the game]> </language>`.

Then, translate all strings into your desired language and save the file.

## Converting `.xml` to `.loc2`
The `localization.exe` file, located in the `_windows` folder of the game, is used for conversion.

Example path to the file:
`G:\SteamLibrary\steamapps\common\DarkestDungeon\_windows\localization.exe`

To convert `.xml`, place `localization.exe` and several other files from the `_windows` folder (listed below) into the mod’s `localization` folder.

> The folder must be named exactly `localization`, or `localization.exe` will not work correctly.

The folder should contain the following files:
* `One or more .xml files for creating .loc2`
* `localization.exe`
* `fmod.dll`
* `fmodstudio.dll`
* `glew32.dll`
* `SDL2.dll`
* `steam_api.dll`

Next, run `localization.exe`, which will create the `.loc2` localization files for the game.

## Adding Paths to `modfiles.txt`
The `.loc2` files are created, but the game needs to know which mod files to load. This is handled by `modfiles.txt`, located in the mod’s root folder.

It specifies the relative path to the file (relative to the mod folder) and the file size in bytes:
`project.xml 4585`

The file size is likely used by the Steam Workshop to determine which mod files need to be re-downloaded if corrupted.

Add references to the new `.loc2` files and their sizes, for example:
`localization/2200558948_russian.loc2 20232`
`localization/2200558948_english.loc2 20254`

## Editing `project.xml`
The final step is to modify the mod’s name in the `project.xml` file (located in the mod’s root folder) to distinguish it from the original.

Find the `<Title>` tag containing the mod’s name and update it:

`<Title>Lilith class</Title>` -> `<Title>Lilith class Translated</Title>`

---
Done!

The mod should now be translated into your language and available for selection in the game.