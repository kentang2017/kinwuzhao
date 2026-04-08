# -*- coding: utf-8 -*-
"""堅五兆 Streamlit 應用主程式。

移除 urllib.request raw github 載入，改為本地 import。
加強輸入驗證、錯誤處理與 session_state 管理。
增加「手動輸入分裂數」功能。
"""

from __future__ import annotations

import logging
from pathlib import Path

import pendulum as pdlm
import streamlit as st
import streamlit.components.v1 as components
from sxtwl import fromSolar

import config
import jieqi
import kinwuzhao

logging.basicConfig(level=logging.ERROR)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Initialize session state to control rendering
if "render_default" not in st.session_state:
    st.session_state.render_default = True


def _read_local_md(filename: str) -> str:
    """讀取專案根目錄下的 Markdown 文件。"""
    path = Path(__file__).parent / filename
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"⚠️ 找不到檔案: {filename}"


def render_svg(svg: str, num: int) -> None:
    """將 SVG 標記渲染為 Streamlit HTML 元件。"""
    if not svg or "svg" not in svg.lower():
        st.error("Invalid SVG content provided")
        return

    svg = svg.replace("\n", '</tspan><tspan x="0" dy="1.2em">')
    svg = svg.replace("<text", '<text x="0"')

    html_content = f"""
    <div style="display: flex; justify-content: center; align-items: center;">
        {svg}
    </div>
    """
    components.html(html_content, height=num, width=num)


def lunar_date_d(y: int, m: int, d: int) -> dict[str, str]:
    """取得農曆月日資訊。"""
    day = fromSolar(y, m, d)
    return {"月": f"{day.getLunarMonth()}月", "日": str(day.getLunarDay())}


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    layout="wide",
    page_title="堅五兆 - 五兆排盘",
    page_icon="icon.png",
)

tab_pan, tab_example, tab_guji, tab_links, tab_update = st.tabs(
    [" 🧮排盤 ", " 📜案例 ", " 📚古籍 ", " 🔗連結 ", " 🆕更新 "]
)

# ---------------------------------------------------------------------------
# SVG grid builder
# ---------------------------------------------------------------------------

grid = [
    ("兆", 0, 0),    ("火鄉", 1, 0), ("", 2, 0),
    ("木鄉", 0, 1),  ("土鄉", 1, 1), ("金鄉", 2, 1),
    ("", 0, 2),      ("水鄉", 1, 2), ("", 2, 2),
]

CELL_SIZE = 140
SVG_SIZE = CELL_SIZE * 3

ELEMENT_COLORS = {
    "木": "#4CAF50",
    "火": "#FF5252",
    "土": "#FFD740",
    "金": "#E0E0E0",
    "水": "#42A5F5",
}


