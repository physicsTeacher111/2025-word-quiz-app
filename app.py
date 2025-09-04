import streamlit as st
import pandas as pd
import random

# 앱 제목
st.title("📚 영어 단어 시험 앱")
# 이름 입력
st.subheader("🧑‍🎓 학생 정보 입력")
student_name = st.text_input("이름을 입력하세요")
if not student_name:
    st.warning("먼저 이름을 입력하세요!")
    st.stop()
# 학습 기록 보기 버튼
if st.button("📚 내 학습 기록 보기"):
    try:
        all_results = pd.DataFrame(sheet.get_all_records())
        student_results = all_results[all_results["이름"] == student_name]
        st.write(f"✅ {student_name}님의 최근 학습 기록입니다:")
        st.dataframe(student_results)
    except Exception as e:
        st.error("기록을 불러오는 데 문제가 발생했습니다.")
        st.exception(e)

# CSV 파일 불러오기
@st.cache_data
def load_words():
    return pd.read_csv("words.csv")  # 번호, 영어, 한국어 컬럼 필요

df = load_words()

# ✅ 사용자 범위 입력
min_num = int(df["번호"].min())
max_num = int(df["번호"].max())

st.subheader("1️⃣ 시험 범위 선택")
start = st.number_input("시작 번호", min_value=min_num, max_value=max_num, value=min_num)
end = st.number_input("끝 번호", min_value=start, max_value=max_num, value=min(start + 9, max_num))

filtered = df[(df["번호"] >= start) & (df["번호"] <= end)].reset_index(drop=True)

# ✅ 모드 선택: 선다형 or 직접 입력
st.subheader("2️⃣ 시험 모드 선택")
quiz_type = st.radio("시험 유형을 선택하세요", ["4지 선다형", "직접 입력"])

# ✅ 문제 수 선택
st.subheader("3️⃣ 문제 수 선택")
num_questions = st.slider("출제할 문제 수", min_value=1, max_value=len(filtered), value=min(10, len(filtered)))
quiz_data = filtered.sample(num_questions).reset_index(drop=True)

# 시험 시작
st.subheader("📝 문제 시작")

score = 0
submitted = False

with st.form("quiz_form"):
    user_answers = []
    for i, row in quiz_data.iterrows():
        st.write(f"**Q{i+1}.** `{row['영어']}`")

        if quiz_type == "4지 선다형":
            # 보기 생성
            options = [row["한국어"]]
            while len(options) < 4:
                wrong = df.sample(1)["한국어"].values[0]
                if wrong not in options:
                    options.append(wrong)
            random.shuffle(options)
            answer = st.radio(f"👉 뜻을 고르세요:", options, key=f"q{i}")
        else:
            answer = st.text_input("👉 뜻을 직접 입력하세요:", key=f"q{i}")
        
        user_answers.append((row["한국어"], answer))

    submitted = st.form_submit_button("제출")

st.info(f"🎯 총 점수: **{score} / {num_questions}**")
# 📝 Google Sheet에 결과 저장
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Google Sheet 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("your_credentials.json", scope)  # 여기에 .json 파일 이름
client = gspread.authorize(creds)

# 시트 열기
sheet = client.open("student_quiz_results").worksheet("results")

# 저장할 데이터 구성
today = datetime.date.today().strftime("%Y-%m-%d")
wrong_words = [correct for correct, user in user_answers if correct.strip() != user.strip()]
score_str = f"{score}/{num_questions}"
range_str = f"{start}~{end}"

row = [student_name, today, score_str, range_str, ", ".join(wrong_words)]
sheet.append_row(row)

# 결과 표시
# 결과 표시
if submitted:
    st.subheader("✅ 결과 확인")
    for i, (correct, user) in enumerate(user_answers):
        # 여러 정답 중 하나라도 맞으면 정답 처리
        acceptable_answers = [ans.strip() for ans in correct.replace(";", ",").split(",")]
        if user.strip() in acceptable_answers:
            st.success(f"Q{i+1}: 정답! ✅ ({user})")
            score += 1
        else:
            st.error(f"Q{i+1}: 오답 ❌ - 정답은: {correct}, 입력한 답: {user}")

    st.info(f"🎯 총 점수: **{score} / {num_questions}**")
