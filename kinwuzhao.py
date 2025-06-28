import random, re
import config

# 數字對應五行
num_to_element = {
    1: "水",
    2: "火",
    3: "木",
    4: "金",
    5: "土"
}

# 六獸序列
six_beasts_order = ["青龍", "朱雀", "螣蛇", "勾陳", "白虎", "玄武"]

# 日干對應起六獸首位
day_gan_to_beast = {
    "甲": "青龍",
    "乙": "青龍",
    "丙": "朱雀",
    "丁": "朱雀",
    "戊": "勾陳",
    "己": "勾陳",
    "庚": "白虎",
    "辛": "白虎",
    "壬": "玄武",
    "癸": "玄武"
}

# 隨機分兩份，返回左一份
def random_split(total):
    if total <= 1:
        return 1
    return random.randint(1, total - 1)

# 主流程
def five_zhao_paipan(day_gan, num):
    num = 0
    if day_gan not in day_gan_to_beast:
        return {"錯誤": "日干不正確，請輸入：甲乙丙丁戊己庚辛壬癸"}

    base = 36
    result = {}

    # 六獸序列，循環分配六個位置
    beast_start = day_gan_to_beast[day_gan]
    start_index = six_beasts_order.index(beast_start)
    beast_seq = [six_beasts_order[(start_index + i) % len(six_beasts_order)] for i in range(6)]

    positions = [
        ("巽宮", "兆"),
        ("震宮", "木鄉"),
        ("離宮", "火鄉"),
        ("中宮", "土鄉"),
        ("兌宮", "金鄉"),
        ("坎宮", "水鄉")
    ]

    remain = base
    my_element = ""

    for idx, (gong, label) in enumerate(positions):
        left = random_split(remain)
        zhao_num = left % 5
        zhao_num = zhao_num if zhao_num != 0 else 5
        zhao_element = num_to_element[zhao_num]
        beast = beast_seq[idx]

        if idx == 0:
            relation = ""
            my_element = zhao_element
        else:
            relation = dict(zip(re.findall("..", "尅我我尅比和生我我生"),re.findall("..", "官鬼妻財兄弟父母子孫"))).get(config.multi_key_dict_get(config.wuxing_relation_2, my_element+zhao_element))
        result[label] = {
            "宮位": dict(zip("巽宮,震宮,離宮,中宮,兌宮,坎宮".split(","),"兆,木鄉,火鄉,土鄉,金鄉,水鄉".split(","))).get(gong),
            "數字": zhao_num,
            "五行": zhao_element,
            "六獸": beast,
            "六親": relation
        }

        remain -= zhao_num
        if remain <= 0:
            break
    return result


def gangzhi_paipan(gz_list, num):
    """以年月日時干支計算五兆。

    參數 ``gz_list`` 為 ``config.gangzhi`` 所傳回的前四項 [年, 月, 日, 時]。
    """
    if len(gz_list) < 4:
        return {"錯誤": "干支資料不足"}

    y, m, d, h, mi= gz_list
    if mi not in day_gan_to_beast:
        return {"錯誤": "日干不正確，請輸入：甲乙丙丁戊己庚辛壬癸"}

    jz2num = dict(zip(config.jiazi(), range(1, 61)))
    beast_start = day_gan_to_beast[day_gan]
    start_index = six_beasts_order.index(beast_start)
    beast_seq = [six_beasts_order[(start_index + i) % len(six_beasts_order)]
                 for i in range(6)]

    positions = [
        ("巽宮", "兆", [y, m, d, h, mi, num]),
        ("震宮", "木鄉", [m, d, h, mi, num]),
        ("離宮", "火鄉", [d, h, mi, num]),
        ("中宮", "土鄉", [h, mi, num]),
        ("兌宮", "金鄉", [mi, num]),
        ("坎宮", "水鄉", [num])
    ]

    result = {}
    my_element = ""

    for idx, (gong, label, parts) in enumerate(positions):
        # ``parts`` may include an integer ``num`` provided by the user. The
        # mapping ``jz2num`` only contains keys for traditional 60 ``甲子``
        # values, so directly indexing with ``num`` would raise ``KeyError``.
        # Use ``dict.get`` to treat non-``甲子`` entries as their numeric
        # values when calculating ``total``.
        total = sum(jz2num.get(i, i) for i in parts)
        zhao_num = total % 5
        zhao_num = zhao_num if zhao_num != 0 else 5
        zhao_element = num_to_element[zhao_num]
        beast = beast_seq[idx]

        if idx == 0:
            relation = ""
            my_element = zhao_element
        else:
            relation = dict(zip(re.findall("..", "尅我我尅比和生我我生"),
                                re.findall("..", "官鬼妻財兄弟父母子孫")))\
                .get(config.multi_key_dict_get(config.wuxing_relation_2,
                                              my_element + zhao_element))

        result[label] = {
            "宮位": dict(zip(
                "巽宮,震宮,離宮,中宮,兌宮,坎宮".split(","),
                "兆,木鄉,火鄉,土鄉,金鄉,水鄉".split(","))).get(gong),
            "數字": zhao_num,
            "五行": zhao_element,
            "六獸": beast,
            "六親": relation,
        }

    return result


if __name__ == '__main__':
    dg = config.gangzhi(2025,6,27,11,24)[2][0]
    print(five_zhao_paipan(dg))
