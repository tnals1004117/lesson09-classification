import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# 데이터 설정
# --------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/tnals1004117/data/refs/heads/main/stroke.csv"


@st.cache_data(ttl=3600)
def load_data():
    """첫 화면과 같은 주소에서 UTF-8 형식으로 데이터를 읽는다."""
    return pd.read_csv(DATA_URL, encoding="utf-8")


# --------------------------------------------------
# 데이터 불러오기 및 기본 정리
# --------------------------------------------------
st.title("🔎 데이터 탐색")
st.write(
    "나이, 평균 혈당, 질병 여부, BMI 결측 여부, 흡연 상태에 따라 "
    "데이터의 분포와 뇌졸중 비율을 살펴봅니다."
)

try:
    df = load_data()
except Exception as error:
    st.error("데이터를 불러오지 못했습니다. 인터넷 연결과 데이터 주소를 확인해 주세요.")
    st.caption(f"오류 내용: {error}")
    st.stop()

required_columns = [
    "age",
    "avg_glucose_level",
    "hypertension",
    "heart_disease",
    "bmi",
    "smoking_status",
    "stroke",
]
missing_columns = [column for column in required_columns if column not in df.columns]

if missing_columns:
    st.error("분석에 필요한 열이 데이터에 없습니다: " + ", ".join(missing_columns))
    st.stop()

# 분석에 사용할 열을 숫자형으로 변환한다.
for column in [
    "age",
    "avg_glucose_level",
    "hypertension",
    "heart_disease",
    "bmi",
    "stroke",
]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# 그래프의 그룹 이름
stroke_labels = {0: "뇌졸중 없음 (0)", 1: "뇌졸중 있음 (1)"}


# --------------------------------------------------
# 1. 나이와 평균 혈당 분포
# --------------------------------------------------
st.subheader("1. 나이와 평균 혈당의 분포")
st.write("각 항목의 값이 어느 구간에 많이 모여 있는지 히스토그램으로 확인합니다.")

hist_col1, hist_col2 = st.columns(2)

with hist_col1:
    age_data = df[["age"]].dropna()
    age_fig = px.histogram(
        age_data,
        x="age",
        nbins=30,
        title="나이 분포",
        labels={"age": "나이", "count": "사람 수"},
    )
    age_fig.update_layout(
        xaxis_title="나이",
        yaxis_title="사람 수",
        bargap=0.08,
    )
    st.plotly_chart(age_fig, use_container_width=True)
    st.caption(f"나이 값이 있는 사람: {len(age_data):,}명")

with hist_col2:
    glucose_data = df[["avg_glucose_level"]].dropna()
    glucose_fig = px.histogram(
        glucose_data,
        x="avg_glucose_level",
        nbins=30,
        title="평균 혈당 분포",
        labels={"avg_glucose_level": "평균 혈당", "count": "사람 수"},
