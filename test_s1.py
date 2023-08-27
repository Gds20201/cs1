import time
import json
import datetime
from lxml import etree
import random
from tqdm import tqdm
from utils import return_response, start_log
import os
import logging


def create_log(keyword):
    logger = logging.getLogger(keyword)
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(f"{keyword}.log")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s     | - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # logger.info("1")
    return logger


def create_date_list(keyword):
    with open(f"{keyword}.log", encoding="utf-8") as f:
        dates = f.readlines()
    if len(dates) == 0:
        logger.info("init")
        logger.info("2010-01-01")
    last_date = dates[-1].strip()[-10:]
    s = datetime.datetime.strptime(last_date, "%Y-%m-%d")
    s = s.timetuple()
    start_date = datetime.datetime(s[0], s[1], s[2])
    end_date = datetime.datetime(2017, 12, 31)

    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime("%Y-%m-%d"))
        current_date += datetime.timedelta(days=1)
    return date_list


def save(data, keyword):
    with open(f"{keyword}.json", encoding="utf-8") as f:
        old_data = json.loads(f.read())
        old_data.extend(data)
    with open(f"{keyword}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(old_data, ensure_ascii=False, indent=2))


def index(date_list, keyword):
    base_url = f"https://{keyword}.com/"
    urls = base_url + "works/list/date/{}"
    all_result = []
    for i in tqdm(date_list[:30]):
        url = urls.format(i)
        try:
            res = return_response(url)
        except Exception as e:
            logger.warning(f"{e} on {url}")
            break
        html = etree.HTML(res)
        r1 = html.xpath('//div[@class="swiper-slide c-low--6"]')
        if len(r1) != 0:
            href = r1[0].xpath('.//div[@class="item"]//a[1]/@href')
            dic = {i: {"href": href, "count": len(href)}}
            all_result.append(dic)
            time.sleep(random.randint(2, 4))
        if len(all_result) >= 5:
            save(all_result, keyword)
            all_result = []
    # print(f"the last {date_list[-1]}")
    logger.info(f"{i}")
    if len(all_result) != 0:
        save(all_result, keyword)


def main(keyword):
    filename = f"{keyword}.json"
    if not os.path.isfile(filename):
        with open(filename, "w") as f:
            f.write(json.dumps([]))
    else:
        # print(f"The file {filename} already exists.")
        pass
    # logger = create_log(keyword)
    a = create_date_list(keyword)
    # print(a)

    index(a, keyword)


if __name__ == "__main__":
    s = "ideapocket"
    logger = create_log(s)
    main(s)

    pass
