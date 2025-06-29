import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Это наш "виртуальный" чайник. В реальном приложении
# эти данные будут храниться в базе данных или получаться напрямую от устройства.
MY_KETTLE = {
    "id": "kettle-12345",  # ВАШ уникальный ID для этого устройства
    "name": "Электрический чайник",
    "description": "Мой умный чайник на кухне",
    "room": "Кухня",
    "type": "devices.types.kettle", # Тип устройства из документации Яндекса

    # Описываем, что умеет устройство (capabilities)
    "capabilities": [
        {
            # Умение включаться/выключаться
            "type": "devices.capabilities.on_off",
            "retrievable": True, # Можем ли мы запросить текущее состояние (вкл/выкл)
            "reportable": True, # Может ли устройство само сообщать об изменении состояния
            "parameters": {
                "split": False # False означает, что это единая функция вкл/выкл
            }
        },
        {
            # Умение устанавливать температуру
            "type": "devices.capabilities.range",
            "retrievable": True,
            "reportable": True,
            "parameters": {
                "instance": "temperature", # Указываем, что это диапазон для температуры
                "name": "температура",
                "unit": "unit.temperature.celsius", # Единица измерения - градусы Цельсия
                "random_access": True, # Можно установить любое значение из диапазона
                "range": {
                    "min": 40,
                    "max": 100,
                    "precision": 5 # Шаг изменения (40, 45, 50, ...)
                }
            }
        }
    ],

    # Информация о производителе (необязательно, но полезно)
    "device_info": {
        "manufacturer": "My DIY Devices",
        "model": "DIY-Kettle-v1",
        "hw_version": "1.0",
        "sw_version": "1.1"
    }
}


@app.route('/')
def health_check():
    """Проверка, что сервер жив (обязательный эндпоинт)."""
    return "I'm alive!", 200

@app.route('/v1.0/user/unlink', methods=['POST'])
def unlink_user():
    """Отвязка аккаунта пользователя (обязательный эндпоинт)."""
    # Здесь должна быть логика удаления токена пользователя из вашей системы
    request_id = request.headers.get('X-Request-Id', 'unknown')
    print(f"User unlinked! Request ID: {request_id}")
    return jsonify({"request_id": request_id}), 200


@app.route('/v1.0/user/devices', methods=['GET'])
def get_user_devices():
    """
    Основной эндпоинт. Отвечает на запрос Яндекса о списке устройств.
    Именно здесь мы "добавляем" наш чайник.
    """
    request_id = request.headers.get('X-Request-Id', 'unknown')
    print(f"Request for devices list. Request ID: {request_id}")

    # Формируем ответ в строгом соответствии с документацией
    response = {
        "request_id": request_id,
        "payload": {
            # В реальном приложении user_id нужно получить из Authorization хедера
            # и по нему найти устройства пользователя в вашей базе данных.
            "user_id": "some_user_id_from_your_system",
            "devices": [
                MY_KETTLE # Добавляем наш чайник в список
            ]
        }
    }

    return jsonify(response), 200

# TODO: Вам также нужно будет реализовать эндпоинты /v1.0/devices/query и /v1.0/devices/action
# для управления чайником и получения его состояния. Без них он будет виден, но неактивен.


if __name__ == '__main__':
    # Для теста запускаем локально. Для продакшена нужен WSGI сервер (gunicorn, uwsgi)
    # и HTTPS.
    app.run(host='0.0.0.0', port=5000)