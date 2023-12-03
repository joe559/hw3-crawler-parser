from bs4 import BeautifulSoup
import pymongo

# Set up MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["crawlerDB"]

# Collections
pages_collection = db["pages"]  # Collection where pages are stored
professors_collection = db["professors"]  # Collection to store professor data

# Function to parse faculty information and store it
def parse_faculty_information(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Find all 'div' tags with the class 'clearfix', which contain the faculty info
    faculty_divs = soup.find_all('div', class_='clearfix')
    
    for div in faculty_divs:
        # Initialize a dictionary to store the faculty member's information
        faculty_data = {}
        
        # The name is the text of the first 'h2' tag within the div
        faculty_data['name'] = div.h2.get_text(strip=True) if div.h2 else None
        
        # All details are contained within 'p' tags directly under the div
        paragraphs = div.find_all('p')
        for p in paragraphs:
            # Extract title, office, email, and website
            if p.strong and 'Title:' in p.text:
                faculty_data['title'] = p.strong.next_sibling.strip()
            if p.strong and 'Office:' in p.text:
                faculty_data['office'] = p.strong.next_sibling.strip()
            if p.strong and 'Email:' in p.text:
                # Email is contained within an 'a' tag
                faculty_data['email'] = p.a.get_text(strip=True)
            if p.strong and 'Web:' in p.text:
                # Website is the 'href' of the first 'a' tag after the 'Web:' text
                # that does not contain 'mailto:' in the 'href'
                web_tag = p.find('a', href=lambda href: 'mailto:' not in href)
                if web_tag:
                    faculty_data['website'] = web_tag['href'].strip()

        # Store the faculty member's information in MongoDB
        professors_collection.insert_one(faculty_data)
    
# Retrieve the Permanent Faculty page HTML from the pages collection
permanent_faculty_page = pages_collection.find_one({"url": "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"})

if permanent_faculty_page:
    parse_faculty_information(permanent_faculty_page['html'])
else:
    print("Permanent Faculty page HTML not found in the database.")
