import urllib.request
import streamlit as st
import pendulum as pdlm
import logging
from sxtwl import fromSolar
import streamlit.components.v1 as components
import config, jieqi
import kinwuzhao

logging.basicConfig(level=logging.ERROR)

# Initialize session state to control rendering
if 'render_default' not in st.session_state:
    st.session_state.render_default = True

# 定義基礎 URL

# Fetch files from the repositories' default branch
BASE_URL_KINWUZHAO = 'https://raw.githubusercontent.com/kentang2017/kinwuzhao/main/'
BASE_URL_KINLIUREN = 'https://raw.githubusercontent.com/kentang2017/kinliuren/master/'

@st.cache_data
def get_file_content_as_string(base_url, path):
    """從指定 URL 獲取文件內容並返回字符串"""
    url = base_url + path
    try:
        response = urllib.request.urlopen(url)
        return response.read().decode("utf-8")
    except Exception as e:
        logging.error("Error loading %s: %s", url, e)
        # Clear cached result to avoid stale data
        get_file_content_as_string.clear()
        return "Unable to load content."

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
tab_pan, tab_example, tab_guji, tab_links, tab_update = st.tabs([' 🧮排盤 ', ' 📜案例 ', ' 📚古籍 ', ' 🔗連結 ', ' 🆕更新 '])


# Map palace names to grid positions
grid = [
    ("兆", 0, 0),   ("火鄉", 1, 0), ("", 2, 0),
    ("木鄉", 0, 1), ("土鄉", 1, 1), ("金鄉", 2, 1),
    ("", 0, 2),     ("水鄉", 1, 2), ("", 2, 2)
]

CELL_SIZE = 140  # size of each square
SVG_SIZE = CELL_SIZE * 3

# Five-element color mapping for SVG display
ELEMENT_COLORS = {
    "木": "#4CAF50",  # Green
    "火": "#FF5252",  # Red
    "土": "#FFD740",  # Yellow/Amber
    "金": "#E0E0E0",  # White/Silver
    "水": "#42A5F5",  # Blue
}

def build_svg(data):
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_SIZE} {SVG_SIZE}" '
                 f'width="{SVG_SIZE}" height="{SVG_SIZE}">')

    # Add dark background
    parts.append(f'<rect x="0" y="0" width="{SVG_SIZE}" height="{SVG_SIZE}" fill="#1A1C23" rx="8"/>')

    # Create a lookup by palace name
    by_palace = {v.get("宮位"): v for v in data.values()}

    # Draw grid lines
    for i in range(1, 3):
        # Vertical lines
        parts.append(f'<line x1="{i * CELL_SIZE}" y1="0" x2="{i * CELL_SIZE}" y2="{SVG_SIZE}" '
                     f'stroke="#444" stroke-width="1"/>')
        # Horizontal lines
        parts.append(f'<line x1="0" y1="{i * CELL_SIZE}" x2="{SVG_SIZE}" y2="{i * CELL_SIZE}" '
                     f'stroke="#444" stroke-width="1"/>')

    # Outer border
    parts.append(f'<rect x="0" y="0" width="{SVG_SIZE}" height="{SVG_SIZE}" '
                 f'fill="none" stroke="#666" stroke-width="2" rx="8"/>')

    # Add cell text
    for name, col, row in grid:
        cx = col * CELL_SIZE + CELL_SIZE / 2
        cy = row * CELL_SIZE + 20
        cell = by_palace.get(name, {})

        element = cell.get("五行", "")
        element_color = ELEMENT_COLORS.get(element, "#E0E0E0")

        # Prepare text lines
        texts = [
            name,
            "{}{}".format(element, cell.get("旺相", "")),
            "{}{}{}".format(cell.get("六獸", ""), cell.get("六獸死", ""), cell.get("六獸害", "")),
            cell.get("六親", ""),
            "{}{}{}{}".format(cell.get("關", ""), cell.get("籥", ""), cell.get("孤", ""), cell.get("虛", "")),
        ]

        parts.append(f'<text x="{cx}" y="{cy}" text-anchor="middle" '
                     f'dominant-baseline="hanging" font-size="14" fill="#E0E0E0">')
        for i, line in enumerate(texts):
            if line:
                dy = "1.4em" if i > 0 else "0"
                if i == 0:
                    # Palace name: bold, slightly larger
                    parts.append(f'<tspan x="{cx}" dy="{dy}" font-size="15" '
                                 f'font-weight="bold" fill="#BDBDBD">{line}</tspan>')
                elif i == 1:
                    # Five element + prosperity: colored and bold
                    parts.append(f'<tspan x="{cx}" dy="{dy}" font-size="18" '
                                 f'font-weight="bold" fill="{element_color}">{line}</tspan>')
                else:
                    parts.append(f'<tspan x="{cx}" dy="{dy}">{line}</tspan>')
        parts.append('</text>')

    parts.append('</svg>')
    return ''.join(parts)

