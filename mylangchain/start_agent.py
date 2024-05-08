import langchain

langchain.debug = True
from langchain.tools import tool
from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_openai_tools_agent,
    create_structured_chat_agent,
)
from langchain_core.messages import AIMessage, HumanMessage
from myopenai.answer_question import answer_question
from langchain_openai import AzureChatOpenAI
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import sql_database
from langchain_google_genai import ChatGoogleGenerativeAI
from whitehouse.database import (
    get_summary_article_results,
    get_summary_article_results_by_year_only,
)
from .tools.keyword_extractor import extract_keywords_from_text


db = sql_database.SQLDatabase.from_uri(
    "postgresql://postgres:postgres@postgres:5432/newsanalysis"
)

print(db.get_table_names())
sql_query_tool = QuerySQLDataBaseTool(db=db)
sql_query_tool.description += (
    f"These are the tables in the database: {str(db.get_table_names())} "
)


@tool
def answer_question_from_knowledge_base(question: str) -> str:
    """Answer a question from the knowledge base. anything related to the whitehouse and the US president.
    Use this tool only for queries that are not aggregate in nature or does not granular time access such as trends overtime
    This API can be used to perhaps enhance the search results of the newsanalysis database, but use the get_month_summary tool
    for aggregates and performing time analysis and trends over time."""
    print(f"Answering question: {question}")
    return answer_question(question)


@tool
def add_Stone_to_fly(a: int, b: int) -> int:
    """Add a stone to a fly."""
    return a + b + 3


@tool
def get_month_summary(key_words: str, month: int, year: int) -> str:
    """This tool gets the summary of the articles for the month and year.
    The database it uses is the newsanalysis database. which is based on all white house press releases.
    Use this tool for aggregate queries and time analysis and trends over time.
    If a user asks quesions about a year, break down the query into month increments and use this tool to get the summary for each month.
    """
    res = get_summary_article_results(key_words, month, year)
    return res


@tool
def get_year_summary(key_words: str, year: int) -> str:
    """This tool gets the summary of the articles for year.
    The database it uses is the newsanalysis database. which is based on all white house press releases.
    Use this tool for aggregate queries and time analysis and trends over time.
    If a user asks quesions about a year, use this tool to get the summary for that year.
    """
    res = get_summary_article_results_by_year_only(key_words, year)
    return res


def start_loop():
    """Start the loop"""
    prompt = hub.pull("hwchase17/openai-tools-agent")
    # prompt = hub.pull("hwchase17/structured-chat-agent")
    # print(prompt)

    tools = [
        answer_question_from_knowledge_base,
        add_Stone_to_fly,
        # sql_query_tool,
        get_month_summary,
        get_year_summary,
        extract_keywords_from_text,
    ]

    llm = AzureChatOpenAI(
        azure_deployment="gpt-35-turbo-16k",
        verbose=True,
    )
    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-pro", convert_system_message_to_human=True
    # )

    # agent = create_structured_chat_agent(llm, tools, prompt)
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    chat_history = []
    while True:
        user_input = input("User message: ")
        res = agent_executor.invoke(
            {
                "input": user_input,
                "chat_history": chat_history,
            }
        )
        print(f'chatbot" {res["output"]}')
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=res["output"]))
        print("ending session: Mohamed")
        break
    # res = agent_executor.invoke(
    #     {
    #         "input": "What was the relationship between Egypt and te US like through 2014",
    #         # "input": "Add a stone to a fly with 9 and 6",
    #     }
    # )
    # print(res)
    print(res["output"])
