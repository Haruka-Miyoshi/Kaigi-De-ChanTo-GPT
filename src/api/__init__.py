import sys
from dotenv import load_dotenv
from langchain.llms import OpenAIChat
from langchain.memory import ConversationBufferMemory
from langchain import PromptTemplate, LLMChain

# ./srcにパスを通す
sys.path.append('..')

# .envファイルの内容を読み込みます
load_dotenv()

# chatGPT APIクラス
class ChatAPI:
    # コンストラクタ
    def __init__(self, context:str, role="system") -> None:
        # コンテキスト
        self.content = context
        # ルール
        self.role = role
        # メッセージ
        self.prefix_messages = [{"role": self.role, "content": self.content}]
    
    # 対話開始
    def run(self, text:str, mode=False) -> str:
        # 入力する文章
        template = "{text}"
        # プロンプト
        prompt = PromptTemplate( template=template, input_variables=["text"] )

        # 会話履歴を残す場合
        if mode:
            # 会話履歴を読み込み
            memory = ConversationBufferMemory()

            # chatGPTなどの言語モデルを呼び出すためのラッパー
            llms = OpenAIChat( temperature=0, prefix_messages=self.prefix_messages )

            # 言語モデルなどの処理の連携
            llm_chain = LLMChain( memory=memory, prompt=prompt, llm=llms )
            
            # LLMを実行
            res = llm_chain.run(text)

            return res

        # 会話履歴を残さない場合
        else:
            # chatGPTなどの言語モデルを呼び出すためのラッパー
            llms = OpenAIChat( temperature=0, prefix_messages=self.prefix_messages )

            # 言語モデルなどの処理の連携
            llm_chain = LLMChain( prompt=prompt, llm=llms )

            # LLMを実行
            res = llm_chain.run(text)

            return res