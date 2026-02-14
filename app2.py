import streamlit as st
import requests
from streamlit_js_eval import get_geolocation

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="Midnight Starry Weather", layout="wide")

# CSS: 텍스트 가독성을 위해 배경과 색상 대비 조절
st.markdown("""
    <style>
    .main { color: #191970; }
    h1, h2, h3 { color: #191970 !important; }
    </style>
    """, unsafe_allow_html=True)

# API 키 설정
try:
    API_KEY = st.secrets["WEATHER_API_KEY"]
except:
    st.error("API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인하세요.")
    st.stop()

st.title("✨ 미드나잇 스타리 웨더 (Midnight Starry Weather)")

# 2. 사용자 입력 및 GPS 섹션 (수정된 부분)
col_input1, col_input2 = st.columns([2, 1])

# 목록에 추가하고 싶은 도시가 있다면 아래 리스트에 영어로 추가하시면 됩니다.
CITIES = [
    "Seoul", "Busan", "Incheon", "Daegu", "Daejeon", "Gwangju", "Ulsan", "Sejong",
    "Tokyo", "New York", "London", "Paris", "Sydney", "Berlin", "Singapore"
]

with col_input1:
    # 드롭다운 형식으로 변경
    city_input = st.selectbox("도시를 선택하세요", options=CITIES, index=0)

with col_input2:
    use_gps = st.checkbox("📍 내 위치 정보 사용")

# 위치 정보 결정
query = city_input
if use_gps:
    location_data = get_geolocation()
    if location_data:
        lat = location_data['coords']['latitude']
        lon = location_data['coords']['longitude']
        query = f"{lat},{lon}"
    else:
        st.warning("위치 정보를 가져오는 중입니다... (브라우저 권한을 허용해주세요)")

# 3. 데이터 불러오기 및 시각화
if query:
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={query}&aqi=no&lang=ko"
    res = requests.get(url)
    
    if res.status_code == 200:
        response = res.json()
        current = response['current']
        loc = response['location']
        
        temp = current['temp_c']
        condition = current['condition']['text']
        cloud = current['cloud']
        vis_km = current['vis_km']

        weather_emoji = "☀️"
        if "비" in condition: weather_emoji = "☔"
        elif "눈" in condition: weather_emoji = "☃️"
        elif "구름" in condition or "흐림" in condition: weather_emoji = "☁️"

        st.divider()

        # 4. 화면 분할 출력
        left_col, right_col = st.columns(2)

        with left_col:
            st.subheader(f"📍 {loc['name']} ({loc['country']})")
            st.markdown(f"<h1 style='text-align: center; font-size: 100px;'>{weather_emoji}</h1>", unsafe_allow_html=True)
            st.metric("현재 온도", f"{temp}°C")
            st.write(f"**현재 상태:** {condition}")
            
            if temp >= 30: st.warning("너무 더워요! 🥵")
            elif temp <= 5: st.info("너무 추워요! 🥶")

        with right_col:
            st.subheader("🔭 별 관측 지수 (Stargazing)")
            if cloud < 20 and vis_km > 10:
                st.success("오늘은 별이 쏟아지는 밤입니다! ✨")
            elif cloud < 50:
                st.info("구름 사이로 별을 찾을 수 있어요! 🌟")
            else:
                st.error("하늘이 흐려 별이 잘 보이지 않아요. ☁️")
            
            st.write(f"**구름 양:** {cloud}%")
            st.write(f"**가시거리:** {vis_km}km")

        # 5. 지도 표시
        st.divider()
        st.subheader("⭐ 관측 위치 확인")
        map_data = {"lat": [loc['lat']], "lon": [loc['lon']]}
        st.map(map_data)
        
    else:
        st.error("도시 정보를 찾을 수 없습니다.")

# 6. 새로고침 버튼
if st.button("날씨 데이터 새로고침"):
    st.balloons()
    st.toast("최신 데이터를 불러왔습니다!")