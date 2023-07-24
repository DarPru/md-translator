import os
from os import walk
from itertools import chain, zip_longest
from googletrans import Translator

translator = Translator(service_urls=["translate.googleapis.com"])
def translate_params(params, md_path, lang, params_to_ignore):
    translated_str = ''
    keys = [i.split(':', 1)[0] for i in params]
    vals = [''.join(filter(lambda el: el.replace('"', ''),i.split(':', 1)[1])) for i in params]
    dict_params = dict(zip(keys, vals))
    try:
        for k, v in dict_params.items():
            if k in params_to_ignore:
                translated_str += f'{k}:{v}'
                continue
            translated_str += f'{k}: '
            result = translator.translate(v, dest=lang)
            if result.text != '':
                translated_str += f'"{result.text}"\n'
            else:
                translated_str += f'\n'
    except Exception as ex:
        print(f'Ошибка перевода поля в файле {md_path}: {ex}')

    return translated_str

def translate_shortcode(str, lang, ignore_shortcodes_list):
    shortcode_name = str.split(' ')[0]
    shortcode_elem = str.split('"')[::2]
    shortcode_attrs = [i.replace('=', '').replace(shortcode_name, '').strip() for i in shortcode_elem if '>}}' not in i]
    lines_for_translate = str.split('"')[1::2]
    translated_lines = []
    for i, item in enumerate(lines_for_translate):
        if shortcode_attrs[i] in ignore_shortcodes_list:
            translated_lines.append(f'"{item}"')
        else:
            result = translator.translate(item, dest=lang)
            translated_lines.append(f'"{result.text}"')

    shortcode_str = ''.join(x for x in chain(*zip_longest(shortcode_elem, translated_lines)) if x is not None)
    return shortcode_str


def translate_content(content, md_path, lang, ignore_shortcodes_list):
    translated_str = ''
    try:
        for c in content:
            if c.startswith('{{</'):
                translated_str += c
                continue
            elif '{{<' in c:
                translated_str += f'{translate_shortcode(c, lang, ignore_shortcodes_list)}\n'
            else:
                result = translator.translate(c, dest=lang)
                translated_str += f'{result.text}\n'
    except Exception as ex:
        print(f'Ошибка перевода контента в файле {md_path}: {ex}')
    return translated_str


def translate_md(md_path, lang, params_to_ignore, ignore_shortcodes_list):
    folder_name = '/'.join(md_path.split('/')[1:-1])
    file_name = ''.join(md_path.split('/')[-1])
    print(f'Перевожу файл {folder_name}/{file_name}...')
    with open (md_path, 'r', encoding='utf-8') as file:
        file_lines = [line for line in file]
        file_lines.pop(0)
        params = file_lines[:file_lines.index('---\n')]
        content = file_lines[file_lines.index('---\n'):]

        translated_params = translate_params(params, md_path, lang, params_to_ignore)
        translated_content = translate_content(content, md_path, lang, ignore_shortcodes_list)
        if not os.path.exists(f'translations/{lang}/{folder_name}'):
            os.makedirs(f'translations/{lang}/{folder_name}')

        with open(f'translations/{lang}/{folder_name}/{file_name}', 'w', encoding='utf-8') as f:
            try:
                f.write('---\n')
                f.write(translated_params)
                f.write(translated_content)
            except Exception as ex:
                print(f'Ошибка файла {file_name}: {ex}')

def get_games_list(folder):
    w = walk(folder)
    arr = []
    for (dirpath, dirnames, filenames) in w:
        for item in filenames:
            char = '\\'

            arr.append(f"{dirpath.replace(char, '/')}/{item}")
    return arr

if __name__ == '__main__':
    folder = 'sourse'
    lang = 'uk'
    with open('ignore.txt', 'r', encoding='utf8') as ignore_list:
        ignores = ignore_list.read().split('\n')
        for i in ignores:
            if 'params' in i:
                ignore_params_list = [j.strip() for j in i.replace('params', '').replace('=', '').split(',')]
                continue
            if 'shortcodes' in i:
                ignore_shortcodes_list = [j.strip() for j in i.replace('shortcodes', '').replace('=', '').split(',')]
    files = get_games_list(folder)
    for f in files:
        translate_md(f, lang, ignore_params_list, ignore_shortcodes_list)
