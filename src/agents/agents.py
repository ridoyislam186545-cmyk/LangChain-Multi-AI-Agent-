from langchain.agents import create_agent
from langchain_groq import ChatGroq  # <--- ১. OpenAI এর বদলে Groq ইমপোর্ট
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import web_search, scrape_url
from dotenv import load_dotenv
load_dotenv()


# Model Initialization (Groq ব্যবহার করে)
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0) # <--- ২. মডেল পরিবর্তন

# 1st Agent: Search_Agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )
    
# 2nd Agent: Reader_Agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )
    
# Writer_chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "you are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """write a detailed research report on the topic below.

Topic:{topic}
Research gathered:
{research}

Structure the report as:
-Introduction
-Key findings(minimum 3 well-explained points)
-Conclusion
-Sources(list all URLs found in the research)
Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()
    

# critic_chain

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic.Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.
     Report{report}
     Respond in this exact format:
     Source: x/10
     strength:
     - ...
     - ...
     Areas to improve
     - ...
     - ...
     One line verdict:
     ...""")
])
critic_chain = critic_prompt | llm | StrOutputParser()