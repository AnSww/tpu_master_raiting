import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from .directions import DIRECTIONS

BASE_URL = "https://apply.tpu.ru"

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_total_pages(PAGE_URL_TEMPLATE):
    """Определяем количество страниц по пагинации"""
    response = requests.get(PAGE_URL_TEMPLATE.format(page=1), headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    name = " - ".join(str(soup.find("div", class_="alert-info alert").find_all("b")[0]).split(' / ')).replace("<b>", "")[:-4]
    pagination = soup.select("ul.pagination li a")
    if not pagination:
        return name, 1
    pages = [int(a.text.strip()) for a in pagination if a.text.strip().isdigit()]
    return name, max(pages) if pages else 1

def parse_page(page_num, PAGE_URL_TEMPLATE):
    """Парсинг одной страницы"""
    url = PAGE_URL_TEMPLATE.format(page=page_num)
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="table-condensed")

    if not table:
        return []

    rows = table.find_all("tr")[1:]  # без заголовка
    data = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) != 8:
            continue

        participant_id = cols[0].text.strip()
        priority = cols[1].text.strip()
        agreement = cols[2].text.strip()
        total_score = cols[3].text.strip()
        if not total_score.isdigit():
            continue

        vi_score_div = cols[4].find("div")
        vi_score = vi_score_div.text.strip() if vi_score_div else cols[4].text.strip()

        id_score = cols[5].text.strip()
        status = cols[6].text.strip()
        date = cols[7].text.strip()



        data.append({
            "ID": participant_id,
            "Приоритет": priority,
            "Согласие": agreement,
            "Сумма баллов": total_score,
            "Баллы за ВИ": vi_score,
            "Баллы за ИД": id_score,
            "Статус": status,
            "Дата": date
        })

    return data

def main():

    for id in DIRECTIONS.keys():
        print(f"Формирование таблицы {DIRECTIONS[id]}.csv")
        all_data = []
        url = f"https://apply.tpu.ru/spisok/view.html?id={id}&page=" + "{page}&per-page=25"
        name, total_pages = get_total_pages(url)
        print(f"Всего страниц: {total_pages}")

        for page in range(1, total_pages + 1):
            print(f"Парсим страницу {page}...")
            page_data = parse_page(page, url)
            all_data.extend(page_data)
            time.sleep(1)  # чтобы не заспамить сервер
        df = pd.DataFrame(all_data)
        if not df.empty:
            df["Сумма баллов"] = pd.to_numeric(df["Сумма баллов"], errors="coerce")
            df = df.sort_values(by=["Приоритет", "Сумма баллов"], ascending=[True, False])
            df.to_csv(f"./scripts/tables/{name}.csv", index=False, encoding="utf-8-sig")
            print(f"Готово! Сохранено в {name}.csv")
        else:
            print(f'{name} пустой:(')



if __name__ == "__main__":
    while True:
        main()
        time.sleep(60*30)
