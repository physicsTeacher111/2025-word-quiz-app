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

# 단어장 로드 (word.csv 사용)
@st.cache_data
def load_words():
    return pd.read_csv("word.csv", encoding="utf-8-sig")

df = load_words()

# 시험 범위 선택
st.subheader("1️⃣ 시험 범위 선택")
min_num = int(df["No"].min())
max_num = int(df["No"].max())
start = st.number_input("시작 번호", min_value=min_num, max_value=max_num, value=min_num)
end = st.number_input("끝 번호", min_value=start, max_value=max_num, value=min(start + 9, max_num))
filtered = df[(df["No"] >= start) & (df["No"] <= end)].reset_index(drop=True)

# 시험 모드 선택
st.subheader("2️⃣ 시험 모드 선택")
quiz_type = st.radio("시험 유형을 선택하세요", ["4지 선다형", "직접 입력"])

# 문제 수 선택
st.subheader("3️⃣ 문제 수 선택")
num_questions = st.slider("출제할 문제 수", min_value=1, max_value=len(filtered), value=min(10, len(filtered)))
quiz_data = filtered.sample(num_questions).reset_index(drop=True)

# 문제 풀기
st.subheader("📝 문제 시작")
score = 0
user_answers = []

with st.form("quiz_form"):
    for i, row in quiz_data.iterrows():
        st.write(f"**Q{i+1}.** `{row['Word']}`")

        if quiz_type == "4지 선다형":
            options = [row["Meaning"]]
            while len(options) < 4:
                wrong = df.sample(1)["Meaning"].values[0]
                if wrong not in options:
                    options.append(wrong)
            random.shuffle(options)
            answer = st.radio("👉 뜻을 고르세요:", options, key=f"q{i}")
        else:
            answer = st.text_input("👉 뜻을 직접 입력하세요:", key=f"q{i}")
        user_answers.append((row["Meaning"], answer))

    submitted = st.form_submit_button("제출")

# 정답 확인
if submitted:
    st.subheader("✅ 결과 확인")
    for i, (correct, user) in enumerate(user_answers):
        acceptable_answers = [ans.strip() for ans in correct.replace(";", ",").split(",")]
        if user.strip() in acceptable_answers:
            st.success(f"Q{i+1}: 정답! ✅ ({user})")
            score += 1
        else:
            st.error(f"Q{i+1}: 오답 ❌ - 정답은: {correct}, 입력한 답: {user}")
    st.info(f"🎯 총 점수: **{score} / {num_questions}**")
