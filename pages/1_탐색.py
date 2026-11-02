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
    )
    glucose_fig.update_layout(
        xaxis_title="평균 혈당",
        yaxis_title="사람 수",
        bargap=0.08,
    )
    st.plotly_chart(glucose_fig, use_container_width=True)
    st.caption(f"평균 혈당 값이 있는 사람: {len(glucose_data):,}명")

st.divider()


# --------------------------------------------------
# 2. 뇌졸중 여부에 따른 나이와 평균 혈당 비교
# --------------------------------------------------
st.subheader("2. 뇌졸중 여부에 따른 나이와 평균 혈당 비교")
st.write(
    "상자그림은 각 그룹의 중앙값과 값이 퍼져 있는 범위를 비교할 때 유용합니다. "
    "아래 표에는 두 그룹의 평균값도 함께 정리했습니다."
)

box_data = df[df["stroke"].isin([0, 1])].copy()
box_data["뇌졸중 여부"] = box_data["stroke"].map(stroke_labels)

box_col1, box_col2 = st.columns(2)

with box_col1:
    age_box_data = box_data[["age", "뇌졸중 여부"]].dropna()
    age_box_fig = px.box(
        age_box_data,
        x="뇌졸중 여부",
        y="age",
        color="뇌졸중 여부",
        title="뇌졸중 여부에 따른 나이",
        labels={"age": "나이", "뇌졸중 여부": "그룹"},
        points="outliers",
    )
    age_box_fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="나이")
    st.plotly_chart(age_box_fig, use_container_width=True)

with box_col2:
    glucose_box_data = box_data[["avg_glucose_level", "뇌졸중 여부"]].dropna()
    glucose_box_fig = px.box(
        glucose_box_data,
        x="뇌졸중 여부",
        y="avg_glucose_level",
        color="뇌졸중 여부",
        title="뇌졸중 여부에 따른 평균 혈당",
        labels={"avg_glucose_level": "평균 혈당", "뇌졸중 여부": "그룹"},
        points="outliers",
    )
    glucose_box_fig.update_layout(
        showlegend=False,
        xaxis_title="",
        yaxis_title="평균 혈당",
    )
    st.plotly_chart(glucose_box_fig, use_container_width=True)

mean_rows = []
for stroke_value, label in stroke_labels.items():
    group = box_data[box_data["stroke"] == stroke_value]
    mean_rows.append(
        {
            "뇌졸중 여부": label,
            "사람 수": len(group),
            "평균 나이": group["age"].mean(),
            "평균 혈당": group["avg_glucose_level"].mean(),
        }
    )

mean_table = pd.DataFrame(mean_rows)
mean_table["평균 나이"] = mean_table["평균 나이"].round(2)
mean_table["평균 혈당"] = mean_table["평균 혈당"].round(2)

st.markdown("**그룹별 평균값**")
st.dataframe(mean_table, use_container_width=True, hide_index=True)

st.divider()


# --------------------------------------------------
# 3. 고혈압 / 심장병 여부에 따른 뇌졸중 비율
# --------------------------------------------------
st.subheader("3. 고혈압과 심장병 여부에 따른 뇌졸중 비율")
st.write(
    "각 항목이 0인 그룹과 1인 그룹에서 stroke가 1인 비율을 비교합니다. "
    "비율은 각 그룹의 유효한 stroke 응답 수를 기준으로 계산합니다."
)


def make_stroke_rate_table(data, group_column, group_name):
    """그룹별 인원수와 뇌졸중 비율(%)을 계산한다."""
    valid = data[data[group_column].isin([0, 1]) & data["stroke"].isin([0, 1])]
    summary = (
        valid.groupby(group_column)["stroke"]
        .agg(사람수="count", 뇌졸중_인원="sum", 뇌졸중_비율="mean")
        .reindex([0, 1])
        .reset_index()
    )
    summary[group_column] = summary[group_column].map(
        {0: f"{group_name} 없음 (0)", 1: f"{group_name} 있음 (1)"}
    )
    summary["뇌졸중_비율"] = summary["뇌졸중_비율"] * 100
    summary = summary.rename(
        columns={
            group_column: "구분",
            "사람수": "사람 수",
            "뇌졸중_인원": "뇌졸중 인원",
            "뇌졸중_비율": "뇌졸중 비율(%)",
        }
    )
    return summary


