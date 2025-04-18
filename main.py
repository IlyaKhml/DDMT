settings = {
    # Основные настройки
    'target_languages': ['russian'],
    'mod_folder_path': r'G:\SteamLibrary\steamapps\common\DarkestDungeon\mods\0000000',

    # Приоритет выбора файла xml/языка с которого переводить
    'translate_xml_language_priority': ['schinese', 'english'],

    # Флаг определяющий нужно ли делать перевод xml или просто скопировать loc2 с языком из LOC2_TRANSLATE_PRIORITY
    'copy_loc2_without_translate': False,
    'loc2_translate_priority': ['english'],

    # Изменение названия мода
    'suffix_to_mod_title': 'Translated',
    'new_mod_title': False,

    # Настройки переводчика
    'translator': 'GoogleTranslator',

    # Api-ключ для переводчика
    # 'translator_api_key': "",

    # Режим перевода [raw, optimal, deepl_mustache]
    'translator_mode': 'optimal',

    # Язык исходного текста для переводчика (для GoogleTranslator - 'auto')
    'translator_source_lang': False,
    
    # Модель для перевода (только для API LLM)
    # 'translator_model': 'deepseek-ai/DeepSeek-R1',

    # Настроики для переводчика (только для API LLM)
    # 'translator_settings': {'system_prompt': ''},

    'translate_comments': False,
    'force_overwrite_loc2': False,
    
    # Использовать детектор языка для каждой строки xml
    # 'use_language_detector':False,

    # Api-ключ для языкового детектора
    # 'language_detector_api_key':'',

    # Вывод отладочных сообщений (Показывает все строки, которые отправляются в переводчик)
    'translator_debug': True,
}
if __name__ == "__main__":
    from TranslationManager import TranslationManager
    mod_translator = TranslationManager(settings)
    mod_translator.translate_mod()