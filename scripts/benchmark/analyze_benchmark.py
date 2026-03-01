import os
import time
import struct
import glob

# --- НАСТРОЙКА ---
path_to_your_blocks_dir = 'D:\\BitcoinData\\blocks'


# ------------------

def parse_blocks_raw(data_dir):
    print(f"Запускаем НИЗКОУРОВНЕВЫЙ БЕНЧМАРК (V7) для: {data_dir}")

    # Магические байты Bitcoin Mainnet (начало каждого блока)
    MAGIC_BYTES = b'\xf9\xbe\xb4\xd9'

    # Находим все файлы blk*.dat
    # Используем glob для поиска файлов по маске
    search_path = os.path.join(data_dir, "blk*.dat")
    files = sorted(glob.glob(search_path))

    print(f"Найдено файлов данных (.dat): {len(files)}")

    start_time = time.time()

    total_blocks = 0
    total_bytes_read = 0

    for file_path in files:
        print(f"Чтение файла: {os.path.basename(file_path)}...")

        try:
            with open(file_path, 'rb') as f:
                while True:
                    # 1. Читаем "Магические байты" (4 байта)
                    magic = f.read(4)
                    if len(magic) < 4:
                        break  # Конец файла

                    if magic != MAGIC_BYTES:
                        # Если байты не магические, это часто "нули" в конце файла
                        # Просто пропускаем их
                        continue

                    # 2. Читаем размер блока (следующие 4 байта)
                    size_bytes = f.read(4)
                    if len(size_bytes) < 4:
                        break

                    # Расшифровываем размер (Little Endian unsigned int)
                    block_size = struct.unpack('<I', size_bytes)[0]

                    # 3. Читаем сам блок (block_size байт)
                    # Мы просто читаем их в память, имитируя загрузку
                    _ = f.read(block_size)

                    total_bytes_read += 8 + block_size  # 4 magic + 4 size + data
                    total_blocks += 1

                    if total_blocks % 10000 == 0:
                        current_time = time.time()
                        speed = total_bytes_read / (1024 * 1024) / (current_time - start_time)
                        print(f"--- Обработано блоков: {total_blocks}. Скорость: {speed:.2f} MB/s")

        except Exception as e:
            print(f"[!] Ошибка при чтении файла {file_path}: {e}")
            # Не прерываем работу, идем к следующему файлу
            continue

    end_time = time.time()
    elapsed_seconds = end_time - start_time
    elapsed_minutes = elapsed_seconds / 60
    total_gb = total_bytes_read / (1024 * 1024 * 1024)

    print("\n" + "=" * 40)
    print("ФИНАЛЬНЫЙ РЕЗУЛЬТАТ БЕНЧМАРКА (V7)")
    print("=" * 40)
    print(f"Всего обработано файлов: {len(files)}")
    print(f"Всего найдено блоков: {total_blocks}")
    print(f"Объем прочитанных данных: {total_gb:.2f} GB")
    print("-" * 20)
    print(f"Затраченное время: {elapsed_seconds:.2f} секунд")
    print(f"Это примерно: {elapsed_minutes:.2f} минут")
    print("=" * 40)


if __name__ == "__main__":
    parse_blocks_raw(path_to_your_blocks_dir)