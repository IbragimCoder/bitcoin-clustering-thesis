import requests
import json
import datetime

# --- НАСТРОЙКИ ---
rpc_user = 'admin'
rpc_password = '123'
rpc_url = 'http://127.0.0.1:8332'


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


# Функция для поиска информации о "предыдущей" транзакции (чтобы найти Отправителя)
def get_input_details(txid, vout_index):
    # Запрашиваем "сырую" транзакцию, на которую ссылается вход
    prev_tx = rpc_call("getrawtransaction", [txid, 1])
    if not prev_tx:
        return "Unknown", 0.0

    # Находим нужный выход в той старой транзакции
    try:
        target_output = prev_tx['vout'][vout_index]
        amount = target_output['value']
        # Извлекаем адрес (в старых блоках формат может отличаться, ставим защиту)
        addresses = target_output['scriptPubKey'].get('addresses', [])
        if not addresses:
            # Иногда адрес записан просто как 'address' (в новых версиях Core)
            address = target_output['scriptPubKey'].get('address', 'Non-standard')
        else:
            address = addresses[0]
        return address, amount
    except Exception:
        return "ParseError", 0.0


# --- ГЛАВНЫЙ БЛОК ---
print("🚀 Запускаем извлечение данных...")

# Возьмем для примера блок № 200000 (это примерно 2012 год)
# Вы можете поменять это число на любое другое (до 290000, которые у нас есть)
target_block_height = 200000

block_hash = rpc_call("getblockhash", [target_block_height])
# verbosity=2 дает полную информацию о транзакциях сразу
block = rpc_call("getblock", [block_hash, 2])

if not block:
    print("Ошибка: Не удалось получить блок. Проверьте Bitcoin Core.")
    exit()

# Преобразуем время блока в понятный формат
block_time = datetime.datetime.fromtimestamp(block['time'])

print(f"\n=== БЛОК {target_block_height} ===")
print(f"Время: {block_time}")
print(f"Всего транзакций: {len(block['tx'])}")
print("=" * 60)

# Перебираем транзакции в блоке
for tx in block['tx']:
    txid = tx['txid']
    print(f"\n🔸 Транзакция: {txid}")

    # --- 1. ОТПРАВИТЕЛИ (Inputs / VIN) ---
    print("   ОТКУДА (Отправители):")
    input_total = 0.0

    for inp in tx['vin']:
        if 'coinbase' in inp:
            print("     [Награда майнеру (Coinbase)] -> Новые биткоины")
        else:
            # Чтобы узнать отправителя, мы берем txid предыдущей транзакции
            prev_txid = inp['txid']
            prev_vout = inp['vout']

            # И ищем адрес и сумму
            addr, val = get_input_details(prev_txid, prev_vout)
            print(f"     Address: {addr:34} | Sum: {val:.8f} BTC")
            input_total += val

    # --- 2. ПОЛУЧАТЕЛИ (Outputs / VOUT) ---
    print("   КУДА (Получатели):")
    output_total = 0.0

    for out in tx['vout']:
        val = out['value']
        # Пытаемся достать адрес
        script = out['scriptPubKey']
        # Bitcoin Core менял формат JSON. Проверяем оба варианта.
        if 'address' in script:
            addr = script['address']
        elif 'addresses' in script:
            addr = script['addresses'][0]
        else:
            addr = "Non-standard/Op_Return"

        print(f"     Address: {addr:34} | Sum: {val:.8f} BTC")
        output_total += val

    print(f"   --- Баланс: {output_total:.8f} BTC ---")

print("\n" + "=" * 60)
print("✅ Анализ блока завершен.")