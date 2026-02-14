import streamlit as st
import requests
from streamlit_js_eval import streamlit_js_eval, get_geolocation
from datetime import datetime

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="✨ 날씨 및 별자리 도우미", layout="wide")

st.markdown(f"""
    <style>
    .main {{ color: #191970; }}
    h1, h2, h3 {{ color: #191970 !important; }}
    /* 날짜 시간 박스 스타일 */
    .time-container {{
        background-color: #f0f7ff;
        border: 2px solid #191970;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin: 10px 0px 20px 0px;
    }}
    /* 별자리 이름 강조 박스 스타일 */
    .constellation-box {{
        font-size: 2.5rem !important;
        font-weight: bold !important;
        color: #ffffff !important;
        background: linear-gradient(90deg, #191970, #00008b);
        padding: 20px 40px;
        border-radius: 15px;
        display: inline-block;
        margin: 15px 0;
        box-shadow: 3px 3px 12px rgba(0,0,0,0.3);
    }}
    /* 버튼 스타일 조정 */
    .stButton>button {{
        width: 100%;
        font-weight: bold;
        border: 1px solid #191970;
        color: #191970;
    }}
    </style>
    """, unsafe_allow_html=True)

# API 키 설정
try:
    API_KEY = st.secrets["WEATHER_API_KEY"]
except:
    st.error("API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인하세요.")
    st.stop()

# --- [로직] 날짜와 시간에 따른 주인공 별자리 및 이미지 매칭 ---
def get_best_star_info():
    now = datetime.now()
    month = now.month
    
    if 3 <= month <= 5:
        return "처녀자리", "봄의 대곡선 근처에서 가장 우아하게 빛나는 별자리입니다."
    elif 6 <= month <= 8:
        return "백조자리", "은하수 한가운데에서 날개를 펼친 모습의 여름철 대표 별자리입니다."
    elif 9 <= month <= 11:
        return "페가수스자리", "가을 밤하늘 거대한 사각형 모양으로 찾기 쉬운 별자리입니다."
    else:
        # 현재 2월 기준 (겨울철 별자리)
        return "오리온자리", "겨울 밤하늘 가장 밝고 화려한 사냥꾼 모습의 별자리입니다."

st.title("✨ 날씨 및 별자리 도우미 (Weather and star helper)")

# 2. 지역 선택 섹션
st.subheader("📍 확인하고 싶은 지역을 선택하세요")
cities = {
    "SEOUL": "Seoul", "BUSAN": "Busan", "INCHEON": "Incheon", 
    "DAEGU": "Daegu", "DAEJEON": "Daejeon", "GWANGJU": "Gwangju", 
    "ULSAN": "Ulsan", "SEJONG": "Sejong", "JEJU": "Jeju"
}

cols = st.columns(len(cities))
selected_city = None

for i, (display_name, search_name) in enumerate(cities.items()):
    with cols[i]:
        if st.button(display_name):
            selected_city = search_name

# --- 현재 날짜 및 시각 표시 박스 ---
now = datetime.now()
current_time_str = now.strftime("%Y년 %m월 %d일 %H시 %M분")
st.markdown(f"""
    <div class="time-container">
        <h3 style="margin:0; color: #191970;">📅 현재 기준 시각: {current_time_str}</h3>
    </div>
    """, unsafe_allow_html=True)

use_gps = st.checkbox("📍 내 위치 정보 사용 (GPS 권한 필요)")

query = selected_city
if use_gps:
    location_data = get_geolocation()
    if location_data:
        lat, lon = location_data['coords']['latitude'], location_data['coords']['longitude']
        query = f"{lat},{lon}"

# 3. 데이터 불러오기 및 시각화
if query:
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={query}&aqi=no&lang=ko"
    res = requests.get(url)
    
    if res.status_code == 200:
        data = res.json()
        current, loc = data['current'], data['location']
        temp, condition = current['temp_c'], current['condition']['text']
        cloud = current['cloud']

        st.divider()
        left_col, right_col = st.columns(2)

        with left_col:
            st.subheader(f"📍 {loc['name']}의 현재 날씨")
            weather_emoji = "☀️"
            if "비" in condition: weather_emoji = "☔"
            elif "눈" in condition: weather_emoji = "☃️"
            elif "구름" in condition or "흐림" in condition: weather_emoji = "☁️"
            
            st.markdown(f"<h1 style='font-size: 80px;'>{weather_emoji}</h1>", unsafe_allow_html=True)
            st.metric("현재 온도", f"{temp}°C")
            st.write(f"**상태:** {condition}")

        with right_col:
            # --- [수정 완료] '별 관측 지수' 삭제 후 '오늘의 별 추천'으로 교체 ---
            st.subheader("🔭 오늘의 별 추천")
            star_name, star_desc = get_best_star_info()
            
            # 1. 별자리 이름 강조 박스
            st.markdown(f"<div style='text-align: center;'><div class='constellation-box'>{star_name}</div></div>", unsafe_allow_html=True)
            
            # 2. 별자리 성도 이미지 가이드
            if star_name == "오리온자리":
                st.markdown("")
            elif star_name == "처녀자리":
                st.markdown("

[Image of the constellation Virgo star chart]
")
            elif star_name == "백조자리":
                st.markdown("")
            else:
                st.markdown("")
            
            # 3. 별자리 설명
            st.info(f"✨ **{star_name}**: {star_desc}")
            
            # 4. 관측 상태 메시지 (수치는 삭제)
            if cloud < 40:
                st.success(f"오늘 밤, 밤하늘에서 **{star_name}**를 찾아보기에 아주 좋은 날씨입니다!")
            elif cloud < 80:
                st.warning(f"약간의 구름은 있지만, 밝은 **{star_name}**는 충분히 감상하실 수 있습니다.")
            else:
                st.error(f"아쉽게도 지금은 구름이 많아 **{star_name}**가 구름 뒤에 숨어있네요.")
            
            st.write("---")
            st.caption("※ 실시간 날씨 정보를 바탕으로 별자리를 추천해 드립니다.")

        # 4. 지도 표시
        st.divider()
        st.subheader("⭐ 별자리 관측 명당 추천")
        st.map([{"lat": loc['lat'], "lon": loc['lon']}])
        
    else:
        st.error("데이터를 불러오지 못했습니다.")
else:
    st.info("지역 버튼을 클릭하거나 GPS를 활성화해 주세요.")