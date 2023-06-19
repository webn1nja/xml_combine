# Cкрипт для объединения нескольких XML-файлов с наличием товара в один по правилам маркетплейса Озон с указанием складов

ver. 1.1

>This script is designed to combine several XML files with the availability of goods into one according to the rules of the Ozone marketplace with the indication of warehouses.

>Для получения содержимого предложенных url выполняется обход Cloudflare's anti-bot page

#### Установка виртуального окружения

-   `python3 -m venv venv` в Linux/macOS;
-   `python -m venv venv` или `py -3 -m venv venv` в Windows

#### Активируйте виртуальное окружение

Из директории xml_cashback выполните команду:
    -   Linux/macOS: `source venv/bin/activate`;
    -   Windows: ` venv\Scripts\activate.bat`.

#### Обновите пакетный менеджер
  При создании виртуального окружения будет использоваться та версия менеджера, которая была установлена вместе с Python. И это будет, скорее всего, не самая последняя версия, о чём вам и будет сообщаться каждый раз при обращении к нему.
  Обновить версию можно командой:

-   Windows: `python -m pip install --upgrade pip`;
-   Linux/macOS: `python3 -m pip install --upgrade pip`.


#### Установка зависимостей

`pip install -r requirements.txt`

#### Запуск скрипта

-   `python3 -m main.py` в Linux/macOS;
-   `python -m main.py` или `py -3 -m main.py` в Windows