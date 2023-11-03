from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.chains import LLMChain
from langchain.callbacks.base import BaseCallbackHandler
import streamlit as st

model_name = 'gpt-4'

class Quiz(BaseModel):
    questions: str = Field(description="question")
    answer: str = Field(description="correct answer")

parser = PydanticOutputParser(pydantic_object=Quiz)

format_instructions = parser.get_format_instructions()

template = """以下のカテゴリ関するクイズを作成し、答えも作成してください。
{format_instructions}
カテゴリ: {category}
"""
prompt = PromptTemplate(
    template = template,
    input_variables = ["category"],
    partial_variables = {"format_instructions": format_instructions}
)
formatted_prompt = prompt.format(category="科学")

chat = ChatOpenAI(model_name=model_name,temperature=0,openai_api_key="")
messages = [HumanMessage(content=formatted_prompt)]
output = chat(messages)
print(output.content)

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