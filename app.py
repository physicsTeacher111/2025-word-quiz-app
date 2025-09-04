import streamlit as st
import pandas as pd
import random

# 앱 제목
st.title("📚 영어 단어 시험 앱")

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

# 결과 표시
if submitted:
    st.subheader("✅ 결과 확인")
    for i, (correct, user) in enumerate(user_answers):
        if str(correct).strip() == str(user).strip():
            st.success(f"Q{i+1}: 정답! ✅ ({user})")
            score += 1
        else:
            st.error(f"Q{i+1}: 오답 ❌ - 정답은: {correct}, 입력한 답: {user}")
    st.info(f"🎯 총 점수: **{score} / {num_questions}**")
