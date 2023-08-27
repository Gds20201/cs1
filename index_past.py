import time
import json
import datetime
from lxml import etree
import random
from tqdm import tqdm
from utils import return_response, start_log, aioRequest, get_header
import os
import logging
import asyncio
import setting

CONCURRENCY = 20
semaphore = asyncio.Semaphore(CONCURRENCY)
start_log()

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def parse(text):
    html = etree.HTML(text)
    r1 = html.xpath('//div[@class="swiper-slide c-low--6"]')
    if len(r1) != 0:
        href = r1[0].xpath('.//div[@class="item"]//a[1]/@href')
        dic = {"href": href, "count": len(href)}
        return dic
    else:
        return None


async def download(session, data):
    global all_result, done_ls
    async with semaphore:
        logging.info(f'Crawling: {data["url"]}')
        try:
            async with session.get(url=data["url"], headers=get_header()) as response:
                content = await response.read()
                res = parse(content)
                if res:
                    rr = {data["url"]: res}
                    all_result.append(rr)
                    data["state"] = 2
                else:
                    data["state"] = 1
                done_ls.append(data)
        except Exception as e:
            print({"url": data["url"], "error": str(e)})


def out(file_name, num):
    with open(f"./Files/json/{file_name}", encoding="utf-8") as f:
        data = json.loads(f.read())
    count = 0
    for i in data:
        for m, n in i.items():
            count += n["count"]
    ss = up(file_name)
    print(
        f"{num: <3}: {file_name: <20} exist {count: >6} item {ss: <20}={setting.eval(ss)}"
    )
    # print()


def up(file_name):
    return file_name.split(".")[0].upper().replace("-", "_")


class IndexPast:
    def __init__(self, keyword) -> None:
        self.keyword = keyword
        self.log_path = f"./Files/log/{self.keyword}.log"
        self.json_path = f"./Files/json/{self.keyword}.json"
        self.text_path = f"./Files/text/{self.keyword}.json"
        with open("setting2.json", encoding="utf-8") as f:
            a = json.loads(f.read())
        print(f"|{'id': <4}|  {'name:': <20} |  {'count': <10} |  {'url': <10}")
        for i in range(1, len(a) + 1):
            b = [x for x in a[i - 1].items()][0]
            c = [y for y in b[1].values()]
            self.url = c[1]
            print(f"|{i: <4}|  {b[0]: <20} |  {c[0]: <10} |  {c[1]: <10}")
            print(self.url)

    def create_log(self):
        logger = logging.getLogger(self.keyword)
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(self.log_path)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s     | - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        with open(self.log_path, encoding="utf-8") as f:
            datas = f.readlines()
        if len(datas) == 0:
            logger.info("init")
        return logger

    def create_data_list(self):
        # 创建网站数据不可见列表
        if not os.path.exists(self.text_path):
            start_date = datetime.datetime(2010, 1, 1)
            end_date = datetime.datetime(2018, 1, 1)
            data_list = []
            base_url = f"https://{self.keyword}.com/"
            urls = base_url + "works/list/date/{}"
            current_date = start_date + datetime.timedelta(days=1)
            while current_date <= end_date:
                index_url = urls.format(current_date.strftime("%Y-%m-%d"))
                data_list.append({"url": index_url, "state": 0})
                current_date += datetime.timedelta(days=1)

            with open(self.text_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(data_list, indent=2, ensure_ascii=False))

    def create_new_list(self):
        # 创建网站数据可见列表
        text = return_response(f"https://{self.keyword}.com/works/date")
        html = etree.HTML(text)
        result = html.xpath('//ul[@class="p-accordion"]//li//a//@href')
        new_list = [{"url": i, "state": 0} for i in result]

        return new_list

    def index(self, num=30, data_list=None):
        if data_list:
            data_list = data_list[:]
        else:
            data_list = []
            with open(self.text_path, encoding="utf-8") as f:
                data = json.loads(f.read())
            for i in data:
                if i.get("state") == 0:
                    data_list.append(i)

        global all_result, done_ls
        if num != -1:
            data_list = data_list[:num]
        elif num == -1:
            data_list = data_list[:]
        if len(data_list) != 0:
            aio = aioRequest(asy_func=download)
            try:
                aio.start(data_list)
            except:
                pass
            if len(all_result) != 0:
                self.save(all_result)
            # print(done_ls)
            if len(done_ls) != 0:
                # with open(self.text_path, encoding="utf-8") as f:
                #     data = json.loads(f.read())
                for i in done_ls:
                    for j in data:
                        if i.get("url") == j.get("url"):
                            j["state"] = i["state"]
                with open(self.text_path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print("None data")

    def save(self, data):
        with open(self.json_path, encoding="utf-8") as f:
            old_data = json.loads(f.read())
            old_data.extend(data)
        with open(self.json_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(old_data, ensure_ascii=False, indent=2))

    def start(self, num=30, option=1):
        if not os.path.exists(self.json_path):
            with open(self.json_path, "w") as f:
                f.write(json.dumps([]))
        else:
            pass
        self.logger = self.create_log()
        if option == 1:
            self.create_data_list()
            self.index(num=num)
        elif option == 2:
            data_list = self.create_new_list()
            self.index(num=-1, data_list=data_list)

    def cs(self):
        self.__create_new_list()


if __name__ == "__main__":
    all_result = []
    done_ls = []
    s = "premium-beauty"
    a = IndexPast(s)
    # a.start(num=1000, option=1)
    # b = a.create_new_list()
    # print(b)
    pass
