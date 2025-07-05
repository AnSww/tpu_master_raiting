import requests
from bs4 import BeautifulSoup

def parse_directions(url="https://apply.tpu.ru/spisok/index.html?pk_id=21&uroven_id=2&forma_id=1&organizaciya_id=33765&etap_id=1"):
    response = requests.get(url)
    response.encoding = 'utf-8'
    if response.status_code != 200:
        raise Exception(f"Ошибка запроса: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.select_one('table.table.table-bordered')

    directions = {}
    current_code = ""
    current_title = ""

    for row in table.select('tr'):
        tds = row.find_all('td')

        # если это строка с основным направлением
        if len(tds) >= 2 and not row.get('class'):
            current_code = tds[0].text.strip()
            current_title = tds[1].text.strip()

        # если есть ссылка на поднаправление
        link = row.select_one('a[href*="view.html?id="]')
        if link:
            href = link.get("href")
            text = link.text.strip()

            try:
                spec_id = int(href.split("id=")[1].split("&")[0])
                full_title = f"{current_code} {current_title} {text}"
                directions[spec_id] = full_title
            except Exception:
                continue

    return directions

res = parse_directions()
print(res)
'''for i in res:
    print(i, res[i])'''