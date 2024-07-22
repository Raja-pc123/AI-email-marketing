from scrapegraphai.graphs import SearchGraph
import os
import google.generativeai as genai
import asyncio
import uvicorn
from fastapi import FastAPI

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
app = FastAPI()

@app.post('/scrape')
async def companyWebScrapper(company:str):
    prompt_1 = f"About {company} in detail"
    graph_config = {
        "llm": {
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "model": "gemini-pro",
        },
    }

    # Create the search graph
    search_graph_1= SearchGraph(prompt_1, graph_config)

    # Run the search graph
    result = search_graph_1.run()

    summ_res= model.generate_content(f""" Summarize the below information in a readble format:
                                      {result}
                                      Include good enough content at the beginning of the text containing almost all information of the company.
                                      Don't include services and solutions of the company.
                                      Also don't include any testimonials or reviews.
                                      Don't include Contact info or Contact emails.
                                      Also Don't include any social media platform and its links.
                                      There should not be any kind of link present in the text.
                                      """)
    
    prompt_2= f"list out all the company services and solutions provided by {company}. "
    search_graph_2 = SearchGraph(prompt_2, graph_config)
    # Run the search graph
    services = search_graph_2.run()
    
    prompt_3 = f"{company} client testimonials" 

    # Create the search graph
    search_graph_3 = SearchGraph(prompt_3, graph_config)
    client_review = search_graph_3.run()
    
    return summ_res.text, services, client_review


if __name__ == "__main__":
   # asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    # asyncio.run(app)
    uvicorn.run(app, host='127.0.0.1', port=8500)