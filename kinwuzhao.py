import random, re
import config
import jieqi
from bidict import bidict
from kinliuren import kinliuren

# 數字對應五行
num_to_element = {
    1: "水",
    2: "火",
    3: "木",
    4: "金",
    5: "土"
}

sixbeast_weakness = {"青龍":re.findall("..", "坤死兌害"),
"朱雀":re.findall("..", "坎死巽害"),
"螣蛇":re.findall("..", "坎死巽害"),
"勾陳":re.findall("..", "巽死巽害"),
"白虎":re.findall("..", "坎死離害"),
"玄武":re.findall("..", "巽死震害")}

guxu = dict(zip(config.liujiashun_dict().keys(), [
{"陽":{"孤":"戌", "虛":"辰"}, "陰": {"孤":"亥", "虛":"巳"}},
{"陽":{"孤":"申", "虛":"寅"}, "陰": {"孤":"酉", "虛":"卯"}},
{"陽":{"孤":"午", "虛":"子"}, "陰": {"孤":"未", "虛":"丑"}},
{"陽":{"孤":"辰", "虛":"戌"}, "陰": {"孤":"巳", "虛":"亥"}},
{"陽":{"孤":"寅", "虛":"申"}, "陰": {"孤":"卯", "虛":"酉"}},
{"陽":{"孤":"子", "虛":"午"}, "陰": {"孤":"丑", "虛":"未"}}]))

yy = {tuple(list("甲丙戊庚壬")):"陽", tuple(list("乙丁己辛癸")):"陰"}

general = dict(zip(list("子丑寅卯辰巳午未申酉戌亥"),list("子酉午卯子酉午卯子酉午卯")))
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
wangxiang = tuple("王相胎沒死囚廢休") 
trigrams = tuple("艮震巽離坤兌乾坎") 
jieqi_groups = [
    ("立春", "雨水", "驚蟄"),
    ("春分", "清明", "穀雨"),
    ("立夏", "小滿", "芒種"),
    ("夏至", "小暑", "大暑"),
    ("立秋", "處暑", "白露"),
    ("秋分", "寒露", "霜降"),
    ("立冬", "小雪", "大雪"),
    ("冬至", "小寒", "大寒")
]

# 定義二十四節氣
twenty_four_solar_terms = (
    "立春", "雨水", "驚蟄", "春分", "清明", "穀雨",  # 春季
    "立夏", "小滿", "芒種", "夏至", "小暑", "大暑",  # 夏季
    "立秋", "處暑", "白露", "秋分", "寒露", "霜降",  # 秋季
    "立冬", "小雪", "大雪", "冬至", "小寒", "大寒"   # 冬季
)

# 建立二十四節氣對應四季的 dictionary
solar_terms_by_season = {
    twenty_four_solar_terms[0:6]:{"關":"丑","籥":"巳"},   # 立春到穀雨
    twenty_four_solar_terms[6:12]:{"關":"辰","籥":"申"},  # 立夏到大暑
    twenty_four_solar_terms[12:18]:{"關":"未","籥":"亥"}, # 立秋到霜降
    twenty_four_solar_terms[18:24]:{"關":"戌","籥":"寅"}  # 立冬到大寒
}
zhi2gua = {
    '子': '坎', '寅': '震', '卯': '震', '辰': '巽', '巳': '巽', 
    '午': '離', '申': '兌', '酉': '兌', '戌': '乾', '亥': '乾', 
    '丑': '中', '未': '中'
}
#locknkey ={("正","二","三"):re.findall("..","關中籥離"),
#("四","五","六"):re.findall("..","關震籥兌"),
#("七","八","九"):re.findall("..","關離籥坎"),
#("十","冬","腊"):re.findall("..","關中籥震")}
locknkey ={("丑","寅","卯"):re.findall("..","關中籥離"),
("辰","巳","午"):re.findall("..","關震籥兌"),
("未","申","酉"):re.findall("..","關離籥坎"),
("戌","亥","子"):re.findall("..","關中籥震")}


def rotate_trigrams(base, shift):
    return base[shift:] + base[:shift]

jieqi_wangxiang = {
    jieqi: dict(zip(rotate_trigrams(trigrams, i), wangxiang))
    for i, jieqi in enumerate(jieqi_groups)
}

# 隨機分兩份，返回左一份
def random_split(total):
    if total <= 1:
        return 1
    return random.randint(1, total - 1)

