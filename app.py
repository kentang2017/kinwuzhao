import datetime
import os, urllib
import streamlit as st
import pendulum as pdlm
from contextlib import contextmanager, redirect_stdout
from sxtwl import fromSolar
from io import StringIO
import streamlit.components.v1 as components
from streamlit.components.v1 import html
import config, jieqi
import kinwuzhao

# Initialize session state to control rendering
if 'render_default' not in st.session_state:
    st.session_state.render_default = True

@st.cache_data
def get_file_content_as_string(base_url, path):
    """從指定 URL 獲取文件內容並返回字符串"""
    url = base_url + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

@contextmanager
def st_capture(output_func):
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write
        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret
        stdout.write = new_write
        yield

def get_file_content_as_string(path):
    url = 'https://raw.githubusercontent.com/kentang2017/kinliuren/master/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

def get_file_content_as_string1(path):
    url = 'https://raw.githubusercontent.com/kentang2017/kinwuzhao/master/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

def render_svg(svg, num):
    if not svg or 'svg' not in svg.lower():
        st.error("Invalid SVG content provided")
        return
    
    # Replace \n with <tspan> for proper line breaks in SVG
    svg = svg.replace('\n', '</tspan><tspan x="0" dy="1.2em">')
    svg = svg.replace('<text', '<text x="0"')  # Ensure x is reset for tspans
    
    # Simplified HTML wrapper
    html_content = f"""
    <div style="display: flex; justify-content: center; align-items: center;">
        {svg}
    </div>
    """
    # Use num for height, but ensure it matches SVG dimensions
    components.html(html_content, height=num, width=num)

def lunar_date_d(y, m, d):
    day = fromSolar(y,m,d)
    return {"月": str(day.getLunarMonth())+"月", "日":str(day.getLunarDay())}
        
st.set_page_config(
    layout="wide",
    page_title="堅五兆 - 五兆排盘",
    page_icon="icon.png"
)
pan,example,guji,links,update = st.tabs([' 🧮排盤 ', ' 📜案例 ', ' 📚古籍 ',' 🔗連結 ',' 🆕更新 ' ])


# Map palace names to grid positions
grid = [
    ("兆", 0, 0), ("火鄉", 1, 0), ("", 2, 0),
    ("木鄉", 0, 1), ("土鄉", 1, 1), ("金鄉", 2, 1),
    ("", 0, 2),     ("水鄉", 1, 2), ("", 2, 2)
]

CELL_SIZE = 120  # size of each square
SVG_SIZE = CELL_SIZE * 3

def build_svg(data):
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_SIZE} {SVG_SIZE}" '
                 f'width="{SVG_SIZE}" height="{SVG_SIZE}">')
    
    # Add black background rectangle
    parts.append(f'<rect x="0" y="0" width="{SVG_SIZE}" height="{SVG_SIZE}" fill="black"/>')
    
    # Create a lookup by palace name
    by_palace = {v.get("宮位"): v for v in data.values()}

    # Add cell text (white text with tspans for multiline)
    for name, col, row in grid:
        x = col * CELL_SIZE + CELL_SIZE / 2
        y = row * CELL_SIZE + CELL_SIZE / 2 - 30  # Adjust y to center multiline text
        cell = by_palace.get(name, {})  # May be empty if not returned
        # Prepare text components
        texts = [
            name,  # Palace name (e.g., 巽宮)
            "{}{}".format(cell.get("五行", ""),cell.get("旺相", "")),  # Five Elements (e.g., 水)
            cell.get("六獸", ""),  # Six Beasts (e.g., 朱雀)
            cell.get("六親", "")   # Six Relations (e.g., 我本人)
        ]
        # Add text with tspans for multiline rendering
        parts.append(f'<text x="{x}" y="{y}" text-anchor="middle" '
                     f'dominant-baseline="hanging" font-size="14" fill="white">')
        for i, line in enumerate(texts):
            if line:  # Only add non-empty lines
                # Apply bold and larger font-size to 五行 (index 1)
                if i == 1:
                    parts.append(f'<tspan x="{x}" dy="{"1.2em" if i > 0 else "0"}" '
                                 f'font-size="18" font-weight="bold">{line}</tspan>')
                else:
                    parts.append(f'<tspan x="{x}" dy="{"1.2em" if i > 0 else "0"}">{line}</tspan>')
        parts.append('</text>')
    
    parts.append('</svg>')
    return ''.join(parts)

