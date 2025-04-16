from typing import List, Dict, Optional, Union
import xml.etree.ElementTree as ET
import re

class XMLUtils:
    def parse_xml(self, file_path: str) -> Union[Optional[ET.Element], Optional[ET.ElementTree]]:
        """
        Парсит XML файл, сохраняя комментарии, и возвращает корневой элемент и дерево.
        """
        try:
            parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
            tree = ET.parse(file_path, parser=parser)
            return tree.getroot(), tree
        except FileNotFoundError:
            print(f"Файл не найден: {file_path}")
            return None, None
        except ET.ParseError:
            print(f"Ошибка при парсинге XML файла: {file_path}")
            return None, None

    @staticmethod
    def get_languages(root: ET.Element) -> List[str]:
        """Возвращает список id всех языков из XML"""
        return [lang.get('id') for lang in root.findall('language')]

    @staticmethod
    def get_language_element(root: ET.Element, language_id: str) -> Optional[ET.Element]:
        """Возвращает элемент <language> с указанным id"""
        return root.find(f"language[@id='{language_id}']")

    @staticmethod
    def get_text_elements(language_element: ET.Element) -> list:
        """
        Возвращает список кортежей (element, idx) для всех вложенных элементов,
        содержащих непустой текст внутри language_element.
        """
        return [(elem, idx) for idx, elem in enumerate(language_element.iter()) if elem.text and elem.text.strip()]

    @staticmethod
    def save_xml_with_cdata_and_comments(tree: ET.ElementTree, file_path: str) -> None:
        """
        Сохраняет XML, сохраняя комментарии, пустые теги как <entry></entry> и добавляя <![CDATA[]]>.
        """
        xml_str = ET.tostring(tree.getroot(), encoding="utf-8").decode("utf-8")
        
        def replace_text(match):
            tag = match.group(1)
            text = match.group(2)
            return f'<{tag}><![CDATA[{text}]]></{tag.split()[0]}>'
        
        pattern = r'<(entry id="[^"]*")>(.*?)</entry>'
        xml_str = re.sub(pattern, replace_text, xml_str, flags=re.DOTALL)

        # Заменяем <entry id="..."/> на <entry id="..."></entry>
        xml_str = re.sub(r'<(entry id="[^"]*") ?/>', r'<\1><![CDATA[]]></entry>', xml_str)

        # Форматируем <language> с отступами
        lines = xml_str.splitlines()
        formatted_lines = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('<language'):
                formatted_lines.append(f'\t{stripped_line}')
            elif stripped_line.startswith('</language'):
                formatted_lines.append(f'\t{stripped_line}')
            else:
                formatted_lines.append(line)

        formatted_xml = '\n'.join(formatted_lines)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(formatted_xml)

    def remove_languages(self, file_path: str, languages_to_remove: List[str]) -> None:
        """
        Удаляет языки из XML файла по списку их id, сохраняя комментарии.
        """
        root, tree = self.parse_xml(file_path)
        if root is None or tree is None:
            return

        removed_count = 0
        for lang_id in languages_to_remove:
            lang_element = root.find(f"language[@id='{lang_id}']")
            if lang_element is not None:
                root.remove(lang_element)
                removed_count += 1
                print(f"Язык {lang_id} успешно удален.")
            else:
                print(f"Язык {lang_id} не найден в файле.")
        
        if removed_count > 0:
            self.save_xml_with_cdata_and_comments(tree, file_path)
            print(f"Файл обновлен. Удалено {removed_count} языков.")
        else:
            print("Ничего не было удалено.")

    def add_languages_with_structure(
        self,
        file_path: str,
        languages_to_add: Dict[str, List[ET.Element]],
        overwrite_existing: bool = True,
    ) -> None:
        """
        Добавляет несколько языков из словаря {id: [элементы]}, сохраняя комментарии.
        :param overwrite_existing: Если True, существующие языки будут перезаписаны
        """
        root, tree = self.parse_xml(file_path)
        if root is None or tree is None:
            return

        added_count = 0
        for lang_id, elements in languages_to_add.items():
            existing_lang = root.find(f"language[@id='{lang_id}']")
            
            if existing_lang is not None:
                if not overwrite_existing:
                    print(f"Язык {lang_id} уже существует. Пропуск. (Файл: {file_path})")
                    continue
                else:
                    # Удаляем существующий язык перед добавлением нового
                    root.remove(existing_lang)
                    print(f"Язык {lang_id} будет перезаписан. (Файл: {file_path})")

            # Создаем новый элемент языка
            new_lang = ET.Element("language", attrib={"id": lang_id})
            for elem in elements:
                new_elem = ET.Element(elem.tag, attrib=elem.attrib)
                new_elem.text = elem.text
                new_elem.tail = elem.tail
                new_lang.append(new_elem)
            
            root.append(new_lang)
            added_count += 1
            action = "перезаписан" if existing_lang is not None else "добавлен"
            print(f"Язык {lang_id} успешно {action} в файл {file_path}.")

        if added_count > 0:
            self.save_xml_with_cdata_and_comments(tree, file_path)
            print(f"Файл xml обновлен. Обработано {added_count} языков.")
        else:
            print("Ничего не было изменено в xml файле.")