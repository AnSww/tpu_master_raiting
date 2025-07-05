import os
import pandas as pd
import re

# Путь к папке с CSV-файлами
folder_path = "tables"  # ← замени на свою папку

# Список всех файлов CSV
csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

all_rows = []

for file in csv_files:
    full_path = os.path.join(folder_path, file)
    direction = file.replace(".csv", "")  # Название направления

    df = pd.read_csv(full_path)

    for _, row in df.iterrows():
        # Извлекаем баллы ВИ (если есть "ООП (ВИ): 98", берём 98)
        vi_raw = str(row.get("Сумма баллов") or row.get("VI") or "")
        vi_match = re.search(r"\d+", vi_raw)
        vi_score = int(vi_match.group()) if vi_match else None

        all_rows.append({
            "ID": row.get("ID") or row.get("Id"),
            "Направление": direction,
            "Приоритет": row.get("Приоритет") or row.get("priority"),
            "Сумма баллов": vi_score
        })

# Собираем итоговую таблицу
result_df = pd.DataFrame(all_rows)

result_df = result_df.sort_values(by=["ID", "Приоритет"], ascending=[True, False])

# Сохраняем результат
result_df.to_csv("сводная_таблица.csv", index=False, encoding="utf-8-sig")
print("✅ Сводная таблица сохранена в файл: сводная_таблица.csv")
