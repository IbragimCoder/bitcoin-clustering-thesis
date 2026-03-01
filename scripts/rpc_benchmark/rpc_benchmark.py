import requests
import json
import time

# --- НАСТРОЙКИ ---
rpc_user = 'admin'
rpc_password = '123'
rpc_url = 'http://127.0.0.1:8332'


# ------------------

def rpc_call(method, params=[]):
    payload = {
        "method": method,
        "params": params,
        "jsonrpc": "1.0",
        "id": "bench"
    }
    response = requests.post(rpc_url, auth=(rpc_user, rpc_password), json=payload)
    return response.json()['result']


print("🚀 Запускаем RPC БЕНЧМАРК (Обработка 1000 блоков)...")

start_time = time.time()
block_count = 0
tx_count = 0

# Начнем, например, с 100 000-го блока (там уже много транзакций)
start_height = 100000
end_height = 101000  # Обработаем 1000 блоков

try:
    for height in range(start_height, end_height):
        # Шаг 1: Получить ХЭШ блока по его высоте (номеру)
        block_hash = rpc_call("getblockhash", [height])

        # Шаг 2: Скачать сам блок (с транзакциями)
        # verbosity=2 означает "дай полную информацию о транзакциях"
        block = rpc_call("getblock", [block_hash, 2])

        block_count += 1
        tx_count += len(block['tx'])

        if block_count % 100 == 0:
            print(f"--- Обработано {block_count} блоков...")

    end_time = time.time()
    elapsed = end_time - start_time

    print("\n" + "=" * 40)
    print("📊 РЕЗУЛЬТАТЫ RPC БЕНЧМАРКА")
    print("=" * 40)
    print(f"Обработано блоков: {block_count}")
    print(f"Обработано транзакций: {tx_count}")
    print(f"Время выполнения: {elapsed:.2f} сек")
    print("-" * 20)
    print(f"Скорость: {block_count / elapsed:.2f} блоков/сек")
    print(f"Скорость: {tx_count / elapsed:.2f} транзакций/сек")
    print("=" * 40)

except Exception as e:
    print(f"❌ Ошибка: {e}")
    print("Убедитесь, что Bitcoin Core запущен!")