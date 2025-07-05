import pandas as pd

def get_position(filename, user_id):

    df = pd.read_csv(f"./scripts/tables/{filename}.csv", encoding="utf-8-sig")


    df.sort_values(by="Сумма баллов", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    if user_id not in df["ID"].values:
        return {"message": f"❌ В рейтинге по направлению {filename} участник с таким ID"
                           f" не найден или отсутствует информации о сумме баллов."}

    user_row = df[df["ID"] == user_id].iloc[0]
    total_score = user_row["Сумма баллов"]
    priority = user_row["Приоритет"]


    # Обработка рангов
    def get_rank_with_user(df_sub):
        """Добавляет пользователя в подтаблицу, если его там нет, и считает позицию"""
        df_sub = df_sub.copy()
        if user_id not in df_sub["ID"].values:
            df_sub = pd.concat([df_sub, pd.DataFrame([user_row])], ignore_index=True)
        df_sub = df_sub.sort_values(by="Сумма баллов", ascending=False).reset_index(drop=True)
        rank_dict = {row["ID"]: idx + 1 for idx, row in df_sub.iterrows()}
        return rank_dict.get(user_id, None)

    # Все
    rank_all = get_rank_with_user(df)

    # Приоритет 1
    rank_p1 = get_rank_with_user(df[df["Приоритет"] == 1])

    # Приоритет 1 и 2
    rank_p12 = get_rank_with_user(df[df["Приоритет"].isin([1, 2])])

    # Приоритет 1–3
    rank_p123 = get_rank_with_user(df[df["Приоритет"].isin([1, 2, 3])])

    return {
        'Направление': filename,
        'Место участника ID': user_id,
        'Приоритет': priority,
        'Сумма баллов': total_score,
        'Среди приоритета 1': rank_p1,
        'Среди приоритета 1 и 2': rank_p12,
        'Среди приоритетов 1–3': rank_p123,
        'Среди всех': rank_all,
    }

