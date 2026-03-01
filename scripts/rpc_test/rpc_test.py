import requests
import json

# --- НАСТРОЙКИ (Точно как в файле bitcoin.conf) ---
rpc_user = 'admin'
rpc_password = '123'
rpc_url = 'http://127.0.0.1:8332'  # Стандартный порт Bitcoin Core
# --------------------------------------------------

print("📡 Посылаем сигнал 'Официанту' (Bitcoin Core)...")

# Формируем "Заказ" (JSON-RPC запрос)
# Мы просим выполнить команду 'getblockchaininfo'
payload = {
    "method": "getblockchaininfo",
    "params": [],
    "jsonrpc": "1.0",
    "id": "test_connection"
}

try:
    # Отправляем запрос
    response = requests.post(
        rpc_url,
        auth=(rpc_user, rpc_password),
        json=payload
    )

    # Проверяем статус
    if response.status_code == 200:
        print("✅ УСПЕХ! Связь установлена.")
        print("Вот что ответил Bitcoin Core:")

        # Красиво выводим ответ
        data = response.json()
        result = data['result']

        print("-" * 30)
        print(f"Цепочка: {result['chain']}")
        print(f"Количество блоков: {result['blocks']}")
        print(f"Размер на диске: {result['size_on_disk'] / (1024 ** 3):.2f} GB")
        print("-" * 30)
    else:
        print(f"❌ Ошибка доступа! Код: {response.status_code}")
        print("Проверьте логин/пароль в bitcoin.conf")

except Exception as e:
    print(f"❌ Не удалось подключиться: {e}")
    print("Убедитесь, что Bitcoin Core запущен!")