with st.sidebar:
    st.header("日期與時間選擇")
    
    # Set default datetime to current time in Asia/Hong_Kong (HKT)
    default_datetime = pdlm.now(tz='Asia/Hong_Kong')  # June 1, 2025, 12:49 PM HKT
    
    # Separate input fields for year, month, day, hour, minute
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        y = st.number_input(
            "年",
            min_value=0,
            max_value=2100,
            value=default_datetime.year,
            step=1,
            help="輸入年份 (1900-2100)"
        )
    with col2:
        m = st.number_input(
            "月",
            min_value=1,
            max_value=12,
            value=default_datetime.month,
            step=1,
            help="輸入月份 (1-12)"
        )
    with col3:
        d = st.number_input(
            "日",
            min_value=1,
            max_value=31,
            value=default_datetime.day,
            step=1,
            help="輸入日期 (1-31)"
        )
    
    col4, col5 = st.columns(2)
    with col4:
        h = st.number_input(
            "時",
            min_value=0,
            max_value=23,
            value=default_datetime.hour,
            step=1,
            help="輸入小時 (0-23)"
        )
    with col5:
        min = st.number_input(
            "分",
            min_value=0,
            max_value=59,
            value=default_datetime.minute,
            step=1,
            help="輸入分鐘 (0-59)"
        )
    col6 = st.columns(1)
    with col6[0]:  # Access the single column object
        number = st.number_input(
            "數字",
            min_value=0,
            max_value=9,
            value=0,
            step=1,
            help="輸入數字(0-9)"
        )
    # Quick-select buttons for common times
    st.subheader("快速選擇")
    if st.button("現在"):
        now = pdlm.now(tz='Asia/Hong_Kong')
        y = now.year
        m = now.month
        d = now.day
        h = now.hour
        min = now.minute
    
    # Display selected datetime
    try:
        selected_datetime = pdlm.datetime(y, m, d, h, min, tz='Asia/Hong_Kong')
        st.write(f"已選擇: {y}年{m}月{d}日 {h:02d}:{min:02d}")
    except ValueError:
        st.error("請輸入有效的日期和時間！")
    
    # 起盤方式選擇
    pan_mode = st.radio(
        "起盤方式",
        ["日干起盤", "時干起盤", "分干起盤" ,"干支起盤"],
        index=0,
    )

    # Timezone info
    st.caption("時區: Asia/Hong_Kong")

with links:
    st.header('連結')
    st.markdown(get_file_content_as_string("update.md"), unsafe_allow_html=True)

with guji:
    st.header('古籍')
    st.markdown(get_file_content_as_string1("guji.md"))

with update:
    st.header('更新')
    st.markdown(get_file_content_as_string1("log.md"))
  
with pan:
    st.header('堅五兆')
    cm = dict(zip(list(range(1, 13)), list("正二三四五六七八九十") + ["十一", "十二"])).get(
        int(lunar_date_d(y, m, d).get("月").replace("月", ""))
    )
    qgz = config.gangzhi(y, m, d, h, min)
    jq = jieqi.jq(y, m, d, h, min)
    if pan_mode == "干支起盤":
        pan = kinwuzhao.gangzhi_paipan(qgz, number, jq)
    if pan_mode == "日干起盤":
        pan = kinwuzhao.five_zhao_paipan(qgz[2][0], number, jq)
    if pan_mode == "時干起盤":
        pan = kinwuzhao.five_zhao_paipan(qgz[3][0], number, jq)
    if pan_mode == "分干起盤":
        pan = kinwuzhao.five_zhao_paipan(qgz[4][0], number, jq) 
    svg_markup = build_svg(pan)

    a = "日期︰{}年{}月{}日{}時{}分   數字:{}\n".format(y, m, d, h, min, number)
    c = "節氣︰{}\n".format(jq)
    d = "干支︰{}年 {}月 {}日 {}時 {}分\n".format(qgz[0], qgz[1], qgz[2], qgz[3], qgz[4])
    
    # Capture and display text output
    output2 = st.empty()
    with st_capture(output2.code):
        print(a + c + d)
    
    # Render SVG
    render_svg(svg_markup, 600)
