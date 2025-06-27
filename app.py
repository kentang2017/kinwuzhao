import streamlit as st
import datetime
import config
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

def lunar_date_d(y, m, d):
    day = fromSolar(y,m,d)
    return {"月": str(day.getLunarMonth())+"月", "日":str(day.getLunarDay())}
        
st.set_page_config(
    layout="wide",
    page_title="堅五兆 - 五兆排盘",
    page_icon="icon.jpg"
)
pan,example,guji,links,update = st.tabs([' 🧮排盤 ', ' 📜案例 ', ' 📚古籍 ',' 🔗連結 ',' 🆕更新 ' ])

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
    
    # Timezone info
    st.caption("時區: Asia/Hong_Kong")

with guji:
    st.header('古籍')
    st.markdown(get_file_content_as_string("guji.md"))

with links:
    st.header('連結')
    st.markdown(get_file_content_as_string("update.md"), unsafe_allow_html=True)

with update:
    st.header('更新')
    st.markdown(get_file_content_as_string("log.md"))
  
with pan:
    st.header('堅五兆')
    cm =  dict(zip(list(range(1,13)), list("正二三四五六七八九十")+["十一","十二"])).get(int(lunar_date_d(y, m, d).get("月").replace("月", "")))
    qgz = gangzhi(y, m, d, h, min)
    jq = jq(y, m, d, h, min)
    pan = kinwuzhao.five_zhao_paipan(qgz[2][0])
    output2 = st.empty()
    with st_capture(output2.code):
        print()
