import re
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pymongo

# Set up MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
#  set up database and collections
db = client["crawlerDB"]
pages_collection = db["pages"]

# Define target page
target_heading = "Permanent Faculty"

# Define frontier class
class Frontier:
    def __init__(self):
        self.visited_urls = set()
        self.pending_urls = []

    # add url to queue
    def add_url(self, url):
        if url not in self.visited_urls:
            self.pending_urls.append(url)

    #get next url in queue
    def next_url(self):
        return self.pending_urls.pop(0) if self.pending_urls else None

    # check if frontier is empty
    def done(self):
        return len(self.pending_urls) == 0

    # mark url as visited
    def mark_visited(self, url):
        self.visited_urls.add(url)

# retrieve and open url
def retrieve_url(url):
    try:
        response = urlopen(url) 
        return response
    except HTTPError as e:
        print(e)
    except URLError as e:
        print("Server not be found.")
    except Exception as e:
        print("error")

# store page
def store_page(url, html):
    pages_collection.insert_one({"url": url, "html": html})

# check if the current page is the target page
def target_page(html):
    bs = BeautifulSoup(html, 'html.parser')
    # get page heading
    if bs.find("h1", string=target_heading):
        print("found target")
        return True
    else:
        return False

# Crawler main from peusdocode
def crawler_thread(frontier):
    while not frontier.done():

        url = frontier.next_url()
        if not url:
            break
        print(f"Retrieved {url}")
        
        html = retrieve_url(url)
        if not html:
            continue
        html = html.read()

        store_page(url, html)

        if target_page(html):
            break
        else:
            # Parse the HTML for links and add to the frontier
            bs = BeautifulSoup(html, 'html.parser')
            for link in bs.find_all('a', href=True):
                href = link['href']
                # Fix relative links before adding
                if (re.match("^https://www.cpp.edu", href) == None):
                    href = "https://www.cpp.edu" + href
                frontier.add_url(href)

        frontier.mark_visited(url)

# Initialize frontier with starting URL
frontier = Frontier()
frontier.add_url('https://www.cpp.edu/sci/computer-science/')

# Start crawler
crawler_thread(frontier)