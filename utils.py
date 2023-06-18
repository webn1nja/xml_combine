import hashlib
from datetime import datetime
from typing import Dict, TextIO
from xml.dom import minidom

import cfscrape
import pytz
import requests
from requests.exceptions import HTTPError

import vars


def get_initial_info() -> str:
    '''
    Функция инициирует скачивание файлов и формирует строку
    для детектирования изменений в дальнейшем.
    '''
    f_s = ''
    for key, value in vars.warehouses_and_links.items():
        wh_name = key
        for link in value:
            f_s += get_file_xml(link, wh_name)
    return f_s


def get_file_xml(link: str, wh_name: str) -> str:
    '''
    Функция скачивает файлы, приводит имена скачанных файлов к нужному формату
    и возвращает содержимое по ссылке.
    '''
    fname_index = link.rfind('/')
    fname = link[fname_index:]
    url = link
    USER_AGENT = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
                  'like Gecko) Chrome/50.0.2661.102 Safari/537.36')
    HTTP_HEADERS = {'User-Agent': USER_AGENT}
    BASE_URL = 'http://' + url.rsplit('/')[2]
    HTTP_HEADERS['Referer'] = BASE_URL
    HTTP_HEADERS['Content-Type'] = 'text/html; charset=utf-8'
    s = requests.session()
    s.headers = HTTP_HEADERS
    try:
        scraper_one = cfscrape.create_scraper(sess=s)
        r = scraper_one.get(url)
        r.encoding = 'utf-8'
        content = r.text
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        print(f'Содержимое ссылки загружено: {url}')

    with open(
        'xml_files' + '/' + wh_name + '-' + fname[1:],
        'w',
        encoding="utf-8"
    ) as f:
        f.write(content)
    return content


def check_counter(xml_file: str) -> bool:
    input_file_hash = hashlib.md5(xml_file.encode('utf-8')).hexdigest()

    with open(vars.hash_file, 'r', encoding="utf-8") as f:
        rez = f.read()

    if (rez == 0):
        print('Происходит первый запуск скрипта')
        return True
    elif (rez == input_file_hash):
        print('Изменений в фидах не обнаружено')
        return False
    else:
        print('Обнаружены изменения в фидах')
        return True


def save_hash(xml_file: str) -> TextIO:

    with open(vars.hash_file, 'w', encoding="utf-8") as f:
        f.write(hashlib.md5(xml_file.encode('utf-8')).hexdigest())


def get_current_timestring() -> str:
    moscow_time = datetime.now(pytz.timezone('Europe/Moscow'))
    return moscow_time.isoformat(timespec='seconds')


def xml_files_proccessing(filename, data):

    # получаем название склада
    start_index = filename.find('\\')
    stop_index = filename.rfind('-')

    wh_name = filename[start_index+1:stop_index]

    # обрабатываем xml
    mydoc = minidom.parse(filename)
    items = mydoc.getElementsByTagName('offer')

    for elem in items:
        offer_id = elem.attributes['id'].value
        if not data.get(offer_id):
            data[offer_id] = dict(warehouse_name=list())
            data[offer_id]['warehouse_name'].append(wh_name)

        else:
            data[offer_id]['warehouse_name'].append(wh_name)

        for node in elem.childNodes:
            if node.nodeName == 'price':
                data[offer_id]['price'] = node.firstChild.nodeValue
            elif node.nodeName == 'oldprice':
                data[offer_id]['oldprice'] = node.firstChild.nodeValue
            elif node.nodeName == 'count':
                data[offer_id]['count'] = node.firstChild.nodeValue


def generate_output_file(data: Dict[str, Dict]) -> TextIO:

    output_content = ''
    current_timestring = get_current_timestring()

    xml_start = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE yml_catalog SYSTEM "shops.dtd">
<yml_catalog date="{current_timestring}">
    <shop>
        <name>{vars.company_name}</name>
        <company>{vars.company_name}</company>
        <url>{vars.company_url}</url>
        <platform>BSM/Yandex/Market</platform>
        <version>2.5.7</version>
        <currencies>
            <currency id="RUR" rate="1"/>
        </currencies>
        <offers>
'''

    xml_end = '''\t\t</offers>
\t</shop>
</yml_catalog>
    '''

    output_content += xml_start

    for k, v in data.items():

        offer_xml_content_start = '''\t\t\t<offer id="{0}">
\t\t\t\t<price>{1}</price>\n'''
        outlets_start = '\t\t\t\t<outlets>\n'

        oldprice_xml = '\t\t\t\t<oldprice>{0}</oldprice>\n'

        outlet_xml = '\t\t\t\t\t<outlet instock="{0}" warehouse_name="{1}"/>\n'

        offer_xml_content_end = '''\t\t\t\t</outlets>
\t\t\t</offer>\n'''
        output_content += offer_xml_content_start.format(k, v['price'])

        if v.get('oldprice'):
            output_content += oldprice_xml.format(v['oldprice'])

        output_content += outlets_start
        for item in v['warehouse_name']:
            output_content += outlet_xml.format(v['count'], item)

        output_content += offer_xml_content_end

    output_content += xml_end

    with open(vars.output_file, 'w', encoding="utf-8") as f:
        f.write(output_content)
