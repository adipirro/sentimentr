import logging
import re

from flask import Flask, jsonify, request
from textblob import TextBlob
from markdown import markdown
from bs4 import BeautifulSoup

# Setup tasks
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#
# App Routing
#

@app.route("/analyze", methods=["POST"])
def analyze_request():
    text_to_analyze = request.json['text']

    if text_to_analyze:
        analysis = sentiment_analysis(text_to_analyze)
    else:
        analysis = {
            "error": "No text recieved"
        }

    return jsonify(analysis)

#
# Helper Functions
#

def sentiment_analysis(text):
    """
    Analyzes a string of stuff for sentiment
    """
    if text == None:
        return {
            "error": "No text to process"
        }

    cleaned_text = clean_text(text)

    text_blob = TextBlob(cleaned_text)

    breakdown = sentiment_breakdown(text_blob)

    sentiment_dict = {
        'analyzed_text': cleaned_text,
        'polarity': text_blob.polarity,
        'subjectivity': text_blob.subjectivity,
        'breakdown': breakdown
    }

    return sentiment_dict

def sentiment_breakdown(blob):
    """
    Gives sentiment breakdown of text by sentence
    """
    sentiment_breakdown = []
    for sentence in blob.sentences:
        senctence_sentiment = {
            'sentence': sentence.raw,
            'polarity': sentence.polarity,
            'subjectivity': sentence.subjectivity
        }
        sentiment_breakdown.append(senctence_sentiment)

    return sentiment_breakdown

def clean_text(text):
    """
    Converts text to html and uses BeautifulSoup to clean it up
    Also strips code blocks from text
    """
    text = re.sub(r"(\s*```[a-z]*\n[\s\S]*?\n\s*```)", "", text)

    html = markdown(text)
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()

# Flask start
if __name__ == "__main__":
    app.run(host='0.0.0.0')
