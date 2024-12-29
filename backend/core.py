from dotenv import load_dotenv
from typing import Any, Dict, List
from datetime import datetime
import pytz

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain_core.runnables import RunnableBranch
from langchain_core.runnables.passthrough import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain_core.runnables import RunnableLambda

from langchain_core.runnables.router import RouterRunnable

# from langchain.chains import RouterChain, MultiPromptChain

# from .agents.command_agent import run_command

load_dotenv()



def run(user_prompt: str, chat_history: List[Dict[str, Any]] = []) -> str:

    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-3.5-turbo"
    )
    current_time = datetime.now()

    prompt = {
        "parse": """
        你是一名會計師，試著將對話紀錄與使用者輸入中的記帳資料和修改意見，依照規則將資料格式化成表格，並請按照輸出規則回覆不要包含額外的說明文字。

        <<輸出規則>>
        `markdown表格`
        請確認內容是否正確？如果有任何需要修改或補充的地方，請告訴我！

        <<表格規則>>
        表格標題: 編號,收支,類別,金額,幣別,日期時間,原始輸入
        編號: 流水號,從1開始,記帳資料可能有多筆且每筆都要編號
        收支: 支出,收入
        類別: 交易分類,參考下方"分析設定"中"格式項目"為"記帳類別"的說明
        金額: 單筆總金額,四捨五入至小數第2位,單筆記帳資料可能有多個金額需將其加總
        幣別: 交易幣別,參考下方"分析設定"中"格式項目"為"幣別"的說明
        時間: 交易日期時間,格式為YYYY/MM/DD HH:MM:SS,無輸入則從記帳資料中或當前日期推算

        <<分析設定>>
        表格標題,收支,表格內容,資料範例
        類別,收入,薪資,"薪資,加班費,獎金,年終獎金"
        類別,收入,投資,"投資收入,利息,股利,租金"
        類別,收入,津貼,"津貼,政府補助,非政府補助,家庭提供生活費"
        類別,支出,其他,無法以目前記帳類別分類
        類別,支出,飲食,"餐飲,食物,飲料,乾糧,生鮮,外送"
        類別,支出,個人用品,"服裝,鞋,配件,化妝品,保養品,清潔用品"
        類別,支出,家居,"水電費,瓦斯費,網路費,電信費,房租,房貸,家具,家居維修,家用清潔,家居日用品"
        類別,支出,交通,"公共交通,大眾運輸,租車,自駕車輛(購買車輛,保險,維修,改裝),加油費,停車費,交通罰單"
        類別,支出,學習,"學習發展,學費(線上課程,實體課程),書籍"
        類別,支出,娛樂,"娛樂活動,數位娛樂,休閒活動,無原因的興趣活動支出,旅遊(住宿,門票,交通),運動(健身房會員費,器材),遊戲(遊戲本體,遊戲點數)"
        類別,支出,健康,"醫療支出,手術,住院,買藥,醫療保險,壽險,健康檢查,心理諮詢"
        類別,支出,社交,"禮金,紅包,禮物,捐款,請客吃飯,借錢"
        類別,支出,投資,"投資支出,儲蓄,股票,基金"
        類別,支出,其他,無法以目前記帳類別分類
        幣別,通用,新台幣,記帳語言為中文
        幣別,通用,美元,記帳語言非中文

        <<當前時間>>
        {current_time}

        <<對話紀錄>>
        {chat_history}
        <<使用者輸入>>
        {input}
        """,
        # "review": """
        # 以下是目前的對話歷史，包含已解析的表格內容:

        # <<對話歷史>>
        # {chat_history}

        # 請根據使用者輸入修改表格內容。

        # <<使用者輸入>>
        # {input}

        # 返回修改後的表格。
        # """,
        "insert": """
        試著根據對話紀錄與使用者輸入中的記帳資料表格轉換成JSON格式，並請按照輸出規則回覆不要包含額外的說明文字。

        <<輸出規則>>
        記帳資料新增完成。
        ```json
        ```

        <<JSON 規則>>
        [
            {{
                'type': 'string, income/expense, default: expense',
                'category': 'string, refer to setting',
                'amount': 'number, round to 2 decimal places',
                'currency': 'string, refer to setting',
                'datetime': 'string, format: YYYY/MM/DD HH:MM:SS',
                'comment': 'string, user raw input'
            }},
        ]

        <<分析設定>>
        json_key,income/expense,json_val,table_example
        category,income,salary,薪資
        category,income,investment,投資
        category,income,allowance,津貼
        category,expense,other,其他
        category,expense,food,飲食
        category,expense,personal_care,個人
        category,expense,utilities,家居
        category,expense,transport,交通
        category,expense,education,學習
        category,expense,entertainment,娛樂
        category,expense,healthcare,健康
        category,expense,social,社交
        category,expense,finance,投資
        category,expense,other,其他
        currency,all,TWD,新台幣
        currency,all,USD,美元

        <<對話紀錄>>
        {chat_history}
        <<使用者輸入>>
        {input}
        """,
    }


    parse_input_chain = PromptTemplate(
        template=prompt['parse'],
        input_variables=["input","chat_history","current_time"],
        output_parser=StrOutputParser(),
    ) | llm

    # review_chain = PromptTemplate(
    #     template=prompt[''],
    #     input_variables=["input"],
    #     output_parser=StrOutputParser(),
    # ) | llm

    insert_chain = PromptTemplate(
        template=prompt['insert'],
        input_variables=["input"],
        # output_parser=StrOutputParser(),
    ) | llm

    default_chain = PromptTemplate.from_template("""
    重複回覆以下內容:
    我無法理解你的輸入，或者該功能目前不被支持，請嘗試重新輸入或描述你的需求
    """) | llm | StrOutputParser()


    route_list = [
        {
            "name": "parse",
            "description": "解析記帳資料",
            "chain": parse_input_chain
        },
        {
            "name": "review",
            "description": "修改記帳資料表",
            "chain": parse_input_chain
        },
        {
            "name": "insert",
            "description": "記帳資料表正確，將新增資料至資料庫",
            "chain": insert_chain
        },
        # {
        #     "name": "query_balance",
        #     "description": "查詢當前餘額",
        #     "chain": query_balance_chain
        # },
        # {
        #     "name": "query_summary",
        #     "description": "查詢記帳明細",
        #     "chain": query_summary_chain
        # }
        {
            "name": "exception",
            "description": "未知、未支援的功能",
            "chain": default_chain
        },
    ]
    func_desc_list = ""
    destination_chains = {}
    for cmd in route_list:
        func_desc_list = f"{func_desc_list}\n{cmd['name']}: {cmd['description']}"
        destination_chains[cmd['name']] = cmd['chain']



    route_prompt = """
    你是記帳助理，請根據對話歷史判斷當前需要執行的功能，並請返回功能名稱，如果不適用任何功能請返回"exception":
    <對話歷史>
    {chat_history}
    <最新輸入>
    {input}
    <可用功能(名稱:描述)>
    {func_desc_list}
    """.replace("{func_desc_list}",func_desc_list)

    route = PromptTemplate.from_template(route_prompt) | llm | StrOutputParser()
    router = RouterRunnable(destination_chains)

    router_chain = {
        "key": route | (lambda x: x),
        "input": RunnablePassthrough()
    } | router

    response = router.stream(input={"input":user_prompt, "chat_history":chat_history, "current_time":current_time})

    return response