from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.base import BaseCallbackHandler
import streamlit as st
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
import json
import time
from dotenv import load_dotenv

load_dotenv()

model_name = 'gpt-4'

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, init_text=""):
        self.container = container
        self.text = init_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

class Quiz(BaseModel):
    questions: str = Field(description="question")
    answer: str = Field(description="correct answer")

parser = PydanticOutputParser(pydantic_object=Quiz)

format_instructions = parser.get_format_instructions()

def main():
    categories = ["地理", "科学", "AI", "医療", "人間"]
    default_index = 0

    if "category" in st.session_state:
        default_index = categories.index(st.session_state.category)

    selected_category = st.selectbox("クイズのカテゴリを選択してください:", categories, index=default_index)

    st.session_state.category = selected_category

    if st.button("クイズを作成"):
        st.session_state.question, st.session_state.answer = handle_button_click(st.session_state.category) 

    if "question" in st.session_state and st.session_state.question:  
        st.write("クイズ:", st.session_state.question)

    if "user_answer" not in st.session_state:
        st.session_state.user_answer = ""

    
    if "input_key" not in st.session_state:  
        st.session_state.input_key = str(time.time())

    st.session_state.user_answer = st.text_input("解答を入力してください。",key=st.session_state.input_key)
    st.write("あなたの回答:", st.session_state.user_answer)

    if st.session_state.user_answer and "answer" in st.session_state and st.session_state.answer:
        st.write("正解:", st.session_state.answer)
        if st.button("カテゴリーを再選択"):
            del st.session_state.input_key 
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

def handle_button_click(category):
    container = st.empty()
    llm = ChatOpenAI(model_name=model_name, streaming=False, temperature=1.0)
    template = """以下のカテゴリ関するクイズを日本語で1つだけ作成し、答えも作成してください。
    {format_instructions}
    カテゴリ: {category}
    """
    prompt = PromptTemplate(
        template = template,
        input_variables = ["category"],
        partial_variables = {"format_instructions": format_instructions}
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    json_string = chain.run(category)  
    data = json.loads(json_string)
    question = data["questions"]
    answer = data["answer"]

    return question, answer

if __name__ == '__main__':
    main()