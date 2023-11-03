import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

load_dotenv()

# LangChainのChatOpenAIを初期化
chat_model = ChatOpenAI(
    model_name=os.environ["OPENAI_API_MODEL"],
    temperature=os.environ["OPENAI_API_TEMPERATURE"],
    streaming=True,
)

def get_quiz_question(category):
    # LangChainを使ってクイズの質問を生成
    prompt = f"Give me a quiz question related to {category}."
    """
    response = chat_model.run(prompt)
    return response["text"] if "text" in response else ""
    """
    try:
        response = chat_model.run(prompt)
        return response.get("text", "")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return ""

st.title('クイズアプリ')

# カテゴリの選択
category = st.selectbox("クイズのカテゴリを選択してください:", ["地理", "科学","AI","医療","人間"])

# "質問を取得"ボタンをクリックしたときの動作
if st.button("質問を取得"):
    question = get_quiz_question(category)
    st.session_state.question = question
    st.session_state.answered = False
    st.write(f"質問: {question}")

# ユーザーが回答を入力する部分
if "question" in st.session_state:
    answer = st.text_input("回答:")

    # 回答を提出するボタン
    if st.button("回答を提出"):
        # ここでは正解のチェック方法を簡略化しています。
        if answer.lower() in st.session_state.question.lower():
            st.write("正解！")
            st.session_state.answered = True
        else:
            st.write("不正解。もう一度挑戦してください！")

# セッションステートの初期化
if "reset" in st.session_state or "answered" not in st.session_state:
    st.session_state.answered = False
    st.session_state.question = ""

if st.session_state.answered:
    st.session_state.reset = True
else:
    st.session_state.reset = False
