# Use
* Run `python crawl.py` from the root folder to start parsing.
One can use the `-c` option so as to remove already existing scrapped json files.
* Run `python populateES.py` from the root folder in order to populate your running ES instance with previously parsed data.

# Structure
* URLs to visit are generated in `crawler.py`: they are supposed to lead to JO publication summaries.
* The same spider is called on each of these URLs. It generates a list of the links leading to the articles of this publication and follows these links.
* Every article is parsed using the same spider.

# Article Parsing
Our article parser mainly does three things:
* it extracts all links contained in the article
* it parses all tables contained in the article (and converts them to JSON)
* it parses the text and removes all HTML tags
