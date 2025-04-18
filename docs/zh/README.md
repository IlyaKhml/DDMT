<!-- (Automatically translated via ChatGPT.) -->

<p align='center'>
    <a href='..\..\README.md'>RU</a> • <a href='..\en\README.md'>EN</a> • <b>ZH</b>
</p>
<p align='center'>
    <b>主页</b> • 
    <a href='settings.md'>文件</a> • <a href='how_it_works.md'>它是如何工作的？</a> • <a href='qa.md'>问题</a>
</p>


# 主要功能
* 从修改的 `.xml` 文件（包括注释）进行全文翻译。
* 自动创建 `.loc2` 文件并添加到修改中。
* 选择多种翻译器（Google Translate、DeepL 和 API LLM 模型）。
* 支持翻译包含多种语言文本的修改。
* 替换特定语言的 `.loc2` 文件。

# 安装
要下载仓库并运行脚本，您需要：
* **Python**（从[官方网站](https://www.python.org/downloads/)下载）；
* **git**（从[官方网站](https://git-scm.com/downloads)下载）。

1. 进入您希望安装 `DDMT` 的文件夹。
2. 克隆仓库：
```bash
git clone https://github.com/IlyaKhml/DDMT.git
```
3. 创建并激活虚拟环境：
```bash
python -m venv venv

source venv/bin/activate # 在 Linux 上
venv\Scripts\activate # 在 Windows 上
```
4. 安装依赖项：
```bash
pip install -r requirements.txt
```

可选：为了更方便地查看 `.xml` 文件，您可以安装 [Notepad++](https://notepad-plus-plus.org/downloads/)（它支持语法高亮）。

# 使用方法
以下是翻译单个修改的大致步骤。

1. 找到您想要翻译的 **修改文件夹**。
   > **示例：** `G:\SteamLibrary\steamapps\workshop\content\262060\2200558948`

2. 将修改复制到 Darkest Dungeon 目录中的 `mods` 文件夹（本地修改文件夹）。
   > **本地修改文件夹示例路径：** `G:\SteamLibrary\steamapps\common\DarkestDungeon\mods`
   >
   > **如何找到游戏文件夹：** 在 Steam 中右键单击游戏图标 > 管理 > 浏览本地文件

3. 检查 `localization` 文件夹中的 `.xml` 文件数量。建议仅保留一个 `.xml` 文件用于翻译。如有需要，可以合并多个 `.xml` 文件的翻译。

4. 选择翻译的源语言，并确保 `.xml` 文件中对应语言标签的所有字符串与该语言一致（用于翻译设置和语言检测）。

5. 复制您刚刚复制的修改文件夹路径。
   > **示例：** `G:\SteamLibrary\steamapps\common\DarkestDungeon\mods\2200558948`

6. 将修改路径粘贴到设置中（为 `mod_folder_path` 键指定值）。
7. 根据需要配置其他参数。
8. 使用 Python 运行脚本文件：
```bash
python main.py
```
9. 等待直到出现 `"Translation completed!"` 消息。