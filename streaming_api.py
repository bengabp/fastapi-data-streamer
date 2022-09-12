from lib2to3.pytree import convert
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import time
from sse_starlette.sse import EventSourceResponse
from starlette.responses import StreamingResponse
import asyncio
import requests

from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession

api = FastAPI()

origins = ["*"]

api.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_headers = ['*'],
    allow_methods = ["*"]
)

def convert_to_json(dict_data:dict):
    return json.dumps(dict_data)



@api.get("/stream")
async def stream_handler(q:str,limit:int=10):
    async def scrape(search_query: str, limit):
        print("Running async funciton")
        print(f"Searching for '{search_query}' ...Results limit={limit}")
        total_results = 0
        current_google_page_number = 0
        scrape = True

        previous_website_urls = set()

        while scrape:
            google_page_url = f"https://www.bing.com/search?q={search_query}&first={10 * (current_google_page_number - 1)}"   
            google_page_content = requests.get(google_page_url,headers={'User-Agent':"Mozilla/5.0 (X11; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0"})
            soup = BeautifulSoup(google_page_content.text,"html.parser")

            #Scrape all urls on google page
            page_results_container = soup.find('ol',id="b_results")
            list_items = page_results_container.find_all('li',class_='b_algo')

            for list_item in list_items:
                if total_results >= limit:
                    scrape = False
                    break
                site_on_page_url = list_item.find('cite').text
                # Get site html contents
                content = requests.get(site_on_page_url).content
                soup = BeautifulSoup(content,"html.parser")
                body = soup.find('body')
                body_text = body.text.strip(" ").strip("\n").replace("\n","")

                if site_on_page_url in previous_website_urls:continue
                previous_website_urls.add(site_on_page_url)

                yield convert_to_json({'text':body_text[:100] if len(body_text)>=100 else body_text,"url":site_on_page_url})

                print("Scraping...",total_results,'-->',site_on_page_url)
                total_results += 1
    return StreamingResponse(scrape(q,limit),media_type="text/json")