def build_svg(data: dict) -> str:
    """組裝九宮格 SVG 排盤圖。"""
    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_SIZE} {SVG_SIZE}" '
        f'width="{SVG_SIZE}" height="{SVG_SIZE}">'
    )
    parts.append(
        f'<rect x="0" y="0" width="{SVG_SIZE}" height="{SVG_SIZE}" fill="#1A1C23" rx="8"/>'
    )

    by_palace = {v.get("宮位"): v for v in data.values()}

    for i in range(1, 3):
        parts.append(
            f'<line x1="{i * CELL_SIZE}" y1="0" x2="{i * CELL_SIZE}" y2="{SVG_SIZE}" '
            f'stroke="#444" stroke-width="1"/>'
        )
        parts.append(
            f'<line x1="0" y1="{i * CELL_SIZE}" x2="{SVG_SIZE}" y2="{i * CELL_SIZE}" '
            f'stroke="#444" stroke-width="1"/>'
        )

    parts.append(
        f'<rect x="0" y="0" width="{SVG_SIZE}" height="{SVG_SIZE}" '
        f'fill="none" stroke="#666" stroke-width="2" rx="8"/>'
    )

    for name, col, row in grid:
        cx = col * CELL_SIZE + CELL_SIZE / 2
        cy = row * CELL_SIZE + 20
        cell = by_palace.get(name, {})
        element = cell.get("五行", "")
        element_color = ELEMENT_COLORS.get(element, "#E0E0E0")

        texts = [
            name,
            f"{element}{cell.get('旺相', '')}",
            f"{cell.get('六獸', '')}{cell.get('六獸死', '')}{cell.get('六獸害', '')}",
            cell.get("六親", ""),
            f"{cell.get('關', '')}{cell.get('籥', '')}{cell.get('孤', '')}{cell.get('虛', '')}",
        ]

        parts.append(
            f'<text x="{cx}" y="{cy}" text-anchor="middle" '
            f'dominant-baseline="hanging" font-size="14" fill="#E0E0E0">'
        )
        for i, line in enumerate(texts):
            if line:
                dy = "1.4em" if i > 0 else "0"
                if i == 0:
                    parts.append(
                        f'<tspan x="{cx}" dy="{dy}" font-size="15" '
                        f'font-weight="bold" fill="#BDBDBD">{line}</tspan>'
                    )
                elif i == 1:
                    parts.append(
                        f'<tspan x="{cx}" dy="{dy}" font-size="18" '
                        f'font-weight="bold" fill="{element_color}">{line}</tspan>'
                    )
                else:
                    parts.append(f'<tspan x="{cx}" dy="{dy}">{line}</tspan>')
        parts.append("</text>")

    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("📅 日期與時間選擇")

    default_datetime = pdlm.now(tz="Asia/Hong_Kong")

    if st.button("⏱ 使用現在時間", use_container_width=True):
        now = pdlm.now(tz="Asia/Hong_Kong")
        st.session_state["input_y"] = now.year
        st.session_state["input_m"] = now.month
        st.session_state["input_d"] = now.day
        st.session_state["input_h"] = now.hour
        st.session_state["input_min"] = now.minute
        st.rerun()

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        y = st.number_input(
            "年",
            min_value=1,
            max_value=2100,
            value=st.session_state.get("input_y", default_datetime.year),
            step=1,
            help="輸入年份 (1-2100)",
        )
    with col2:
        m = st.number_input(
            "月",
            min_value=1,
            max_value=12,
            value=st.session_state.get("input_m", default_datetime.month),
            step=1,
            help="輸入月份 (1-12)",
        )
    with col3:
        d_input = st.number_input(
            "日",
            min_value=1,
            max_value=31,
            value=st.session_state.get("input_d", default_datetime.day),
            step=1,
            help="輸入日期 (1-31)",
        )

    col4, col5 = st.columns(2)
    with col4:
        h = st.number_input(
            "時",
            min_value=0,
            max_value=23,
            value=st.session_state.get("input_h", default_datetime.hour),
            step=1,
            help="輸入小時 (0-23)",
        )
    with col5:
        mi = st.number_input(
            "分",
            min_value=0,
            max_value=59,
            value=st.session_state.get("input_min", default_datetime.minute),
            step=1,
            help="輸入分鐘 (0-59)",
        )

    number = st.number_input(
        "數字",
        min_value=0,
        max_value=90,
        value=0,
        step=1,
        help="輸入數字 (0-90)",
    )

    st.divider()

    # Date validation
    valid_date = True
    try:
        selected_datetime = pdlm.datetime(y, m, d_input, h, mi, tz="Asia/Hong_Kong")
        st.info(f"📆 已選擇: {y}年{m}月{d_input}日 {h:02d}:{mi:02d}")
    except ValueError:
        st.error("請輸入有效的日期和時間！")
        valid_date = False

    # 起盤方式選擇
    pan_mode = st.radio(
        "🔮 起盤方式",
        ["日干起盤", "時干起盤", "分干起盤", "干支起盤", "唐代正法揲筮"],
        index=0,
    )

    # 手動折竹輸入（僅在隨機/唐代正法模式下顯示）
    manual_splits: list[int] | None = None
    if pan_mode in ("日干起盤", "時干起盤", "分干起盤", "唐代正法揲筮"):
        use_manual = st.checkbox("🎋 手動輸入分裂數（傳統折竹體驗）")
        if use_manual:
            st.caption("依序輸入 6 次折竹數（每次從剩餘算子中取走的數量）")
            split_cols = st.columns(6)
            manual_splits = []
            labels = ["兆", "木鄉", "火鄉", "土鄉", "金鄉", "水鄉"]
            for i, sc in enumerate(split_cols):
                with sc:
                    val = st.number_input(
                        labels[i],
                        min_value=1,
                        max_value=35,
                        value=6,
                        step=1,
                        key=f"split_{i}",
                    )
                    manual_splits.append(val)

    st.caption("🌏 時區: Asia/Hong_Kong")


