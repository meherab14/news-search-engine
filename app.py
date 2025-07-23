from flask import Flask, request, render_template
import feedparser
import pandas as pd
import re

app = Flask(__name__)

# Function to clean text for better searching
def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    return text.lower().strip()

# Function to fetch news from Google News RSS
def fetch_news(search_terms, num_articles=50):
    rss_url = f"https://news.google.com/rss/search?q={search_terms}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    articles = []
    for entry in feed.entries[:num_articles]:
        article = {
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'description': entry.description,
            'source': entry.source.title if 'source' in entry else 'Unknown'
        }
        articles.append(article)
    
    return pd.DataFrame(articles)

# Function to search articles
def search_articles(df, search_terms):
    search_terms = clean_text(search_terms)
    results = df[df['title'].str.lower().str.contains(search_terms) |
                 df['description'].str.lower().str.contains(search_terms)]
    return results.to_dict('records')

@app.route('/', methods=['GET', 'POST'])
def news_search():
    results = []
    message = ""
    search_terms = ""
    
    if request.method == 'POST':
        search_terms = request.form.get('terms')
        if search_terms:
            df = fetch_news(search_terms)
            if not df.empty:
                results = search_articles(df, search_terms)
                if not results:
                    message = "No articles match your search terms."
                else:
                    message = f"Found {len(results)} matching articles."
            else:
                message = "No articles found. Try different search terms."
    
    return render_template('index.html', results=results, message=message, search_terms=search_terms)

if __name__ == '__main__':
    app.run(debug=True)
