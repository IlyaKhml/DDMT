from openai import OpenAI
from tqdm import tqdm

import requests
import warnings
import time

from pprint import pprint


class LLMClient:
    DEFAULT_MODELS = {
        'OpenAI': 'gpt-4o-mini',
        'AIOI': 'deepseek-ai/DeepSeek-R1',
    }
    AVALIABLE_API = list(DEFAULT_MODELS.keys())

    def __init__(self, API='OpenAI', model=None, translator_api=None):
        # Выбираем API
        if API not in self.AVALIABLE_API:
            raise Exception(f'API {API} не доступен для выбора (доступные: {self.AVALIABLE_API})')
        self.API = API

        # Выбираем модель
        if not model:
            self.model = self.DEFAULT_MODELS[self.API]
            print(f'Для API {self.API} используется модель по умолчанию {self.model}')
        else:
            self.model = model
        
        # Получаем api-ключ
        if translator_api is None:
            raise Exception('"translator_api_key" не может быть "None" для LLMClient.')
        self.api_key = translator_api

        # Словарь API: функция
        self.func_map = {
            'OpenAI': self.translate_open_ai,
            'AIOI': self.translate_aioi,
        }

    def translate_texts(self, target_language:str, texts_to_translate: dict, settings: dict = dict(), debug: bool = False):
        """
        Переводит текст в texts_to_translate на указанный язык (target_language).

        Args:
            target_language (str): Язык, на который нужно перевести.
            texts_to_translate (dict): Словарь с текстом, где в ключах оригинальные строки, а в значениях пустые строки для перевода.
            settings (dict, optional): Дополнительные настройки для переводчика (промты, и т.д). Defaults to dict().
            debug (bool, optional): Выводить отладочную информацию (что отправляется и что получаем). Defaults to False.
        """
        func = self.func_map.get(self.API)
        
        if func is None:
            raise Exception(f'API {self.API} не поддерживается')
        
        return func(target_language, texts_to_translate, settings, debug)
    

    def translate_open_ai(self, target_language:str, texts_to_translate: dict, settings: dict = dict(), debug: bool = False):
        client = OpenAI(api_key=self.api_key)

        BASE_SYSTEM_PROMPT = "Translate all of the following text into {}. Parts marked as <m id=.... /> must remain unchanged and are the only exceptions to translation. Your response must consist solely of the translated text. Do not include any explanations, commentary, or additional information."
        system_prompt = settings.get('system_prompt', BASE_SYSTEM_PROMPT.format(target_language))

        tokens_spended = 0
        tries = 3

        # Перевод
        for text in tqdm(list(texts_to_translate.keys()), desc='Перевод текста'):
            if debug:
                print(f'[DEBUG] Отправка на перевод: {text}')

            for i in range(tries):
                try:
                    response = client.responses.create(
                        model=self.model,
                        input=text,
                        instructions=system_prompt
                    )
                    tokens_spended += response.usage.total_tokens
                    texts_to_translate[text] = response.output_text
                    if debug:
                        print(f'[DEBUG] Получен перевод: {texts_to_translate[text]}')
                    break
                except Exception as e:
                    print(f'Ошибка при переводе "{text}": {e}. Повтор через 3 секунды.')
                    time.sleep(3)
            
            if i == tries-1:
                warnings.warn(f'Не удалось перевести строку "{text}" за отведённое количество попыток. Пропускаем ...')
                texts_to_translate[text] = text

        print(f'Всего токенов затрачено на перевод: {tokens_spended}')
        return texts_to_translate        
    

    def translate_aioi(self, target_language:str, texts_to_translate: dict, settings: dict = dict(), debug: bool = False):
        url = "https://api.intelligence.io.solutions/api/v1/chat/completions"
        BASE_SYSTEM_PROMPT = "You are a translation assistant. When given a target language and text, translate all provided text into that language. Parts marked as <m id=.... /> are exceptions and must remain unchanged."

        system_prompt = settings.get('system_prompt', BASE_SYSTEM_PROMPT.format(target_language))

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        def get_custom_data(text, target_language):
            content_text = "Translate into {} and respond with only the translated text:".format(target_language) + text

            data = {
                "model": self.model,
                "reasoning_content": "false",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": content_text
                    }
                ],
            }

            return data

        tokens_spended = 0
        tries = 3

        # Перевод
        for text in tqdm(list(texts_to_translate.keys()), desc='Перевод текста'):
            if debug:
                print(f'[DEBUG] Отправка на перевод: {text}')
            
            custom_data = get_custom_data(text, target_language)
            pprint(custom_data)

            for i in range(tries+1):
                if i == tries:
                    warnings.warn(f'Не удалось перевести строку "{text}" за отведённое количество попыток. Пропускаем ...')
                    texts_to_translate[text] = text
                    break
                
                try:
                    response = requests.post(url, headers=headers, json=custom_data)
                    data = response.json()
                    tokens_spended += data['usage']['total_tokens']
                    data = data['choices'][0]['message']['content']
                    if data.startswith('<think>') or '</think>' in data:
                        data = data.split('</think>')[1].strip()
                    pprint(data)
                    texts_to_translate[text] = data
                    if debug:
                        print(f'[DEBUG] Получен перевод: {texts_to_translate[text]}')
                    break
                except Exception as e:
                    print(f'Ошибка при переводе "{text}": {e}. Повтор через 3 секунды.')
                    time.sleep(3)

        print(f'Всего токенов затрачено на перевод: {tokens_spended}')

        return texts_to_translate


    