from XMLUtils import XMLUtils
from LLMClient import LLMClient

import xml.etree.ElementTree as ET

import deep_translator
import time
import re

from typing import Dict, Optional, Union, Tuple
from tqdm import tqdm

import warnings

class TranslationService:
    SEGMENT_PATTERN = r'(\{[^}]+\}|[%％]\w+[%％][%％]?|[\n\t]+)'
    XML_UTILS = XMLUtils()

    # Поддерживаемые DD языки
    Darkest_Dungeon_files_languages = ['brazilian','czech','english','french','german','italian','japanese','koreana','koreanb','polish','russian','schinese','spanish','tchinese']
    
    # Перевод языка DD -> Язык переводчика
    DarkestDungeon2Translator = {
        'schinese':'chinese (simplified)',
        'tchinese':'chinese (traditional)',
        'brazilian':'portuguese',
        'koreana':'korean',
        'koreanb':'korean',
    }

    # Для замены паттернов на уникальные шаблоны и обратно при mode равным 'deepl_mustache'
    deepl_mustache_dict = dict()

    def get_text_elements(self, language_element: ET.Element) -> list:
        """
        Возвращает список кортежей (element, idx) для всех вложенных элементов,
        содержащих непустой текст внутри language_element.
        """
        return [(elem, idx) for idx, elem in enumerate(language_element.iter()) if elem.text and elem.text.strip()]
    
    def split_text_segments(self, text: str, mode: str) -> list:
        """
        При режиме 'optimal' разбивает строку на сегменты с использованием SEGMENT_PATTERN,
        а при 'raw' возвращает список с исходным текстом.
        """
        if mode == 'optimal':
            return re.split(self.SEGMENT_PATTERN, text)
        
        return [text]

    def split_text_segments(self, text: str, mode: str) -> list:
        """
        При режиме 'optimal' разбивает строку на сегменты с использованием SEGMENT_PATTERN,
        а при 'raw' и 'deepl_mustache' возвращает список с исходным текстом.
        """
        if mode == 'optimal':
            return re.split(self.SEGMENT_PATTERN, text)
        return [text]

    def select_translation_language(self, available_languages: list, source_language_priority: list, xml_path: str):
        """
        Выбирает язык для перевода на основе приоритетного списка языков.
        
        :param available_languages: Список доступных языков из XML-файла.
        :param source_language_priority: Приоритетный список языков для перевода.
        :param xml_path: Путь к XML-файлу (используется для информативных сообщений).
        :return: Выбранный язык или None, если выбор невозможен.
        """
        if not available_languages:
            print(f'Ошибка: Не найдено доступных для перевода языков в "{xml_path}".\n'
                f'Проверьте файл на наличие тегов <language> с id языка для перевода.')
            return None

        # Выбор языка из приоритетного списка
        for lang in source_language_priority:
            if lang in available_languages:
                print(f'Для перевода выбран язык "{lang}" из файла "{xml_path}".')
                return lang

        # Если ни один язык из приоритетного списка не найден, выбираем первый доступный
        selected_language = available_languages[0]
        print(f'Язык перевода из {source_language_priority} не найден. '
            f'Будет выбран первый язык из файла xml: "{selected_language}".')
        
        return selected_language

    def extract_segments(self, lang_element: ET.Element, mode: str) -> Tuple[list, list, set]:
        """
        Извлекает сегменты текста для каждого элемента XML, возвращая:
        - elems: список элементов (ссылки на узлы XML),
        - segments: список списков сегментов для каждого элемента,
        - comment_indexes: множество индексов, соответствующих комментариям.

        Args:
            lang_element: Элемент XML, содержащий текст для перевода.
            mode: Режим перевода из ['raw', 'optimal'].

        returns:
            Tuple[list, list[list[str]], set]: elems, segments, comment_indexes
        """
        elems = []
        segments = []
        comment_indexes = set()

        for elem in lang_element.iter():
            if elem.text and elem.text.strip():
                elems.append(elem)
                segments.append(self.split_text_segments(elem.text, mode))
                # Если тег является комментарием – фиксируем индекс в списке elems
                if callable(elem.tag) and 'Comment' in elem.tag.__qualname__:
                    comment_indexes.add(len(elems) - 1)
        
        return elems, segments, comment_indexes

    def build_translation_queue(self, segments: list[list[str]], comment_indexes: set, mode: str, translate_comments: bool) -> Tuple[dict, list, int, int]:
        """
        Собирает уникальные строки для перевода из списка сегментов.
        Возвращает:
        - translations: словарь {строка: перевод} (перевод пока пустой),
        - indices_map: список множеств индексов сегментов для перевода для каждого элемента,
        - total_chars: суммарное количество символов для перевода.
        - total_segments: суммарное количество сегментов для перевода.

        Args:
            segments: список списков сегментов для каждого элемента (строки на перевод).
            comment_indexes: множество индексов, соответствующих комментариям.
            mode: Режим перевода из ['raw', 'optimal'].
            translate_comments: Флаг перевода комментариев.

        returns:
            Tuple[dict, list, int, int]: translations, indices_map, total_chars, total_segments
        """
        translations = {}
        indices_map = []
        total_chars = 0
        total_segments = 0

        def has_text(s: str) -> bool:
            return bool(re.search(r'[^\W\d_]+', s))
        
        for idx, seg_list in enumerate(segments):
            trans_indices = set()
            # Если не требуется переводить комментарии и это комментарий – пропускаем
            if not translate_comments and idx in comment_indexes:
                indices_map.append(trans_indices)
                continue

            for i, seg in enumerate(seg_list):
                
                # Пропускаем пустые сегменты и сегменты являющиеся патерном
                if mode == 'optimal':
                    if re.search(self.SEGMENT_PATTERN, seg) or seg == '':
                        continue
                
                seg_stripped = seg.strip()

                if not has_text(seg_stripped):
                    continue

                trans_indices.add(i)

                if seg_stripped not in translations:
                    translations[seg_stripped] = ""
                    total_chars += len(seg_stripped)
                    total_segments += 1

            indices_map.append(trans_indices)

        return translations, indices_map, total_chars, total_segments

    def initialize_translator(self, translator_name: str, translator_api: str, 
                              source_tag: str, target_tag: str, translator_source_lang: Optional[str] = None) -> object:
        """
        Инициализирует переводчик из deep_translator по имени translator_name.
        При необходимости использует translator_api и внешние сопоставления.
        """
        # Получаем класс переводчика
        translator_class = getattr(deep_translator, translator_name)
        if translator_api:
            translator_langs_dict = translator_class(api_key=translator_api).get_supported_languages(as_dict=True)
        else:
            translator_langs_dict = translator_class().get_supported_languages(as_dict=True)
        
        # Получаем язык с которого нужно перевести
        if translator_source_lang:
            source = translator_source_lang
        else:
            source_lang = self.DarkestDungeon2Translator.get(source_tag, source_tag)
            source = translator_langs_dict[source_lang]

        # Язык на который нужно перевести текст
        target = translator_langs_dict[target_tag]

        print(f'{source=} | {target=} | {translator_name=}')

        return translator_class(source=source, target=target, api_key=translator_api)
    
    def translate_texts(self, translator_instance: object, texts: dict, 
                        use_language_detector: bool, language_detector_api_key: Optional[str] = None,
                        debug: bool = False, max_tries: int = 3) -> None:
        """
        Переводит каждую строку из texts с несколькими попытками (max_tries).
        Если debug=True, выводит строки перед отправкой в переводчик.
        """

        for text in tqdm(list(texts.keys()), desc='Перевод текста'):
            tries = max_tries
            if debug:
                print(f'[DEBUG] Отправка на перевод: {text}')
            
            if use_language_detector:
                text_for_lang_detection = re.sub(r'(<m id=\d+/>)', '', text)    # Убираем теги, для лучшей работы
                print(f'[DEBUG] Определение языка: "{text_for_lang_detection}" (сегмент "{text}")')
                segment_lang = deep_translator.single_detection(text_for_lang_detection, api_key=language_detector_api_key)
                translator_instance._source = segment_lang

                if debug:
                    print(f'[DEBUG] Определен язык: "{segment_lang}" (сегмент "{text}")')
                
            while tries > 0:
                try:
                    texts[text] = translator_instance.translate(text)
                    if debug:
                        print(f'[DEBUG] Получен перевод: {texts[text]}')
                    break
                except Exception as e:
                    print(f'Ошибка при переводе "{text}": {e}. Повтор через 3 секунды.')
                    time.sleep(3)
                    tries -= 1

            if tries == 0 and texts[text] == "":
                warnings.warn(f'Не удалось перевести строку "{text}" за отведённое количество попыток. Пропускаем ...')
                texts[text] = text
    
    def apply_translations(self, xml_elems: list, segments: list, indices_map: list, translations: dict, mode: str) -> None:
        """
        Обновляет текст элементов xml, заменяя сегменты на переведённые значения.'

        Args:
            xml_elems: Список xml элементов.
            segments: Список сегментов текста.
            indices_map: Список индексов, соответствующих переводимым сегментам.
            translations: Словарь переводов.
            mode: Режим перевода из ['raw', 'optimal', 'deepl_mustache']. Если 'deepl_mustache', то заменяет непереводимые теги обратно в тексте.
        """
        for xml_elem, seg_list, trans_indices in zip(xml_elems, segments, indices_map):
            for i in trans_indices:
                original = seg_list[i].strip()
                if original in translations:
                    seg_list[i] = seg_list[i].replace(original, translations[original])
            
            # Заменяем непереводимые сегменты обратно
            if mode == 'deepl_mustache':
                self.replace_mustache_patterns_in_list(seg_list)

            xml_elem.text = ''.join(seg_list)

    def find_mustache_patterns(self, segments: list[list[str]]) -> list[list[str]]:
        """
        Находит все паттерны в тексте и сохраняет их в словарь self.deepl_mustache_dict.
        Заменяет паттерны на <m id=0 />, где id - порядковый номер паттерна.
        """
        self.deepl_mustache_dict = {}
        current_id = [0]  # Используем список для корректной модификации в замыкании
        pattern = re.compile(self.SEGMENT_PATTERN)
        
        for segment in segments:
            for i in range(len(segment)):
                text = segment[i]
                
                def replacer(match):
                    idx = current_id[0]
                    self.deepl_mustache_dict[idx] = match.group(0)
                    replacement = f"<m id={idx}/>"
                    current_id[0] += 1
                    return replacement
                
                processed_text = pattern.sub(replacer, text)
                segment[i] = processed_text
        
        return segments

    def replace_mustache_patterns_in_list(self, segments: list[str]) -> None:
        """
        Заменяет все паттерны в тексте c <m id=0 /> на исходное значение из self.deepl_mustache_dict,
        где id - порядковый номер паттерна.
        Работает с list[str] и изменяет его "на месте".
        """
        # Определяем регулярное выражение для поиска паттернов
        tag_pattern = re.compile(r'<m id=(\d+)/>')
        
        # Функция замены, используемая для каждого найденного паттерна
        def replace_tag(match):
            tag_id = int(match.group(1))
            return self.deepl_mustache_dict.get(tag_id, '')
        
        # Обрабатываем каждую строку в списке, изменяя его "на месте"
        for i in range(len(segments)):
            segments[i] = tag_pattern.sub(replace_tag, segments[i])

    def translate_xml(self, xml_path: str, source_language_priority: list, target_languages: list, 
                      mode: str = 'optimal', translator: str = 'GoogleTranslator', translator_source_lang: Optional[str] = None,
                      translator_api: str = None, translate_comments: bool = False, use_language_detector: bool = False,
                      language_detector_api_key: Optional[str] = None, translator_model: Optional[str] = None, translator_settings: dict = dict(), 
                      debug: bool = False) -> Union[bool, Dict]:
        """
        Переводит содержимое тегов <entry> в XML файле (xml_path) для языка language_tag
        на указанные target_languages.

        Режимы:
        - 'raw': перевод всего текста без предобработки.
        - 'optimal': разбивка строки на переводимые и неизменяемые сегменты.
        - 'deepl_mustache': перевод с использованием Mustache-шаблонов, подходит только для DeepL переводчика. 
                            Остальные переводчики могут искажать шаблоны при переводе. 
                            Заменяем непереводимые сегменты на уникальные идентификаторы, после перевода заменяет обратно.

        Args:
            xml_path (str): Полный путь до xml-файла.
            language_tag (str): ID языка из xml-файла для перевода.
            target_languages (list): Список языков, на который нужно перевести.
            mode (str): Режим перевода ('optimal' или 'raw', 'deepl_mustache').
            translator (str): Название переводчика (из deep_translator).
            translator_api (str): API-ключ для переводчика, если требуется.
            translator_source_lang (str | None): Язык, который нужно указать для переводчика в качестве исходного 
                (для возможности использовать автоматическое определения языка переводчиком, если исходный 
                текст содержит несколько языков (неполный перевод)). 

                Принимает значения: 
                    - None (использовать language_tag как исходный язык) 
                    - 'auto' (для автоматического определения языка переводчиком)

            translate_comments (bool): Флаг перевода комментариев.

            translator_model (str | None): Модель переводчика, если требуется.
            translator_settings (dict): Настройки для модели, если требуется. Базовый промт будет использоваться в случае отсутствия ключа 'system_prompt' и написан под mode='deepl_mustache'.
            
            use_language_detector (bool): Флаг использования языкового детектора. Проверяет язык каждого сегмента текста перед переводом.
            language_detector_api_key (str | None): API-ключ для языкового детектора.
            
            debug (bool): Флаг отладочного вывода строк для перевода.
            
        Returns:
            Словарь переведённых языковых элементов или False при ошибке.
        """
        translate_time = time.time() # Время начала перевода

        available_modes = {'optimal', 'raw', 'deepl_mustache'}
        if mode not in available_modes:
            print(f'Режим "{mode}" не поддерживается. Будет выбран "optimal".')
            mode = 'optimal'

        if translator_source_lang and translator_source_lang != 'auto':
            print(f'Ошибка: translator_source_lang не может принмать значение {translator_source_lang} и будет заменён на "auto".')
            translator_source_lang = 'auto'
        
        # Определяем какой переводчие использвовать
        llm_traslator = False
        if translator not in deep_translator.__all__:
            llm_traslator = True
            LLM_Client = LLMClient(API=translator, model=translator_model, translator_api=translator_api)

        # Парсинг XML
        root, _ = self.XML_UTILS.parse_xml(xml_path)

        # Определение языка, с которого будем переводить
        available_languages = XMLUtils.get_languages(root)

        # Выбор языка для перевода
        language_tag = self.select_translation_language(available_languages, source_language_priority, xml_path)
        if language_tag is None:
            return False
        
        # Получаем элемент <language> указанного языка
        lang_element = self.XML_UTILS.get_language_element(root, language_tag)

        # Извлекаем элементы, сегменты и индексы комментариев
        xml_elems, segments, comment_indexes = self.extract_segments(lang_element, mode)

        # Заменяем непереводимые сегменты на уникальные идентификаторы
        if mode == 'deepl_mustache':
            segments = self.find_mustache_patterns(segments)

        # Собираем уникальные строки для перевода
        texts_to_translate, indices_map, total_chars, total_segments = self.build_translation_queue(segments, comment_indexes, mode, translate_comments)
        
        # Словарь для готовых элеметов с переводом {str: List[ET.Element]}
        translated_xml_languages = {}

        # Переводим на каждый язык
        for target_lang in target_languages:
            if llm_traslator:
                texts_to_translate = LLM_Client.translate_texts(target_lang, texts_to_translate, translator_settings, debug)

            else:
                # Создаём инстанс переводчика
                try:
                    translator_instance = self.initialize_translator(translator, translator_api, language_tag, target_lang, translator_source_lang)
                except ValueError as ve:
                    print(ve)
                    return False

                # Переводим уникальные строки
                self.translate_texts(translator_instance, texts_to_translate, use_language_detector, language_detector_api_key, debug)

            # Применяем переводы к элементам xml
            self.apply_translations(xml_elems, segments, indices_map, texts_to_translate, mode)

            # Добавляем перевод в словарь
            translated_xml_languages[target_lang] = lang_element

        # Добавялем переводы в xml файл
        self.XML_UTILS.add_languages_with_structure(xml_path, translated_xml_languages)

        # Показываем затраченное количество символов.
        def format_number(n):
            return f"{n:,}".replace(',', ' ')
        
        translate_time = round(time.time() - translate_time, 2)
        t_hours = translate_time // 3600
        t_mins = (translate_time % 3600) // 60
        t_secs = translate_time % 60
        translate_time = f'{t_hours} ч. {t_mins} мин. {t_secs:.2f} сек. ({translate_time:.2f} сек.)'
        print(f'Затрачено времени: {translate_time}')
        print("Количестов сегментов для перевода:", format_number(total_segments))
        msg = f'Количество символов для перевода: {format_number(total_chars)}'
        if len(target_languages) > 1:
            msg += f' x {len(target_languages)} ({format_number(total_chars * len(target_languages))})'
        print(msg)

        return translated_xml_languages

    def count_characters_to_translate(self, xml_path: str, language_tag: str, mode: bool = 'optimal', translate_comments: bool = False) -> Union[int, int]:
        """
        Подсчитывает количество символов для перевода с заданными параметрами.

        Режимы:
        - 'raw': перевод всего текста без предобработки.
        - 'optimal': разбивка строки на переводимые и неизменяемые сегменты.
        - 'deepl_mustache': разбивка строки на переводимые и непереводимые сегменты.

        Args:
            xml_path (str): Полный путь до xml-файла.
            language_tag (str): Тег языка из файла xml.
            mode (bool): Режим перевода из ['raw', 'optimal', 'deepl_mustache'].
            translate_comments (bool): Флаг перевода комментариев.

        Returns:
            Union[int, int]: Количество сегментов и символов для перевода.
        """
        root, _ = self.XML_UTILS.parse_xml(xml_path)
        available_languages = XMLUtils.get_languages(root) # Определение языков
        if language_tag not in available_languages:
            print(f'Язык "{language_tag}" не найден в xml-файле (доступные языки: {available_languages}).')
            return False
        lang_element = self.XML_UTILS.get_language_element(root, language_tag)
        _, segments, comment_indexes = self.extract_segments(lang_element, mode)
        _, _, total_chars, total_segments = self.build_translation_queue(segments, comment_indexes, mode, translate_comments)
        
        return total_segments, total_chars