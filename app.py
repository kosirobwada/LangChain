from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.base import BaseCallbackHandler
import streamlit as st
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
import json

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
    category = st.selectbox("クイズのカテゴリを選択してください:", ["地理", "科学","AI","医療","人間"])

    if st.button("質問を取得"):
        container = st.empty()
        stream_handler = StreamHandler(container)
        llm = ChatOpenAI(model_name=model_name, streaming=True, callbacks=[stream_handler], temperature=0)
        template = """以下のカテゴリ関するクイズを日本語で作成し、答えも作成してください。
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
        st.write(question)
        user_answer = st.text_input("解答を入力してください。")
        st.write(user_answer)
        answer = data["answer"]
        st.write(answer)

if __name__ == '__main__':
    main()