with st.sidebar:
    st.header("📅 日期與時間選擇")

    # Set default datetime to current time in Asia/Hong_Kong (HKT)
    default_datetime = pdlm.now(tz='Asia/Hong_Kong')

    # Quick-select for current time using session_state
    if st.button("⏱ 使用現在時間", use_container_width=True):
        now = pdlm.now(tz='Asia/Hong_Kong')
        st.session_state['input_y'] = now.year
        st.session_state['input_m'] = now.month
        st.session_state['input_d'] = now.day
        st.session_state['input_h'] = now.hour
        st.session_state['input_min'] = now.minute
        st.rerun()

    # Separate input fields for year, month, day, hour, minute
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        y = st.number_input(
            "年",
            min_value=0,
            max_value=2100,
            value=st.session_state.get('input_y', default_datetime.year),
            step=1,
            help="輸入年份 (0-2100)"
        )
    with col2:
        m = st.number_input(
            "月",
            min_value=1,
            max_value=12,
            value=st.session_state.get('input_m', default_datetime.month),
            step=1,
            help="輸入月份 (1-12)"
        )
    with col3:
        d_input = st.number_input(
            "日",
            min_value=1,
            max_value=31,
            value=st.session_state.get('input_d', default_datetime.day),
            step=1,
            help="輸入日期 (1-31)"
        )

    col4, col5 = st.columns(2)
    with col4:
        h = st.number_input(
            "時",
            min_value=0,
            max_value=23,
            value=st.session_state.get('input_h', default_datetime.hour),
            step=1,
            help="輸入小時 (0-23)"
        )
    with col5:
        mi = st.number_input(
            "分",
            min_value=0,
            max_value=59,
            value=st.session_state.get('input_min', default_datetime.minute),
            step=1,
            help="輸入分鐘 (0-59)"
        )

    number = st.number_input(
        "數字",
        min_value=0,
        max_value=90,
        value=0,
        step=1,
        help="輸入數字 (0-90)"
    )

    st.divider()

    # Display selected datetime
    try:
        selected_datetime = pdlm.datetime(y, m, d_input, h, mi, tz='Asia/Hong_Kong')
        st.info(f"📆 已選擇: {y}年{m}月{d_input}日 {h:02d}:{mi:02d}")
    except ValueError:
        st.error("請輸入有效的日期和時間！")

    # 起盤方式選擇
    pan_mode = st.radio(
        "🔮 起盤方式",
        ["日干起盤", "時干起盤", "分干起盤", "干支起盤"],
        index=0,
    )

    # Timezone info
    st.caption("🌏 時區: Asia/Hong_Kong")

with tab_links:
    st.header('連結')
    st.markdown(get_file_content_as_string(BASE_URL_KINLIUREN, "update.md"), unsafe_allow_html=True)

with tab_example:
    st.header('案例')
    st.markdown(get_file_content_as_string(BASE_URL_KINWUZHAO, "example.md"))

with tab_guji:
    st.header('古籍')
    st.markdown(get_file_content_as_string(BASE_URL_KINWUZHAO, "guji.md"))
                
with tab_update:
    st.header('更新')
    st.markdown(get_file_content_as_string(BASE_URL_KINWUZHAO, "log.md"))

  
with tab_pan:
    st.header('堅五兆')
    cm = dict(zip(list(range(1, 13)), list("正二三四五六七八九十") + ["十一", "十二"])).get(
        int(lunar_date_d(y, m, d_input).get("月").replace("月", ""))
    )
    qgz = config.gangzhi(y, m, d_input, h, mi)
    jq = jieqi.jq(y, m, d_input, h, mi)
    lunar_month = config.lunar_date_d(y, m, d_input)["農曆月"][0]
    if number > 9:
        number = number % 9
    if pan_mode == "干支起盤":
        result = kinwuzhao.gangzhi_paipan(qgz, number, jq, lunar_month)
    if pan_mode == "日干起盤":
        result = kinwuzhao.five_zhao_paipan(number, jq, lunar_month, qgz[1], qgz[2])
    if pan_mode == "時干起盤":
        result = kinwuzhao.five_zhao_paipan(number, jq, lunar_month, qgz[2], qgz[3])
    if pan_mode == "分干起盤":
        result = kinwuzhao.five_zhao_paipan(number, jq, lunar_month, qgz[3], qgz[4])
    svg_markup = build_svg(result)

    # Display divination info in structured columns
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown(f"**🔮 起盤模式:** {pan_mode}")
        st.markdown(f"**📆 日期:** {y}年{m}月{d_input}日 {h:02d}時{mi:02d}分")
    with info_col2:
        st.markdown(f"**🌿 節氣:** {jq}")
        st.markdown(f"**🔢 干支:** {qgz[0]}年 {qgz[1]}月 {qgz[2]}日 {qgz[3]}時 {qgz[4]}分")

    st.divider()

    # Render SVG
    render_svg(svg_markup, 600)
