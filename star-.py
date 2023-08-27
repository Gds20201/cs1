from utils import return_response
import time
import random
from lxml import etree
import json


def index():
    b_url = "https://ec.sod.co.jp/prime/videos/?id=STAR-{:03d}"
    for i in range(900, 1000):
        url = b_url.format(i)
        try:
            res = return_response(url)
        except Exception as e:
            print(f"{e} on {url}")
            break
        with open("./cs/STAR-{:03d}.html".format(i), "w", encoding="utf-8") as f:
            f.write(res)
        print(url)
        time.sleep(1)


def parse(file):
    html = etree.HTML(file)
    r1 = html.xpath('//div[@class="txt"]//strong//text()')
    dic = {}
    if len(r1) == 0:
        dic["title"] = html.xpath("//h1[2]//text()")[0]
        dic["cover"] = html.xpath('//*[@class="videos_samimg"]/a//@href')[0]
        dic["info"] = html.xpath("//article/text()")[0].strip()
        imgs = html.xpath('//*[@id="videos_samsbox"]//a//@href')
        if len(imgs) != 0:
            dic["imgs"] = imgs
        else:
            dic["imgs"] = ""
        data = html.xpath('//*[@id="v_introduction"]//tr')
        data_dic = {}
        for i in data:
            td = i.xpath(".//td//text()")
            if len(td) != 1:
                data_l = [j.strip() for j in td[1:] if len(j.strip()) != 0]
                if len(data_l) == 1:
                    data_l = data_l[0]
                data_dic[td[0]] = data_l
            else:
                data_dic[td[0]] = ""
        dic["data"] = data_dic
        return dic
    else:
        return None


# //*[@id="videos_toptable"]//div[1]//div[1]//a
# //*[@id="videos_toptable"]//div[1]//div[2]//article
# //*[@id="videos_samsbox"]//a
# //*[@id="v_introduction"]/tbody//tr//td


if __name__ == "__main__":
    # index()
    f1 = "cs\STAR-{:03d}.html"
    all_result = []
    for i in range(1, 1000):
        f2 = f1.format(i)
        with open(f2, encoding="utf-8") as f:
            a = f.read()
        s = parse(a)
        if s:
            all_result.append(s)
        # print(all_result)
    with open("aaa1.json", "w", encoding="utf-8") as ff:
        ff.write(json.dumps(all_result, ensure_ascii=False, indent=2))
    pass
