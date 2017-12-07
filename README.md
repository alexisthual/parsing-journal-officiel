# Use
Run `python crawler.py` from the root folder to start parsing.

# Structure
* URLs to visit are generated in `crawler.py`: they are supposed to lead to JO publication summaries.
* The same spider is called on each of these URLs. It generates a list of the links leading to the articles of this publication and follows these links.
* Every article is parsed using the same spider.

# Article Parsing
Our article parser mainly does three things:
* it extracts all links contained in the article
* it parses all tables contained in the article (and converts them to JSON)
* it parses the text and removes all HTML tags
