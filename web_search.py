#pip install tavily-python langchain-tavily        for active virtual environment

#Tavily account madhe API key tayar karun ti .env file madhe thevli pahije

from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()


# Web search karanyasathi Tavily tool varato.
web_search = TavilySearch(
    max_results=5
)


# User search query web varati search karato.
def search_web(query: str):

    result = web_search.invoke({
        "query": query
    })

    return result
