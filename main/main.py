import json
from pathlib import Path

import pandas as pd
import streamlit as st


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
APP_TITLE = "뇌졸중 예측 실습실"
DATA_URL = "https://raw.githubusercontent.com/tnals1004117/data/refs/heads/main/stroke.csv"

BASE_DIR = Path(__file__).resolve().parent
RECORD_DIR = BASE_DIR / "내_기록"
RECORD_FILE = RECORD_DIR / "뇌졸중_예측_실습실.json"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧠",
    layout="wide",
)


# --------------------------------------------------
# 데이터 및 기록 불러오기
# --------------------------------------------------
@st.cache_data(ttl=3600)
def load_data():
    """UTF-8 CSV 파일을 읽어 온다."""
    return pd.read_csv(DATA_URL, encoding="utf-8")


def load_notes():
    """저장된 우리말 뜻과 출처를 불러온다."""
    if not RECORD_FILE.exists():
        return {"meanings": {}, "source": ""}

    try:
        with RECORD_FILE.open("r", encoding="utf-8") as file:
            saved = json.load(file)
        return {
            "meanings": saved.get("meanings", {}),
            "source": saved.get("source", ""),
        }
    except (json.JSONDecodeError, OSError):
        st.warning("기존 기록 파일을 읽지 못해 빈 기록으로 시작합니다.")
        return {"meanings": {}, "source": ""}


def save_notes(meanings, source):
    """입력한 내용을 JSON 파일로 저장한다."""
    RECORD_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "meanings": meanings,
        "source": source,
    }
    with RECORD_FILE.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
st.title("🧠 뇌졸중 예측 실습실")
st.write(
    "뇌졸중 관련 데이터를 살펴보고, 각 열이 어떤 정보를 담고 있는지 "
    "직접 정리해 보는 실습 공간입니다."
)

try:
    df = load_data()
except Exception as error:
    st.error("데이터를 불러오지 못했습니다. 인터넷 연결과 데이터 주소를 확인해 주세요.")
    st.caption(f"오류 내용: {error}")
    st.stop()

notes = load_notes()

# 요약 통계
person_count = len(df)
column_count = len(df.columns)

if "stroke" in df.columns:
    stroke_count = int((pd.to_numeric(df["stroke"], errors="coerce") == 1).sum())
else:
    stroke_count = 0

stroke_ratio = (stroke_count / person_count * 100) if person_count else 0


# --------------------------------------------------
# 첫 화면: 데이터 소개 및 요약 카드
# --------------------------------------------------
st.subheader("1. 데이터 한눈에 보기")
st.markdown(
    "이 데이터는 여러 사람의 기본 정보와 건강 관련 항목, "
    "그리고 뇌졸중 발생 여부를 담고 있습니다."
)

card1, card2, card3, card4 = st.columns(4)
card1.metric("전체 사람 수", f"{person_count:,}명")
card2.metric("열 개수", f"{column_count:,}개")
card3.metric("stroke가 1인 사람 수", f"{stroke_count:,}명")
card4.metric("stroke가 1인 비율", f"{stroke_ratio:.2f}%")

st.caption(
    "※ stroke가 1인 비율은 전체 행 중 stroke 값이 1인 행의 비율입니다. "
    "이 값은 데이터의 분포를 설명하며 개인의 뇌졸중 위험도를 뜻하지 않습니다."
)

st.divider()


# --------------------------------------------------
# 열 이름 / 우리말 뜻 / 값의 종류 / 빈 값 개수
# --------------------------------------------------
st.subheader("2. 열 이름 살펴보기")
st.write(
    "‘우리말 뜻’ 칸을 교재를 참고해 직접 채워 보세요. "
    "‘값의 종류’는 숫자형 또는 범주형 여부와 범주형 값의 예시를 보여 줍니다."
)

rows = []
for column in df.columns:
    series = df[column]
    missing_count = int(series.isna().sum())

    if pd.api.types.is_numeric_dtype(series):
        value_kind = "숫자형"
    else:
        unique_values = series.dropna().astype(str).unique().tolist()
        shown_values = unique_values[:6]
        value_kind = "범주형"
        if shown_values:
            value_kind += ": " + ", ".join(shown_values)
        if len(unique_values) > 6:
            value_kind += ", ..."

    rows.append(
        {
            "열 이름": column,
            "우리말 뜻": notes["meanings"].get(column, ""),
            "값의 종류": value_kind,
            "빈 값 개수": missing_count,
        }
    )

columns_df = pd.DataFrame(rows)

edited_df = st.data_editor(
    columns_df,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    column_config={
        "열 이름": st.column_config.TextColumn("열 이름", disabled=True),
        "우리말 뜻": st.column_config.TextColumn(
            "우리말 뜻",
            help="교재를 참고해 각 열의 뜻을 입력하세요.",
        ),
        "값의 종류": st.column_config.TextColumn("값의 종류", disabled=True),
        "빈 값 개수": st.column_config.NumberColumn("빈 값 개수", disabled=True),
    },
    key="meaning_editor",
)

st.divider()


# --------------------------------------------------
# 원본 데이터 미리보기
# --------------------------------------------------
st.subheader("3. 데이터 처음 다섯 줄")
st.write("전처리하거나 값을 바꾸지 않은 원본 데이터의 첫 다섯 행입니다.")
st.dataframe(df.head(5), use_container_width=True, hide_index=True)

st.divider()


# --------------------------------------------------
# 출처 기록 및 저장
# --------------------------------------------------
st.subheader("4. 데이터 출처 기록")
source_text = st.text_area(
    "데이터 출처",
    value=notes["source"],
    placeholder="교재에 적힌 데이터 출처를 여기에 입력하세요.",
    height=100,
    key="source_editor",
)

if st.button("💾 우리말 뜻과 출처 저장", type="primary"):
    meanings_to_save = {
        str(row["열 이름"]): (
            "" if pd.isna(row["우리말 뜻"]) else str(row["우리말 뜻"])
        )
        for _, row in edited_df.iterrows()
    }

    try:
        save_notes(meanings_to_save, source_text)
        st.success(f"기록을 저장했습니다. 저장 위치: {RECORD_FILE}")
    except OSError as error:
        st.error(f"기록을 저장하지 못했습니다: {error}")

st.caption(
    "저장한 내용은 main.py와 같은 위치의 '내_기록' 폴더에 JSON 파일로 보관됩니다. "
    "새로고침하면 저장된 우리말 뜻과 출처를 다시 불러옵니다."
)

st.info(
    "학습용 데이터 소개 화면입니다. 이 데이터만으로 개인의 뇌졸중 발생 여부를 "
    "진단하거나 예측할 수는 없습니다."
)
