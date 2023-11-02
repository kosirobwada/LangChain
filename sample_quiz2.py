from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.base import BaseCallbackHandler
import streamlit as st

model_name = 'gpt-4'


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, init_text=""):
        self.container = container
        self.text = init_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)


def main():
    category = st.selectbox("クイズのカテゴリを選択してください:", ["地理", "科学","AI","医療","人間"])

    if st.button("質問を取得"):
        container = st.empty()
        stream_handler = StreamHandler(container)
        llm = ChatOpenAI(model_name=model_name, streaming=True, callbacks=[stream_handler], temperature=0)
        prompt = PromptTemplate(
            input_variables=["query"],
            template="""
                     {category}
                     に関するクイズを1つ作成してください。
                     """,
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        chain.run(category)
    
    answer = st.text_input("メッセージを入力してください。")

if __name__ == '__main__':
    main()

