# beautycity

## Как установить

Рекомендуемая версия питона: 3.10

1. Клонируйте репозиторий 
2. В терминале перейдите в корневую папку проекта
3. Скопируйте и запустите следующие команды:
    ```commandline
    python -m venv venv && venv/bin/pip install -U -r requirements.txt
    ```
#### Paзработчикам
4. Загрузите тестовые объекты в БД:
   ```commandline
   python manage.py migrate && python manage.py loaddata data/test_data.json
   ```
5. Создайте .env файл с содержимым:

```
TG_BOT_TOKEN=''
```
Создайте телеграм-бота с помощью BotFather и вставьте токен, который он вам пришлёт
.
## Как пользоваться

### Салонам

### Клиентам

## Цель проекта
