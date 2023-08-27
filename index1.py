import json
import os


def up(file_name):
    return file_name.split(".")[0].upper().replace("-", "_")


def out(file_name):
    with open(f"./Files/json/{file_name}", encoding="utf-8") as f:
        data = json.loads(f.read())
    count = 0
    for i in data:
        for m, n in i.items():
            count += n["count"]
    print(f"{file_name} exist {count} item")
    for x, y in data[0].items():
        sd = "/".join(x.split("/")[:3])
        print(sd)
        ss = {up(file_name): {"count": count, "url": sd}}

    return ss


if __name__ == "__main__":
    files = os.listdir("./Files/json/")
    # print(files)
    ls = []
    for i in files:
        ls.append(out(i))

    with open("setting2.json", "w", encoding="utf-8") as f:
        a = f.write(json.dumps(ls, ensure_ascii=False, indent=2))
