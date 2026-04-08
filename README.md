<div align="center">

# 🌟 Python 五兆占卜 | Kinwuzhao 堅五兆

### 唐宋官方法定的折竹彈占術 • 復原敦煌遺書與正史記載

*The Official Divination Method of Tang & Song Dynasties — Restored from Dunhuang Manuscripts & Historical Records*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://kinwuzhao.streamlit.app/)
[![GitHub](https://img.shields.io/github/stars/kentang2017/kinwuzhao?style=social)](https://github.com/kentang2017/kinwuzhao)

[![image](https://github.com/kentang2017/kinwuzhao/blob/main/pic/wuzhao.png)](https://kinwuzhao.streamlit.app/)

<a href="https://kinwuzhao.streamlit.app/">
  <img src="https://img.shields.io/badge/%E2%9C%A8%20%E7%AB%8B%E5%8D%B3%E7%B7%9A%E4%B8%8A%E9%AB%94%E9%A9%97%20Try%20Live%20Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo" />
</a>

</div>

---

## ✨ Highlights 亮點

- 🏛️ **堅守古法，正宗唐宋官占** — 嚴格依據敦煌寫本 P.2859《五兆要訣略》及正史記載復原
- 🎋 **折竹彈占，千年再現** — 以 Python 完整實現「折竹彈占謂之五兆」的占卜儀軌
- 🔮 **五行 × 六獸 × 孤虛** — 內建水火木金土五兆體系，搭配青龍、朱雀、螣蛇等六獸斷事
- 🌐 **Streamlit 一鍵體驗** — 無需安裝，瀏覽器即可占卜，暗色主題介面精美
- 📚 **學術級文獻支撐** — 附古籍書目索引，涵蓋隋唐宋三朝五兆典籍

---

## 📖 簡介 Introduction

**五兆**是中國古代重要的占卜方法之一，與龜卜、易占並列為唐代官方法定占卜術。

> 「折竹彈占謂之五兆」 — 宋·趙彥衛《雲麓漫鈔》

其核心定義源自《舊唐書·太宗紀上》，宋代梅堯臣詩作「五兆中開卦」更印證了此術在士大夫階層的廣泛應用。20 世紀初敦煌藏經洞出土的文獻 **P.2859《五兆要訣略》** 等寫本，系統保存了五兆占卜的完整儀軌與卦辭體系，為今日復原提供了珍貴的第一手資料。

**Kinwuzhao** 堅五兆正是基於這些敦煌遺書與正史文獻，以 Python 精確復原的五兆占卜工具。

> *Wuzhao (Five Prognostications) was one of the officially sanctioned divination methods during the Tang and Song dynasties in China. This project faithfully restores the ancient practice based on Dunhuang manuscript P.2859 and historical records such as the Old Book of Tang.*

---

## 🚀 快速開始 Quick Start

### 方式一：線上體驗（推薦）

直接訪問 Streamlit 應用，無需安裝任何依賴：

👉 **<https://kinwuzhao.streamlit.app/>**

### 方式二：本地運行

```bash
# 1. 克隆倉庫
git clone https://github.com/kentang2017/kinwuzhao.git
cd kinwuzhao

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 啟動 Streamlit 應用
streamlit run app.py
```

### 方式三：Python 引入使用

```python
from kinwuzhao import *

# 依據實際函數進行五兆占卜
# Perform Wuzhao divination using the module
```

---

## 🧩 支援功能 Features

| 功能 Feature | 說明 Description |
|:---|:---|
| 🎋 五兆占卜 | 完整復原折竹彈占流程 |
| 🐉 六獸配置 | 青龍、朱雀、螣蛇、勾陳、白虎、玄武自動排列 |
| ☯️ 孤虛判斷 | 陰孤虛、陽孤虛雙系統分析 |
| 📅 日干·時干·分干 | 天干排盤，精確到分鐘 |
| 🔄 王相胎沒死囚廢休 | 五行旺衰全週期判斷 |
| 🔒 關鎖煞 | 特殊煞星標注與提示 |
| 🌙 暗色主題 | 精美 Streamlit 暗色介面 |

---

## 📸 截圖與演示 Screenshots

<div align="center">

[![五兆占卜介面](https://github.com/kentang2017/kinwuzhao/blob/main/pic/wuzhao.png)](https://kinwuzhao.streamlit.app/)

*五兆占卜 Streamlit 應用介面 / Wuzhao Divination App Interface*

<!-- 如有更多截圖，可在 pic/ 資料夾中添加並引用 -->
<!-- Add more screenshots from the pic/ folder as needed -->

</div>

---

## 📦 安裝 Installation

### 環境要求

- Python 3.8 或以上
- 建議使用虛擬環境（venv / conda）

### 詳細步驟

```bash
# 1. 克隆倉庫
git clone https://github.com/kentang2017/kinwuzhao.git
cd kinwuzhao

# 2. 建立並啟用虛擬環境（建議）
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 啟動應用
streamlit run app.py
```

啟動後瀏覽器將自動開啟 `http://localhost:8501`，即可開始占卜。

---

## 💡 使用範例 Usage Examples

### Streamlit 應用

```bash
streamlit run app.py
```

在瀏覽器中開啟後，依照介面指引輸入占卜資訊，系統將自動進行五兆排盤並顯示結果，包括五行歸屬、六獸配置、孤虛分析等完整占斷。

### Python 模組

```python
from kinwuzhao import *

# 五兆占卜的核心函數可直接調用
# Core Wuzhao divination functions are available for direct use
```

---

## 🤝 貢獻指南 Contributing

歡迎對五兆占卜有興趣的朋友參與貢獻！

1. **Fork** 本倉庫
2. 創建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m "Add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 **Pull Request**

無論是文獻校勘、程式優化、介面改進或文檔翻譯，我們都非常歡迎。

> *Contributions are welcome! Whether it's textual collation of historical sources, code optimization, UI improvements, or translations — feel free to open a PR.*

---

## 📬 聯絡方式 Contact

如有任何問題或建議，歡迎透過以下方式聯繫：

- **GitHub Issues**：[提交 Issue](https://github.com/kentang2017/kinwuzhao/issues)
- **微信公眾號**：搜索關注作者公眾號，獲取更多術數研究內容

---

## 📄 License

本專案目前尚未指定開源授權協議。如需使用或二次開發，請先聯繫作者。

> *This project has not yet specified an open-source license. Please contact the author before use or redistribution.*

---

## 🔗 相關專案 Related Projects

| 專案 Project | 說明 Description | 連結 Link |
|:---|:---|:---|
| **堅奇門 Kinqimen** | Python 奇門遁甲 | [GitHub](https://github.com/kentang2017/kinqimen) |
| **堅太乙 Kintaiyi** | Python 太乙神數 | [GitHub](https://github.com/kentang2017/kintaiyi) |
| **堅六壬 Kinliuren** | Python 大六壬 | [GitHub](https://github.com/kentang2017/kinliuren) |

---

<div align="center">

**堅守古法 · 正宗唐宋官占 · 以 Python 復原千年智慧**

*Preserving ancient methods — Authentic Tang & Song dynasty divination — Restored with Python*

⭐ 如果這個專案對你有幫助，請給一顆 Star！

</div>