rate_col1, rate_col2 = st.columns(2)

with rate_col1:
    hypertension_table = make_stroke_rate_table(df, "hypertension", "고혈압")
    hypertension_fig = px.bar(
        hypertension_table,
        x="구분",
        y="뇌졸중 비율(%)",
        title="고혈압 여부에 따른 뇌졸중 비율",
        text="뇌졸중 비율(%)",
        labels={"구분": "고혈압", "뇌졸중 비율(%)": "뇌졸중 비율(%)"},
    )
    hypertension_fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    hypertension_fig.update_layout(yaxis_title="뇌졸중 비율(%)", xaxis_title="")
    st.plotly_chart(hypertension_fig, use_container_width=True)
    st.dataframe(
        hypertension_table.round({"뇌졸중 비율(%)": 2}),
        use_container_width=True,
        hide_index=True,
    )

with rate_col2:
    heart_table = make_stroke_rate_table(df, "heart_disease", "심장병")
    heart_fig = px.bar(
        heart_table,
        x="구분",
        y="뇌졸중 비율(%)",
        title="심장병 여부에 따른 뇌졸중 비율",
        text="뇌졸중 비율(%)",
        labels={"구분": "심장병", "뇌졸중 비율(%)": "뇌졸중 비율(%)"},
    )
    heart_fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    heart_fig.update_layout(yaxis_title="뇌졸중 비율(%)", xaxis_title="")
    st.plotly_chart(heart_fig, use_container_width=True)
    st.dataframe(
        heart_table.round({"뇌졸중 비율(%)": 2}),
        use_container_width=True,
        hide_index=True,
    )

st.divider()


# --------------------------------------------------
# 4. BMI 결측 그룹과 전체의 뇌졸중 비율 비교
# --------------------------------------------------
st.subheader("4. BMI가 비어 있는 사람들의 뇌졸중 비율")
st.write(
    "BMI 값이 비어 있는 사람들만 따로 모아, 전체 데이터의 뇌졸중 비율과 비교합니다. "
    "각 비율은 stroke 값이 0 또는 1로 확인되는 사람을 기준으로 계산합니다."
)

def stroke_summary(data):
    valid_stroke = data[data["stroke"].isin([0, 1])]["stroke"]
    people = len(valid_stroke)
    stroke_people = int((valid_stroke == 1).sum())
    ratio = (stroke_people / people * 100) if people else float("nan")
    return people, stroke_people, ratio


bmi_missing_data = df[df["bmi"].isna()]
missing_people, missing_stroke_people, missing_ratio = stroke_summary(bmi_missing_data)
all_people, all_stroke_people, all_ratio = stroke_summary(df)

bmi_compare = pd.DataFrame(
    {
        "항목": ["사람 수 (stroke 유효값 기준)", "뇌졸중 인원", "뇌졸중 비율(%)"],
        "BMI가 비어 있는 사람": [
            missing_people,
            missing_stroke_people,
            round(missing_ratio, 2) if pd.notna(missing_ratio) else None,
        ],
        "전체 사람": [
            all_people,
            all_stroke_people,
            round(all_ratio, 2) if pd.notna(all_ratio) else None,
        ],
    }
)
st.dataframe(bmi_compare, use_container_width=True, hide_index=True)
st.caption(f"BMI 값이 비어 있는 행은 모두 {len(bmi_missing_data):,}개입니다.")

st.divider()


# --------------------------------------------------
# 5. 흡연 상태별 사람 수
# --------------------------------------------------
st.subheader("5. 흡연 상태별 사람 수")
st.write("흡연 상태에 기록된 값마다 사람 수를 세어 표로 나타냅니다.")

smoking_counts = (
    df["smoking_status"]
    .fillna("값 없음")
    .astype(str)
    .value_counts(dropna=False)
    .rename_axis("흡연 상태")
    .reset_index(name="사람 수")
)

st.dataframe(smoking_counts, use_container_width=True, hide_index=True)

st.caption(
    "※ 이 페이지의 그래프와 비율은 데이터 안의 집단별 통계를 보여 줍니다. "
    "집단 간 차이만으로 원인과 결과를 단정하거나 개인의 건강 상태를 판단할 수는 없습니다."
)
