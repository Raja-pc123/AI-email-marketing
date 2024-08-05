import os
from pprint import pprint 
import google.generativeai as genai
from scrapegraphai.graphs import SearchGraph
import logging
from langchain_core.output_parsers.json import OutputParserException


# Suppress specific logger
logging.getLogger("langchain_google_genai.chat_models").setLevel(logging.ERROR)


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')


def company_scrapper(company):
    prompt_1 = f"About {company} in detail"
    graph_config = {
        "llm": {
            "api_key":  os.getenv("GOOGLE_API_KEY"),
            "model": "gemini-pro",
        },
    }
    # Create the search graph
    search_graph_1 = SearchGraph(prompt_1, graph_config)
    # Run the search graph
    try:
      result = search_graph_1.run()
    except OutputParserException as e:
      result='NA'
    if result=='NA':
      summ_res = model.generate_content(f"""About {company} company in detail

                                          -Don't include any testimonials or reviews.
                                          -Don't include Contact info or Contact emails.
                                          -Don't include any social media platform and its links.
                                          -There should not be any kind of link present in the text.""")
    else:
      summ_res = model.generate_content(f""" Summarize the below information in a readable format:
                                          {result}
                                          Include good enough content at the beginning of the text containing almost all information of the company.
                                          Don't include services and solutions of the company.
                                          Also don't include any testimonials or reviews.
                                          Don't include Contact info or Contact emails.
                                          Also Don't include any social media platform and its links.
                                          There should not be any kind of link present in the text.
                                          """)
    prompt_2 = f"list out all the company services and solutions provided by {company}. "
    search_graph_2 = SearchGraph(prompt_2, graph_config)
    # Run the search graph
    try:
      services = search_graph_2.run()
    except OutputParserException as e:
      services='NA'
    prompt_3 = f"{company} client testimonials"
    # Create the search graph
    search_graph_3 = SearchGraph(prompt_3, graph_config)
    try:
      client_review = search_graph_3.run()
    except OutputParserException as e:
      client_review='NA'

    # Prepare the response
    response = {
        'text': summ_res.text,
        'services': services,
        'review': client_review
    }
    return response
res=company_scrapper('pravaah consulting')
print(res)
