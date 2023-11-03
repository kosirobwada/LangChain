import os
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.callbacks.base import BaseCallbackHandler
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

model_name = 'gpt-4'

class Quiz(BaseModel):
    question: str = Field(description="question")
    answer: str = Field(description="correct answer")

parser = PydanticOutputParser(pydantic_object=Quiz)
format_instructions = parser.get_format_instructions()

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

def main():
    st.title("クイズアプリ")
    category = st.selectbox("クイズのカテゴリを選択してください:", ["地理", "科学", "AI", "医療", "人間"])

    if st.button("質問を取得"):
        container = st.empty()
        stream_handler = StreamHandler(container)
        llm = ChatOpenAI(model_name=model_name, streaming=True, callbacks=[stream_handler], temperature=0, openai_api_key=os.environ["OPENAI_API_KEY"])
        template = f"""以下のカテゴリ関するクイズを作成し、答えも作成してください。
        {format_instructions}
        カテゴリ: {category}
        """
        prompt = PromptTemplate(template=template, input_variables=["category"])
        chain = LLMChain(llm=llm, prompt=prompt)
        output = chain.run({"category": category})
        quiz = parser.parse(output)
        st.session_state.quiz = quiz

    answer = st.text_input("あなたの答えを入力してください：")

    if st.button("答えを送信"):
        correct_answer = st.session_state.quiz.answer
        if answer == correct_answer:
            st.write("正解！")
        else:
            st.write(f"不正解。正しい答えは{correct_answer}でした。")

if __name__ == '__main__':
    main()