<!-- (Automatically translated via ChatGPT.) -->

<p align='center'>
    <a href='..\ru\qa.md'>RU</a> • <b>EN</b> • <a href='..\zh\qa.md'>ZH</a>
</p>
<p align='center'>
    <a href='README.md'>Main</a> • 
    <a href='settings.md'>Documentation</a> • <a href='how_it_works.md'>How does it work?</a> • <b>Questions</b>
</p>

# Q&A:
**Q:** Why do blue inscriptions appear in mods at all?

**A:** If no values are specified for a tag added by the mod in your language, the tag’s name appears in blue instead of a translation.

---
**Q:** Why do I still see blue inscriptions in the game after translating a mod?

**A:** Most likely, the source language used for translation didn’t include all tags. The script doesn’t check for the presence of all tags in the source language (this may be fixed in the future).

---
**Q:** I’m already playing with untranslated mods. Can I translate them and continue playing on my save?

**A:** You can try enabling the translated mod, but it’s better to start a new game, as loading a save with the translated mod might cause the game to crash. This shouldn’t break your save, and you can continue playing with your original mod list as before.

---
**Q:** The mod only has `.loc2` files and no `.xml` files in the `localization` folder. Can I still translate it?

**A:** In such cases, there are two options: find the `.xml` file or copy a `.loc2` file from another language.  
For the first option, a link to the `.xml` file can sometimes be found in the mod’s description, or you can ask the mod author for it. Once obtained, move the file to the `localization` folder and translate as usual.  
The second option is to copy a `.loc2` file from another language that you understand in-game. The script has settings to do this quickly (see Settings Description).