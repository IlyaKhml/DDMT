from TranslationService import TranslationService

from typing import List, Optional

import xml.etree.ElementTree as ET

import subprocess
import warnings
import shutil
import time
import os

# Класс для перевода
class TranslationManager:
    REQUIRED_VALUES = {
        'loc2_translate_priority': [],
        'translate_xml_language_priority': [],
        'suffix_to_mod_title': 'Translated',
        'new_mod_title': False,

        'copy_loc2_without_translate': False,
        'target_languages': None,
        'mod_folder_path': None,

        'translator': 'GoogleTranslator', # DeeplTranslator, OpenAI, AIOI
        'translator_api_key': False,
        'translator_mode': 'optimal',     # [raw, optimal, deepl_mustache]
        'translator_source_lang': False,  # [False, 'auto'] False - выбрать язык из xml-файла, 'auto' - автоматическое определение переводчиком
        'translator_model': False,
        'translator_settings': dict(),

        'translator_debug': False,
        'translate_comments': False,
        'force_overwrite_loc2': False,

        'use_language_detector': False,
        'language_detector_api_key': '',
    }
    
    TranslationService = TranslationService()

    # Путь до папки с с файлами для конвертации xml в loc2
    XML2LOC2_FOLDER = os.path.join(os.getcwd(), 'localization')

    # Файлы необходимые для конвертации xml в loc2
    XML2LOC2_FILES = ['fmod.dll', 'fmodstudio.dll', 'glew32.dll', 'localization.exe', 'SDL2.dll', 'steam_api.dll']

    # Папка программы
    program_dir = os.getcwd()

    # Папка с файлами локализации
    LOCALIZATION_FOLDER = 'localization'
    REQUIRED_MOD_FILES = ['project.xml', 'modfiles.txt'] # Файлы, которые должны быть в директории мода

    # Наличие файлов и папок
    copy_loc2_status = True
    translate_xml_status = True
    requared_files_status = dict()

    # Файлы локализации
    localization_files = []
    localization_loc2 = []
    localization_xml = []
    new_loc2_files = []     # Список созданных файлов loc2

    # Новое название мода (с суффиксом)
    new_mod_name = ''

    def __init__(self, settings: dict):
        print(f"[0]{'[ Инициализация ]':-^50}")

        # Распаковываем настроики
        for key, default_value in self.REQUIRED_VALUES.items():
            # Получаем значение из settings, если оно существует
            value = settings.get(key)
            
            # Если значение не указано или "ложноподобное", используем значение по умолчанию
            if not value:
                if default_value is None:
                    raise ValueError(f"Отсутствует необходимое значение: ключ '{key}' должен быть указан.")
                elif value == default_value: # Если значение такое же как по умолчанию, то пропускаем (чтоб не выводить предупреждение)
                    pass
                else:
                    warnings.warn(f"Используется значение по умолчанию для '{key}': {default_value}.", UserWarning)
                    value = default_value
            
            # Устанавливаем атрибут
            setattr(self, key, value)
        
        self.mod_steam_id = os.path.basename(self.mod_folder_path)

    def check_translation_conditions(self) -> bool:
        """
        Проверяет условия, доступность языков, наличие необходимых файлов и папок 
        для перевода мода и сохраняет результат в классе.
        """

        # Проверка папки с модом
        if not os.path.exists(os.path.join(self.program_dir, self.mod_folder_path)):
            print(f"Ошибка: Папка {self.mod_folder_path} не найдена, невозможно сделать перевод.")
            
        # Проверка файлов в начальной папке мода
        self.requared_files_status = {i: os.path.exists(os.path.join(self.mod_folder_path ,i)) for i in self.REQUIRED_MOD_FILES}
        for file, status in self.requared_files_status.items():
            if not status:
                print(f"Ошибка: Файл {file} не найден в папке мода и действия с ним будут пропущены.")

        # Проверка папки локализации мода
        localization_full_path = os.path.join(self.mod_folder_path, self.LOCALIZATION_FOLDER)
        if os.path.exists(localization_full_path):
            self.localization_files = os.listdir(localization_full_path)

            # Находим файлы xml и loc2
            for file in self.localization_files:
                if file.endswith(('.xml')):
                    self.localization_xml.append(file)

                elif file.endswith(('.loc2')):
                    self.localization_loc2.append(file)

        else:
            print(f"Ошибка: Папка {self.LOCALIZATION_FOLDER} не найдена в папке мода, невозможно сделать перевод.")
            self.copy_loc2_status, self.translate_xml_status = False, False
        

        # Проверить наличие папки с файлами для создания loc2 из xml файлов
        if os.path.isabs(self.XML2LOC2_FOLDER):
            if not os.path.exists(self.XML2LOC2_FOLDER):
                print(f"Ошибка: Папка {self.XML2LOC2_FOLDER} не найдена, невозможно сделать перевод xml файла.")
                self.translate_xml_status = False
            else:
                # Проверяем наличие необходимых файлов для конвертации xml2loc2
                for file in self.XML2LOC2_FILES:
                    if not os.path.exists(os.path.join(self.XML2LOC2_FOLDER, file)):
                        print(f"Ошибка: Файл {file} не найден в папке {self.XML2LOC2_FOLDER}, невозможно сделать перевод xml файла.")
                        self.translate_xml_status = False
        else:
            if not os.path.exists(os.path.join(self.program_dir, self.XML2LOC2_FOLDER)):
                print(f"Ошибка: Папка {self.XML2LOC2_FOLDER} не найдена, невозможно сделать перевод xml файла.")
                self.translate_xml_status = False

        # Проверка запрашиваемого языка перевода
        for lang in self.target_languages:
            if lang not in self.TranslationService.Darkest_Dungeon_files_languages:
                warnings.warn(f'Убедитесь, что язык "{lang}" поддерживается игрой. При необходимости обновите список языков "Darkest_Dungeon_files_languages" в "TranslationService.py", чтобы убрать это предупреждение.', UserWarning)

        # Проверка поддежки языков переводчика
        # for lang in self.target_languages:
        #     if self.TranslationService.DarkestDungeon2Translator[lang] not in self.translator_langs_dict:
        #         print(f"Ошибка: Язык {lang} не поддерживается переводчиком, невозможно сделать перевод.")
        #         self.target_languages.remove(lang)
        
        if not self.target_languages:
            print("Ошибка: Не удалось найти поддерживаемые языки переводчика, невозможно сделать перевод.")
            self.translate_xml_status = False
        
        # Чистим папку xml2loc2
        self.clear_xml2loc2_folder()

        return True

    def clear_xml2loc2_folder(self):
        """
        Удаляет все лишние файлы в self.XML2LOC2_FOLDER, которых нет в списке self.XML2LOC2_FILES.
        """
        # Проверяем, существует ли указанная папка
        if not os.path.isdir(self.XML2LOC2_FOLDER):
            raise ValueError(f"Ошибка: Папка '{self.XML2LOC2_FOLDER}' не существует.")

        # Получаем список всех файлов в папке
        all_files = os.listdir(self.XML2LOC2_FOLDER)

        # Фильтруем только файлы (игнорируем подпапки)
        all_files = [f for f in all_files if os.path.isfile(os.path.join(self.XML2LOC2_FOLDER, f))]

        # Определяем лишние файлы
        extra_files = [f for f in all_files if f not in self.XML2LOC2_FILES]

        # Удаляем лишние файлы
        removed_files = []
        for file_name in extra_files:
            file_path = os.path.join(self.XML2LOC2_FOLDER, file_name)
            try:
                os.remove(file_path)
                removed_files.append(file_name)
            except Exception as e:
                print(f"Не удалось удалить файл '{file_name}': {e}")

        if removed_files:
            # Выводим список удалённых файлов
            print(f"Удалены лишние из {self.XML2LOC2_FOLDER} файлы:", removed_files)

        return True

    def modify_project_xml(self) -> bool:
        """Модификация project.xml для изменения названия мода"""
        try:
            project_full_filepath = os.path.join(self.mod_folder_path, 'project.xml')
            # Парсинг XML файла
            tree = ET.parse(project_full_filepath)
            root = tree.getroot()
            
            # Поиск и модификация тега Title
            title_tag = root.find('.//Title')
            if title_tag is not None:
                if self.new_mod_title:
                    title_tag.text = f"{self.new_mod_title}"
                    self.new_mod_name = title_tag.text
                    print(f"Название мода изменено на: {title_tag.text}")
                elif self.suffix_to_mod_title:
                    title_tag.text = f"{title_tag.text} {self.suffix_to_mod_title}"
                    self.new_mod_name = title_tag.text
                    print(f"Название мода изменено на: {title_tag.text}")
            else:
                print("Ошибка: Тег <Title> не найден в project.xml")
                return False
            
            # Сохранение изменений
            tree.write(project_full_filepath, encoding='utf-8', xml_declaration=True)

            return True
            
        except ET.ParseError:
            print(f"Ошибка: Не удалось разобрать {project_full_filepath}")

        except Exception as e:
            print(f"Ошибка при обработке {project_full_filepath}: {str(e)}")
        
        return False

    def copy_loc2_translate(self) -> bool:
        """Проверка и копирование файлов перевода loc2."""
        loc2_to_copy_name = '' # название файла loc2
        loc2_count = 0    # Количество файлов loc2
        used_lang = ''    # Используемый язык для копирования

        # Находим файл loc2 для копирования
        for lang in self.loc2_translate_priority:
            for i in self.localization_loc2:
                if i.endswith(lang + '.loc2'):
                    if not loc2_to_copy_name:
                        loc2_to_copy_name = i
                        used_lang = lang
                    loc2_count += 1

            if loc2_to_copy_name:
                break
        
        if not loc2_to_copy_name:
            print(f'Не удалось найти файл loc2 для копирования c языком из списка {self.loc2_translate_priority}.')
            return False
        elif loc2_count > 1:
            print(f'Найдено более одного файла loc2 с языком из списка {self.loc2_translate_priority}. Для создания перевода будет использован первый найденный {loc2_to_copy_name}.')

        print(f'Копируем файл перевода loc2: {loc2_to_copy_name}')

        for target_lang in self.target_languages:
            # Копируем файл с другим названием
            new_file_name = loc2_to_copy_name.replace(used_lang, target_lang)
            new_filepath = os.path.join(self.mod_folder_path, os.path.join(self.LOCALIZATION_FOLDER, new_file_name))
            loc2_to_copy = os.path.join(self.mod_folder_path, os.path.join(self.LOCALIZATION_FOLDER, loc2_to_copy_name))

            shutil.copy(loc2_to_copy, new_filepath)

            # Добавляем новый файл в список новых файлов
            self.new_loc2_files.append(new_filepath)

            print(f'Файл {loc2_to_copy_name} скопирован как {new_file_name}.')

        return True

    def modify_localization_file(self, modifies_path: str, second_file_paths: List[str]) -> None:
        """
        Модифицирует файл локализации modfiles.txt, добавляя пути и размеры указанных файлов.
        
        Args:
            modifies_path (str): Путь к modfiles.txt
            second_file_paths (List[str]): Список путей к файлам, которые нужно добавить
            
        Raises:
            FileNotFoundError: Если какой-либо из файлов не найден
        """
        # Проверка существования целевого файла
        if not os.path.isfile(modifies_path):
            raise FileNotFoundError(f"Файл {modifies_path} не найден")

        # Проверка существования всех дополнительных файлов
        for path in second_file_paths:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Файл {path} не найден")

        # Чтение содержимого целевого файла
        with open(modifies_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Поиск позиции для вставки
        insert_position = None
        for i, line in enumerate(lines):
            if line.startswith("localization"):
                insert_position = i + 1
                break

        if insert_position is None:
            insert_position = len(lines) + 1  # Вставка в конец файла, если "localization" не найден

        # Подготовка новых строк
        new_lines = []
        for path in second_file_paths:
            rel_path = os.path.relpath(path, start=os.path.dirname(modifies_path)).replace('\\', '/')
            file_size = int(os.path.getsize(path))
            new_line = f"{rel_path} {file_size}\n"
            new_lines.append(new_line)
            print(f'Добавлена строка {insert_position}: "{new_line.strip()}" в файл "{modifies_path}"')
            insert_position += 1

        # Вставка новых строк
        lines[insert_position-1:insert_position-1] = new_lines

        # Запись изменений
        with open(modifies_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)        

    def choose_xml_file_for_translation(self) -> str:
        """
        Выбирает файл xml для перевода в соответствии с приоритетом (translate_xml_language_priority).

        Returns:
            str: Путь до выбранного файла xml.
        """
        xml_path = None

        # Выбор языка для перевода
        for priority in self.translate_xml_language_priority:
            if priority in self.localization_xml:
                xml_path = priority
                break

        if not xml_path:
            print(f'Не удалось найти файл xml для перевода с языков в названии из списка {self.translate_xml_language_priority}. Используем первый найденный {self.localization_xml[0]}')
            xml_path = self.localization_xml[0]

        xml_path = os.path.join(self.mod_folder_path, self.LOCALIZATION_FOLDER, xml_path)
        print(f'Выбран xml для перевода: {xml_path}')

        return xml_path

    def process_localization(self, xml_path: str, result_path: str, target_langs: Optional[List[str]] = None) -> bool:
        """
        Копирует xml и запускает localization.exe для создания loc2 файлов с переводом.

        Args:
            xml_path (str): Путь до файла xml.
            result_path (str): Путь в который будут перемещены loc2 файлы после создания.
            target_langs (Optional[List[str]]): Список языков, loc2 файлы которых нужно переместить после создания. 
                (чтобы оставить уже существующие (не запрошенные) файлы loc2, без замены).

        Returns:
            bool: True, если процесс успешно завершен, False в противном случае.
        """
        try:
            # 1. Копируем XML
            copied_xml = os.path.basename(xml_path) # Получаем имя xml
            
            # Файл должен заканчиваться на .string_table.xml
            if not os.path.basename(xml_path).endswith('.string_table.xml'):
                copied_xml = copied_xml.replace('.xml', '.string_table.xml')

            copied_xml = os.path.join(self.XML2LOC2_FOLDER, copied_xml) # Получаем полный путь
            shutil.copy(xml_path, copied_xml)
            print(f"XML скопирован: {os.path.exists(copied_xml)}")

            # 2. Запускаем localization.exe
            localization_exe_path = os.path.abspath(os.path.join(self.XML2LOC2_FOLDER, 'localization.exe'))
            if not os.path.exists(localization_exe_path):
                print(f"Ошибка: localization.exe не найден в {self.XML2LOC2_FOLDER}")
                return False

            print(f"Запуск {localization_exe_path} ...")
            process = subprocess.Popen(
                [localization_exe_path],
                cwd=self.XML2LOC2_FOLDER,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True
            )
            time.sleep(1)
            process.communicate()  # Завершаем процесс

            # 3. Проверяем наличие созданных файлов
            loc2_files = [f for f in os.listdir(self.XML2LOC2_FOLDER) if f.endswith('.loc2')]

            if loc2_files:
                print(f"Файлы созданы: {loc2_files}")
            else:
                print("Ошибка: файлы не созданы вовремя.")
                return False

            # 4. Перемещаем файлы
            for file_name in loc2_files:
                file_to_move = True if not target_langs else False

                # Если target_langs не задан, то перемещаем все файлы
                for lang in target_langs:
                    if lang in file_name:
                        file_to_move = True
                        break
                
                if file_to_move:
                    # Переименовываем и перемещаем
                    file_name_full = os.path.join(self.XML2LOC2_FOLDER, file_name)
                    moved_file_name = os.path.join(result_path, self.mod_steam_id + '_' + file_name)
                    shutil.move(file_name_full, moved_file_name)
                    print(f'Файл "{file_name}" переименован в "{os.path.basename(moved_file_name)}" и перемещён из "{self.XML2LOC2_FOLDER}" в "{result_path}"')

                    # Добавляем перемещенные файлы в список
                    self.new_loc2_files.append(moved_file_name)

            # 5. Удаляем временные файлы
            copied_xml = os.path.join(self.XML2LOC2_FOLDER, os.path.basename(xml_path))
            if os.path.exists(copied_xml):
                os.remove(copied_xml)
                print(f"Удалён временный XML: {copied_xml}")

            for file_name in os.listdir(self.XML2LOC2_FOLDER):
                if file_name not in self.XML2LOC2_FILES:
                    os.remove(os.path.join(self.XML2LOC2_FOLDER, file_name))
                    print(f"Удалён лишний файл: {os.path.join(self.XML2LOC2_FOLDER, file_name)}")

        except Exception as e:
            print(f"Ошибка: {e}")
            return False

        return True

    def translate_mod(self):
        """Перевод мода"""
        # 1. Проверка наличия файлов и папок
        print(f"[1]{'[ Проверка наличия файлов и папок ]':-^50}")
        self.check_translation_conditions()

        if not self.copy_loc2_status and not self.translate_xml_status:
            return False
        
        # 2. Перевод
        print(f"[2]{'[ Создание перевода ]':-^50}")
        # 2.1 Копирование loc2 файлов при необходимости
        if self.copy_loc2_without_translate or len(self.localization_xml) == 0:
            if len(self.localization_xml) == 0 and not self.copy_loc2_without_translate:
                print(f'Не найдено файлов xml для создания перевода. Попытаемся скопировать файл перевода loc2 другого языка из списка {self.loc2_translate_priority}.')
            
            if not self.loc2_translate_priority:
                print(f'Нет языков из списка ({self.loc2_translate_priority}), которые можно исспользовать для копирования файлов перевода loc2. Перевод не может быть выполнен.')
                return False

            if not self.copy_loc2_translate():
                return False
        
        # 2.2 Перевод xml-файлов
        if self.translate_xml_status:
            xml_path = self.choose_xml_file_for_translation()

            translate_status = self.TranslationService.translate_xml(xml_path, 
                                                  source_language_priority = self.translate_xml_language_priority, 
                                                  target_languages = self.target_languages, 
                                                  mode = self.translator_mode, 
                                                  translator = self.translator, 
                                                  translator_source_lang = self.translator_source_lang,
                                                  translator_api = self.translator_api_key,
                                                  translate_comments = self.translate_comments,
                                                  use_language_detector = self.use_language_detector,
                                                  language_detector_api_key = self.language_detector_api_key,
                                                  translator_model= self.translator_model,
                                                  translator_settings = self.translator_settings,
                                                  debug = self.translator_debug)
                
            if not translate_status:
                return False
            
            # 2.3 Создание loc2 файлов и перемещение в мод
            translate_status = self.process_localization(xml_path = xml_path, 
                                                         result_path = os.path.join(self.mod_folder_path, 'localization'),
                                                         target_langs = self.target_languages if not self.force_overwrite_loc2 else None)

            if not translate_status:
                return False

        # 2.4 Добавление новых файлов loc2 в modfiles.txt
        if self.requared_files_status['modfiles.txt']:
            modifies_path = os.path.join(self.mod_folder_path, 'modfiles.txt')
            self.modify_localization_file(modifies_path, self.new_loc2_files)

        # 2.5 Добавляем название мода в project.xml
        if self.requared_files_status['project.xml']:
            self.modify_project_xml()
        
        print(f"[3]{'[ Перевод завершен! ]':-^50}")
        print('Новое название мода: ', self.new_mod_name)
        
        return True