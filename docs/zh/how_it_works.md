<!-- (Automatically translated via ChatGPT.) -->

<p align='center'>
    <a href='..\ru\how_it_works.md'>RU</a> • <a href='..\en\how_it_works.md'>EN</a> • <b>ZH</b>
</p>
<p align='center'>
    <a href='README.md'>主页</a> • 
    <a href='settings.md'>文件</a> • <b>它是如何工作的？</b> • <a href='qa.md'>问题</a>
</p>

# 本地化文件与手动翻译说明
## 基础知识
首先，确保模组具有本地化文件（游戏中显示的文本）。检查模组目录中是否有一个名为 `localization` 的文件夹。如果其中包含 `.loc2` 和 `.xml` 文件，则该模组可以完全或部分翻译成你的语言。

| 文件类型 | 功能                                                                                                   | 保证                                                                 |
| -------- | ------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| `.loc2`  | 游戏的编码文本，无法直接翻译。                                                                         | ✔️ 部分翻译（将蓝色文本替换为现有语言）                              |
| `.xml`   | 用于创建 `.loc2` 文件的文本字符串。可以翻译成其他语言。                                                | ✔️ 完整模组翻译                                                     |

## 文件命名
此信息主要针对希望手动翻译的用户。
> **本地化文件有特定部分不可更改！**

| 文件类型 | 示例名称                     | 说明                                                                                                                                                                                                                   |
| -------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.loc2`  | `2200558948_english.loc2`    | 文件名由 `localization.exe` 自动设置。                                                                                                                                                                                 |
| `.xml`   | `test.string_table.xml`      | `test` - 任意名称，无特殊意义。<br>`.string_table` - 表示该文件包含用于翻译的字符串，通过 `localization.exe` 创建 `.loc2` 文件（如果没有此后缀，`.xml` 文件将无法被检测用于翻译）。 |

## 创建翻译
首先选择翻译的目标语言。通常有一个 `.xml` 文件包含所有语言，但一些模组作者为每种语言创建单独的 `.xml` 文件。在这种情况下，你可以创建一个新的翻译文件，复制现有的 `.xml` 文件，或在现有的 `.xml` 文件中添加新的语言标签：
`<language id=[游戏支持的语言]> </language>`。

然后，将所有字符串翻译成目标语言并保存文件。

## 将 `.xml` 转换为 `.loc2`
位于游戏 `_windows` 文件夹中的 `localization.exe` 文件用于转换。

文件示例路径：
`G:\SteamLibrary\steamapps\common\DarkestDungeon\_windows\localization.exe`

要转换 `.xml` 文件，请将 `localization.exe` 和 `_windows` 文件夹中的其他几个文件（如下所述）放入模组的 `localization` 文件夹中。

> 文件夹必须命名为 `localization`，否则 `localization.exe` 将无法正常工作。

文件夹应包含以下文件：
* `一个或多个用于创建 .loc2 的 .xml 文件`
* `localization.exe`
* `fmod.dll`
* `fmodstudio.dll`
* `glew32.dll`
* `SDL2.dll`
* `steam_api.dll`

接下来，运行 `localization.exe`，它将为游戏创建 `.loc2` 本地化文件。

## 在 `modfiles.txt` 中添加路径
`.loc2` 文件已创建，但游戏需要知道加载哪些模组文件。这由位于模组根目录的 `modfiles.txt` 文件处理。

它指定文件的相对路径（相对于模组文件夹）和文件大小（以字节为单位）：
`project.xml 4585`

文件大小可能被 Steam 创意工坊用于判断哪些模组文件在损坏时需要重新下载。

添加对新 `.loc2` 文件及其大小的引用，例如：
`localization/2200558948_russian.loc2 20232`
`localization/2200558948_english.loc2 20254`

## 编辑 `project.xml`
最后一步是修改模组根目录中的 `project.xml` 文件中的模组名称，以区别于原始模组。

找到包含模组名称的 `<Title>` 标签并更新它：

`<Title>Lilith class</Title>` -> `<Title>Lilith class Translated</Title>`

---
完成！

模组现在应已翻译成你的语言，并可在游戏中选择使用。