# 主流程
def five_zhao_paipan(num, jq, cm, gz1, gz2):
    num = 0
    day_gan = gz1[0]
    if day_gan not in day_gan_to_beast:
        return {"錯誤": "日干不正確，請輸入：甲乙丙丁戊己庚辛壬癸"}
    base = 36
    result = {}
    # 六獸序列，循環分配六個位置
    beast_start = day_gan_to_beast[day_gan]
    start_index = six_beasts_order.index(beast_start)
    beast_seq = [six_beasts_order[(start_index + i) % len(six_beasts_order)] for i in range(6)]
    liuren_hour =  kinliuren.Liuren(jq, cm, gz1, gz2).result_m(0)
    sky2earth = bidict(liuren_hour["地轉天盤"])
    lnk = config.multi_key_dict_get(solar_terms_by_season, jq)
    lock = zhi2gua[sky2earth.inverse[lnk["關"]]]
    key = zhi2gua[sky2earth.inverse[lnk["籥"]]]
    g = zhi2gua[sky2earth.inverse[general[gz2[1]]]]
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
        get_gx = config.multi_key_dict_get(guxu, gz2)
        get_yy = get_gx.get(config.multi_key_dict_get(yy, gz2[0]))
        gu = zhi2gua[get_yy["孤"]]
        xu = zhi2gua[get_yy["虛"]]
        if idx == 0:
            relation = ""
            my_element = zhao_element
        else:
            relation = dict(zip(re.findall("..", "尅我我尅比和生我我生"),re.findall("..", "官鬼妻財兄弟父母子孫"))).get(config.multi_key_dict_get(config.wuxing_relation_2, my_element+zhao_element))
        result[label] = {
            "宮位": dict(zip("巽宮,震宮,離宮,中宮,兌宮,坎宮".split(","),"兆,木鄉,火鄉,土鄉,金鄉,水鄉".split(","))).get(gong),
            "旺相": config.multi_key_dict_get(jieqi_wangxiang, jq).get(gong[0].replace("中", "坤"), ""),
            "宮位1": gong[0], 
            "數字": zhao_num,
            "五行": zhao_element,
            "六獸": beast,
            "六獸死": "死" if sixbeast_weakness.get(beast)[0][0] == gong[0] else "",
            "六獸害": "害" if sixbeast_weakness.get(beast)[1][0] == gong[0] else "",
            "六親": relation,
            "孤": "孤" if gu == gong[0] else "",
            "虛": "虛" if xu == gong[0] else "",
            "關": "關" if lock == gong[0] else "",
            "籥": "籥" if key == gong[0] else "",
            "將軍": "將軍" if g == gong[0] else ""
        }

        remain -= zhao_num
        if remain <= 0:
            break
    return result


def gangzhi_paipan(gz_list, num, jq, cm):
    """以年月日時干支計算五兆。

    參數 ``gz_list`` 為 ``config.gangzhi`` 所傳回的前四項 [年, 月, 日, 時]。
    """
    if len(gz_list) < 4:
        return {"錯誤": "干支資料不足"}

    y, m, d, h, mi= gz_list
    if mi[0] not in day_gan_to_beast:
        return {"錯誤": "日干不正確，請輸入：甲乙丙丁戊己庚辛壬癸"}
    #lk = config.multi_key_dict_get(locknkey, mi[1])
    jz2num = dict(zip(config.jiazi(), range(1, 61)))
    beast_start = day_gan_to_beast[mi[0]]
    start_index = six_beasts_order.index(beast_start)
    beast_seq = [six_beasts_order[(start_index + i) % len(six_beasts_order)]
                 for i in range(6)]
    liuren_hour =  kinliuren.Liuren(jq, cm, h, mi).result_m(0)
    sky2earth = bidict(liuren_hour["地轉天盤"])
    lnk = config.multi_key_dict_get(solar_terms_by_season, jq)
    lock = zhi2gua[sky2earth.inverse[lnk["關"]]]
    key = zhi2gua[sky2earth.inverse[lnk["籥"]]]
    g = zhi2gua[sky2earth.inverse[general[mi[1]]]]
    get_gx = config.multi_key_dict_get(guxu, mi)
    get_yy = get_gx.get(config.multi_key_dict_get(yy, mi[0]))
    gu = zhi2gua[get_yy["孤"]]
    xu = zhi2gua[get_yy["虛"]]
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
            "宮位1": gong[0], 
            "旺相": config.multi_key_dict_get(jieqi_wangxiang, jq).get(gong[0].replace("中", "坤"), ""),
            "數字": zhao_num,
            "五行": zhao_element,
            "六獸": beast,
            "六獸死": "死" if sixbeast_weakness.get(beast)[0][0] == gong[0] else "",
            "六獸害": "害" if sixbeast_weakness.get(beast)[1][0] == gong[0] else "",
            "六親": relation,
            "關": "關" if lock == gong[0] else "",
            "籥": "籥" if key == gong[0] else "",
            "孤": "孤" if gu == gong[0] else "",
            "虛": "虛" if xu == gong[0] else "",
            "將軍": "將軍" if g == gong[0] else ""
        }

    return result


if __name__ == '__main__':
    dg = config.gangzhi(2025,6,27,11,24)[2][0]
    print(five_zhao_paipan(dg))