# ---------------------------------------------------------------------------
# Content tabs (local file reads, no urllib)
# ---------------------------------------------------------------------------

with tab_links:
    st.header("連結")
    st.markdown(
        "- [堅六壬 Kinliuren](https://github.com/kentang2017/kinliuren)\n"
        "- [堅奇門 Kinqimen](https://github.com/kentang2017/kinqimen)\n"
        "- [堅太乙 Kintaiyi](https://github.com/kentang2017/kintaiyi)"
    )

with tab_example:
    st.header("案例")
    st.markdown(_read_local_md("example.md"))

with tab_guji:
    st.header("古籍")
    st.markdown(_read_local_md("guji.md"))

with tab_update:
    st.header("更新")
    st.markdown(_read_local_md("log.md"))


# ---------------------------------------------------------------------------
# Main divination panel
# ---------------------------------------------------------------------------

with tab_pan:
    st.header("堅五兆")

    if not valid_date:
        st.warning("請先在側邊欄輸入有效的日期與時間。")
        st.stop()

    try:
        cm = dict(
            zip(range(1, 13), list("正二三四五六七八九十") + ["十一", "十二"])
        ).get(int(lunar_date_d(y, m, d_input).get("月", "1月").replace("月", "")))

        qgz = config.gangzhi(y, m, d_input, h, mi)
        jq_val = jieqi.jq(y, m, d_input, h, mi)
        lunar_month = config.lunar_date_d(y, m, d_input)["農曆月"][0]

        if number > 9:
            number = number % 9

        result: dict = {}

        if pan_mode == "干支起盤":
            result = kinwuzhao.gangzhi_paipan(qgz, number, jq_val, lunar_month)
        elif pan_mode == "日干起盤":
            result = kinwuzhao.five_zhao_paipan(
                number, jq_val, lunar_month, qgz[1], qgz[2],
                manual_splits=manual_splits,
            )
        elif pan_mode == "時干起盤":
            result = kinwuzhao.five_zhao_paipan(
                number, jq_val, lunar_month, qgz[2], qgz[3],
                manual_splits=manual_splits,
            )
        elif pan_mode == "分干起盤":
            result = kinwuzhao.five_zhao_paipan(
                number, jq_val, lunar_month, qgz[3], qgz[4],
                manual_splits=manual_splits,
            )
        elif pan_mode == "唐代正法揲筮":
            div = kinwuzhao.WuzhaoDivination(
                jq=jq_val,
                cm=lunar_month,
                gz1=qgz[2],
                gz2=qgz[3],
                manual_splits=manual_splits,
            )
            result = div.divine()

        if "錯誤" in result:
            st.error(result["錯誤"])
            st.stop()

        svg_markup = build_svg(result)

        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.markdown(f"**🔮 起盤模式:** {pan_mode}")
            st.markdown(f"**📆 日期:** {y}年{m}月{d_input}日 {h:02d}時{mi:02d}分")
        with info_col2:
            st.markdown(f"**🌿 節氣:** {jq_val}")
            st.markdown(
                f"**🔢 干支:** {qgz[0]}年 {qgz[1]}月 {qgz[2]}日 {qgz[3]}時 {qgz[4]}分"
            )

        st.divider()
        render_svg(svg_markup, 600)

    except Exception as e:
        logging.exception("排盤過程發生錯誤")
        st.error(f"排盤過程發生錯誤：{e}")
