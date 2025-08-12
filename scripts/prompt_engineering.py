from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain.globals import set_debug

set_debug(True)

# Load Env Variables
from dotenv import load_dotenv

load_dotenv()

# For BedRock
from langchain_aws import ChatBedrock
from langchain_aws import BedrockEmbeddings


faiss_db_path = "../vector_db/imprenta.faiss"
db = FAISS.load_local(
    faiss_db_path,
    BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0"),
    allow_dangerous_deserialization=True,
)

retriever = db.as_retriever(
    search_type="mmr",  # Also test "similarity"
    search_kwargs={"k": 10},
)

system_prompt_template = """
You are an absolutely professional analytical code review assistant specializing in both security and functional review. 
Your task is to analyze source code and provide detailed insights through a multi-step reflection process and you will ONLY analyse Server Side Request Forgery vulnerabilities when it comes to HTML to PDF generators.

Context for analysis:
{context}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt_template),
        (
            "human",
            """
Please analyze the following aspects of the codebase, following the reflection process outlined above:

{question}

Format your response in the following structure:
1. Initial Analysis
2. Skip the Reflection on Initial Findings
3. Final Comprehensive Analysis
""",
        ),
    ]
)

llm = ChatBedrock(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    model_kwargs={"temperature": 0.9},
)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

user_question = """Tell me the following information about the code base I am providing you. Format your response in the following structure:
 - Purpose of the application
 - Whaat is the vulnerability that you have identified
 - How to exploit the application
 - What is the vulnerable package that you have identified.
"""

# This is an optional addition to stream the output in chunks
# for a chat-like experience
for chunk in chain.stream(user_question):
    print(chunk, end="", flush=True)
