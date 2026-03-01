import requests
import json
import datetime
import csv
import time

# --- НАСТРОЙКИ ---
rpc_user = 'admin'
rpc_password = '123'
rpc_url = 'http://127.0.0.1:8332'

# Диапазон блоков для скачивания (возьмем 5 блоков для теста)
START_BLOCK = 200000
END_BLOCK = 200005

# Имя файла для сохранения
FILENAME = 'blockchain_dataset.csv'


# ------------------

def rpc_call(method, params=[]):
    payload = {"method": method, "params": params, "jsonrpc": "1.0", "id": "extract"}
    try:
        response = requests.post(rpc_url, auth=(rpc_user, rpc_password), json=payload)
        if response.status_code != 200:
            return None
        return response.json()['result']
    except Exception as e:
        print(f"Ошибка RPC: {e}")
        return None


def get_input_details(txid, vout_index):
    # Та же функция для поиска отправителя
    prev_tx = rpc_call("getrawtransaction", [txid, 1])
    if not prev_tx:
        return "Unknown", 0.0
    try:
        target_output = prev_tx['vout'][vout_index]
        amount = target_output['value']
        addresses = target_output['scriptPubKey'].get('addresses', [])
        if not addresses:
            address = target_output['scriptPubKey'].get('address', 'Non-standard')
        else:
            address = addresses[0]
        return address, amount
    except Exception:
        return "ParseError", 0.0


# --- ГЛАВНЫЙ БЛОК ---
print(f"🚀 Начинаем сбор данных в файл: {FILENAME}")
print(f"Обработка блоков с {START_BLOCK} по {END_BLOCK}...")

# Открываем файл для записи
with open(FILENAME, mode='w', newline='', encoding='utf-8') as csv_file:
    # Создаем "писателя" CSV
    writer = csv.writer(csv_file)

    # Записываем ЗАГОЛОВКИ таблицы (Header)
    writer.writerow(['BlockHeight', 'Time', 'TxID', 'Type', 'Address', 'Amount_BTC'])

    total_tx_processed = 0

    # Цикл по блокам
    for height in range(START_BLOCK, END_BLOCK + 1):
        print(f"--- Обработка блока {height} ---")

        block_hash = rpc_call("getblockhash", [height])
        block = rpc_call("getblock", [block_hash, 2])

        if not block:
            print(f"Пропуск блока {height} (ошибка получения)")
            continue

        block_time = datetime.datetime.fromtimestamp(block['time'])

        # Цикл по транзакциям внутри блока
        for tx in block['tx']:
            txid = tx['txid']
            total_tx_processed += 1

            # 1. Записываем ВХОДЫ (Inputs) - Отправители
            for inp in tx['vin']:
                if 'coinbase' in inp:
                    # Это награда майнеру
                    writer.writerow([height, block_time, txid, 'COINBASE', 'New_Coins', 0])
                else:
                    prev_txid = inp['txid']
                    prev_vout = inp['vout']
                    addr, val = get_input_details(prev_txid, prev_vout)

                    # Запись строки в файл: Тип 'INPUT'
                    writer.writerow([height, block_time, txid, 'INPUT', addr, val])

            # 2. Записываем ВЫХОДЫ (Outputs) - Получатели
            for out in tx['vout']:
                val = out['value']
                script = out['scriptPubKey']
                if 'address' in script:
                    addr = script['address']
                elif 'addresses' in script:
                    addr = script['addresses'][0]
                else:
                    addr = "Non-standard"

                # Запись строки в файл: Тип 'OUTPUT'
                writer.writerow([height, block_time, txid, 'OUTPUT', addr, val])

print("=" * 40)
print(f"✅ Готово! Данные сохранены в {FILENAME}")
print(f"Всего обработано транзакций: {total_tx_processed}")
print("Теперь вы можете открыть этот файл в Excel.")