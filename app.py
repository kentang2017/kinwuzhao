# -*- coding: utf-8 -*-
"""堅五兆 Streamlit 應用主程式 — 完整重構版。

重構重點：
- st.date_input + st.time_input 取代多個 number_input
- st.html() 渲染乾淨 SVG，支援大小調整
- st.columns 布局：左側 SVG + 右側詳細解釋（六獸、孤虛、關籥、總論）
- st.form 提交按鈕控制排盤計算
- st.expander 展開案例與古籍
- session_state 完整管理與錯誤處理
- 手動分裂數輸入 + 列印排盤功能
- 暗黑古風美學 + 現代 Streamlit 元件（expander、tooltip、progress bar）
"""

from __future__ import annotations

import datetime
import logging
from pathlib import Path

import pendulum as pdlm
import streamlit as st
import streamlit.components.v1 as components

import config
import jieqi
import kinwuzhao

logging.basicConfig(level=logging.ERROR)

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit command)
# ---------------------------------------------------------------------------

st.set_page_config(
    layout="wide",
    page_title="堅五兆 - 五兆排盤",
    page_icon="icon.png",
)

# ---------------------------------------------------------------------------
# Custom CSS — 暗黑古風美學 + 列印樣式
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .main .block-container { padding-top: 1rem; }
    @media print {
        [data-testid="stSidebar"],
        [data-testid="stHeader"],
        button { display: none !important; }
        .main .block-container { padding: 0; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_local_md(filename: str) -> str:
    """讀取專案根目錄下的 Markdown 文件。"""
    path = Path(__file__).parent / filename
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"⚠️ 找不到檔案: {filename}。請確認檔案存在於專案根目錄。"


# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

if "initialized" not in st.session_state:
    _now = pdlm.now(tz="Asia/Hong_Kong")
    st.session_state.update(
        initialized=True,
        sel_date=datetime.date(_now.year, _now.month, _now.day),
        sel_time=datetime.time(_now.hour, _now.minute),
        result=None,
        info_data=None,
        error_msg=None,
        svg_size=480,
    )

# ---------------------------------------------------------------------------
# SVG grid builder
# ---------------------------------------------------------------------------

_GRID = [
    ("兆", 0, 0),    ("火鄉", 1, 0), ("", 2, 0),
    ("木鄉", 0, 1),  ("土鄉", 1, 1), ("金鄉", 2, 1),
    ("", 0, 2),      ("水鄉", 1, 2), ("", 2, 2),
]

_CELL = 140
_VB = _CELL * 3

ELEMENT_COLORS: dict[str, str] = {
    "木": "#4CAF50",
    "火": "#FF5252",
    "土": "#FFD740",
    "金": "#E0E0E0",
    "水": "#42A5F5",
}


def build_svg(data: dict, display_size: int = _VB) -> str:
    """組裝九宮格 SVG 排盤圖。

    Args:
        data: 排盤結果字典 (label → position dict)。
        display_size: SVG 顯示像素尺寸（viewBox 固定，width/height 可調）。
    """
    vb = _VB
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {vb} {vb}" width="{display_size}" height="{display_size}">',
        f'<rect width="{vb}" height="{vb}" fill="#1A1C23" rx="8"/>',
    ]

    by_palace = {v.get("宮位"): v for v in data.values()}

    for i in range(1, 3):
        x = i * _CELL
        parts += [
            f'<line x1="{x}" y1="0" x2="{x}" y2="{vb}" stroke="#444" stroke-width="1"/>',
            f'<line x1="0" y1="{x}" x2="{vb}" y2="{x}" stroke="#444" stroke-width="1"/>',
        ]

    parts.append(
        f'<rect width="{vb}" height="{vb}" fill="none" stroke="#666" stroke-width="2" rx="8"/>'
    )

    for name, col, row in _GRID:
        cx = col * _CELL + _CELL / 2
        cy = row * _CELL + 20
        cell = by_palace.get(name, {})
        element = cell.get("五行", "")
        ec = ELEMENT_COLORS.get(element, "#E0E0E0")

        lines = [
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
        for idx, line in enumerate(lines):
            if not line:
                continue
            dy = "1.4em" if idx else "0"
            if idx == 0:
                parts.append(
                    f'<tspan x="{cx}" dy="{dy}" font-size="15" '
                    f'font-weight="bold" fill="#BDBDBD">{line}</tspan>'
                )
            elif idx == 1:
                parts.append(
                    f'<tspan x="{cx}" dy="{dy}" font-size="18" '
                    f'font-weight="bold" fill="{ec}">{line}</tspan>'
                )
            else:
                parts.append(f'<tspan x="{cx}" dy="{dy}">{line}</tspan>')
        parts.append("</text>")

    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Sidebar — 輸入面板
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("📅 日期與時間")

    # ── 「使用現在時間」按鈕（在 form 之外，即時更新） ──
    if st.button(
        "⏱ 使用現在時間",
        use_container_width=True,
        help="自動填入當前香港時間",
    ):
        now = pdlm.now(tz="Asia/Hong_Kong")
        st.session_state.sel_date = datetime.date(now.year, now.month, now.day)
        st.session_state.sel_time = datetime.time(now.hour, now.minute)
        st.rerun()

    # ── 起盤方式（在 form 之外，動態顯示手動折竹選項） ──
    pan_mode = st.radio(
        "🔮 起盤方式",
        ["日干起盤", "時干起盤", "分干起盤", "干支起盤", "唐代正法揲筮"],
        index=0,
        help="選擇占卜計算方式",
    )

    # ── 手動折竹輸入（在 form 之外，需即時互動） ──
    manual_splits: list[int] | None = None
    if pan_mode in ("日干起盤", "時干起盤", "分干起盤", "唐代正法揲筮"):
        use_manual = st.checkbox(
            "🎋 手動輸入分裂數",
            help="啟用傳統折竹體驗，依序輸入 6 次折竹數",
        )
        if use_manual:
            st.caption("依序輸入 6 次折竹數（從 36 算子中每次取走的數量）")
            split_cols = st.columns(6)
            manual_splits = []
            _split_labels = ["兆", "木", "火", "土", "金", "水"]
            for i, sc in enumerate(split_cols):
                with sc:
                    manual_splits.append(
                        st.number_input(
                            _split_labels[i],
                            min_value=1,
                            max_value=35,
                            value=6,
                            step=1,
                            key=f"split_{i}",
                        )
                    )

    st.divider()

    # ── 主輸入表單（日期、時間、數字、提交按鈕） ──
    with st.form("divination_form"):
        sel_date = st.date_input(
            "📆 日期",
            value=st.session_state.sel_date,
            help="選擇占卜日期",
        )
        sel_time = st.time_input(
            "🕐 時間",
            value=st.session_state.sel_time,
            step=60,
            help="選擇占卜時間（精確到分鐘）",
        )
        number = st.number_input(
            "🔢 數字",
            min_value=0,
            max_value=90,
            value=0,
            step=1,
            help="輸入數字 (0-90)，超過 9 將取模",
        )
        submitted = st.form_submit_button(
            "🧮 起盤",
            use_container_width=True,
            type="primary",
        )

    st.divider()
    st.caption("🌏 時區: Asia/Hong_Kong")

    # ── SVG 大小調整（在 form 之外，即時更新顯示） ──
    svg_display_size = st.slider(
        "📐 排盤圖大小",
        min_value=300,
        max_value=700,
        value=st.session_state.svg_size,
        step=20,
        help="調整排盤圖顯示尺寸",
    )
    st.session_state.svg_size = svg_display_size


# ---------------------------------------------------------------------------
# Computation — 排盤計算（僅在表單提交時執行）
# ---------------------------------------------------------------------------

if submitted:
    y = sel_date.year
    m_val = sel_date.month
    d_val = sel_date.day
    h_val = sel_time.hour
    mi_val = sel_time.minute

    st.session_state.sel_date = sel_date
    st.session_state.sel_time = sel_time

    # Validate date
    try:
        pdlm.datetime(y, m_val, d_val, h_val, mi_val, tz="Asia/Hong_Kong")
    except (ValueError, OverflowError):
        st.session_state.error_msg = "請輸入有效的日期和時間！"
        st.session_state.result = None
    else:
        try:
            # Progress bar
            _progress = st.empty()
            _progress.progress(0, text="正在計算干支…")

            qgz = config.gangzhi(y, m_val, d_val, h_val, mi_val)
            _progress.progress(20, text="正在推算節氣…")

            jq_val = jieqi.jq(y, m_val, d_val, h_val, mi_val)
            _progress.progress(40, text="正在查詢農曆…")

            lunar_month = config.lunar_date_d(y, m_val, d_val)["農曆月"][0]

            num = number % 9 if number > 9 else number
            _progress.progress(60, text="正在排盤…")

            result: dict = {}

            if pan_mode == "干支起盤":
                result = kinwuzhao.gangzhi_paipan(
                    qgz, num, jq_val, lunar_month
                )
            elif pan_mode == "日干起盤":
                result = kinwuzhao.five_zhao_paipan(
                    num, jq_val, lunar_month, qgz[1], qgz[2],
                    manual_splits=manual_splits,
                )
            elif pan_mode == "時干起盤":
                result = kinwuzhao.five_zhao_paipan(
                    num, jq_val, lunar_month, qgz[2], qgz[3],
                    manual_splits=manual_splits,
                )
            elif pan_mode == "分干起盤":
                result = kinwuzhao.five_zhao_paipan(
                    num, jq_val, lunar_month, qgz[3], qgz[4],
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

            _progress.progress(90, text="正在組裝排盤…")

            if "錯誤" in result:
                st.session_state.result = None
                st.session_state.error_msg = result["錯誤"]
            else:
                st.session_state.result = result
                st.session_state.info_data = {
                    "pan_mode": pan_mode,
                    "date_str": (
                        f"{y}年{m_val}月{d_val}日 "
                        f"{h_val:02d}時{mi_val:02d}分"
                    ),
                    "jq": jq_val,
                    "gz": (
                        f"{qgz[0]}年 {qgz[1]}月 {qgz[2]}日 "
                        f"{qgz[3]}時 {qgz[4]}分"
                    ),
                    "lunar_month": lunar_month,
                }
                st.session_state.error_msg = None

            _progress.progress(100, text="排盤完成！")
            _progress.empty()

        except Exception as exc:
            logging.exception("排盤過程發生錯誤")
            st.session_state.result = None
            st.session_state.error_msg = str(exc)


# ---------------------------------------------------------------------------
# Content Tabs
# ---------------------------------------------------------------------------

tab_pan, tab_example, tab_guji, tab_links, tab_update = st.tabs(
    [" 🧮 排盤 ", " 📜 案例 ", " 📚 古籍 ", " 🔗 連結 ", " 🆕 更新 "]
)

# ── 排盤 Tab ──
with tab_pan:
    st.header("堅五兆")

    if st.session_state.error_msg:
        st.error(f"❌ {st.session_state.error_msg}")
    elif st.session_state.result is None:
        st.info("👈 請在側邊欄選擇日期時間，然後點擊 **「起盤」** 開始占卜。")
    else:
        result = st.session_state.result
        info = st.session_state.info_data

        # ── 基本資訊列 ──
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**🔮 起盤模式:** {info['pan_mode']}")
            st.markdown(f"**📆 日期:** {info['date_str']}")
        with c2:
            st.markdown(f"**🌿 節氣:** {info['jq']}")
            st.markdown(f"**🔢 干支:** {info['gz']}")

        st.divider()

        # ── 主布局：左側 SVG + 右側詳細解釋 ──
        svg_col, detail_col = st.columns([3, 2])

        with svg_col:
            svg = build_svg(result, st.session_state.svg_size)
            st.html(
                f'<div style="display:flex;justify-content:center;'
                f'padding:0.5rem">{svg}</div>'
            )
            # 列印排盤按鈕
            if st.button("🖨️ 列印排盤", help="使用瀏覽器列印功能"):
                components.html(
                    "<script>window.parent.print()</script>",
                    height=0,
                )

        with detail_col:
            # 六獸配置
            with st.expander("🐉 六獸配置", expanded=True):
                for label, cell in result.items():
                    beast = cell.get("六獸", "")
                    death = cell.get("六獸死", "")
                    harm = cell.get("六獸害", "")
                    suffix = ""
                    if death:
                        suffix += " ⚠️ **死**"
                    if harm:
                        suffix += " ⚡ **害**"
                    st.markdown(f"**{label}** — {beast}{suffix}")

            # 孤虛
            with st.expander("🌑 孤虛", expanded=True):
                _found_gx = False
                for label, cell in result.items():
                    gu = cell.get("孤", "")
                    xu = cell.get("虛", "")
                    if gu or xu:
                        _found_gx = True
                        tag = " ".join(
                            filter(
                                None,
                                [
                                    "🔴 孤" if gu else "",
                                    "🔵 虛" if xu else "",
                                ],
                            )
                        )
                        st.markdown(f"**{label}**: {tag}")
                if not _found_gx:
                    st.caption("此盤無孤虛。")

            # 關籥將軍
            with st.expander("🔒 關籥將軍", expanded=True):
                _found_lk = False
                for label, cell in result.items():
                    tags: list[str] = []
                    if cell.get("關"):
                        tags.append("🔒 關")
                    if cell.get("籥"):
                        tags.append("🔑 籥")
                    if cell.get("將軍"):
                        tags.append("⚔️ 將軍")
                    if tags:
                        _found_lk = True
                        st.markdown(f"**{label}**: {' '.join(tags)}")
                if not _found_lk:
                    st.caption("此盤無關籥將軍。")

            # 六親
            with st.expander("👥 六親", expanded=False):
                for label, cell in result.items():
                    lq = cell.get("六親", "")
                    if lq:
                        el = cell.get("五行", "")
                        st.markdown(f"**{label}** ({el}): {lq}")

            # 旺相
            with st.expander("💫 旺相", expanded=False):
                for label, cell in result.items():
                    wx = cell.get("旺相", "")
                    el = cell.get("五行", "")
                    if wx:
                        st.markdown(f"**{label}** ({el}): {wx}")

            # 總論
            with st.expander("📝 總論", expanded=False):
                zhao = result.get("兆", {})
                el = zhao.get("五行", "")
                wx = zhao.get("旺相", "")
                st.markdown(f"兆位五行為 **{el}**，旺相為 **{wx}**。")

                death_palaces = [
                    k for k, v in result.items() if v.get("六獸死")
                ]
                harm_palaces = [
                    k for k, v in result.items() if v.get("六獸害")
                ]
                if death_palaces:
                    st.markdown(
                        f"⚠️ 六獸死宮：{'、'.join(death_palaces)}"
                    )
                if harm_palaces:
                    st.markdown(
                        f"⚡ 六獸害宮：{'、'.join(harm_palaces)}"
                    )

                gu_palaces = [
                    k for k, v in result.items() if v.get("孤")
                ]
                xu_palaces = [
                    k for k, v in result.items() if v.get("虛")
                ]
                if gu_palaces:
                    st.markdown(f"🔴 孤落：{'、'.join(gu_palaces)}")
                if xu_palaces:
                    st.markdown(f"🔵 虛落：{'、'.join(xu_palaces)}")

# ── 案例 Tab（可展開區塊） ──
with tab_example:
    st.header("📜 案例")
    _example_md = _read_local_md("example.md")
    if _example_md.startswith("⚠️"):
        st.warning(_example_md)
    elif not _example_md.strip():
        st.info("暫無案例資料。")
    else:
        # 嘗試按 ## 標題拆分為可展開區塊
        _sections = _example_md.split("\n## ")
        if len(_sections) > 1:
            if _sections[0].strip():
                st.markdown(_sections[0])
            for sec in _sections[1:]:
                nl = sec.find("\n")
                title = sec[:nl].strip() if nl > 0 else sec.strip()
                body = sec[nl:] if nl > 0 else ""
                with st.expander(f"📖 {title}", expanded=False):
                    st.markdown(body)
        else:
            with st.expander("📖 案例內容", expanded=True):
                st.markdown(_example_md)

# ── 古籍 Tab（可展開區塊） ──
with tab_guji:
    st.header("📚 古籍")
    _guji_md = _read_local_md("guji.md")
    if _guji_md.startswith("⚠️"):
        st.warning(_guji_md)
    elif not _guji_md.strip():
        st.info("暫無古籍資料。")
    else:
        with st.expander("📚 五兆古籍書目", expanded=True):
            st.markdown(_guji_md)

# ── 連結 Tab ──
with tab_links:
    st.header("🔗 連結")
    st.markdown(
        "- [堅六壬 Kinliuren](https://github.com/kentang2017/kinliuren)\n"
        "- [堅奇門 Kinqimen](https://github.com/kentang2017/kinqimen)\n"
        "- [堅太乙 Kintaiyi](https://github.com/kentang2017/kintaiyi)"
    )

# ── 更新 Tab ──
with tab_update:
    st.header("🆕 更新")
    st.markdown(_read_local_md("log.md"))
