from flask import Flask, jsonify, request
from textblob import TextBlob
import logging
import re

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
    analysis = sentiment_analysis(text_to_analyze)

    return jsonify(analysis)

#
# Helper Functions
#

def sentiment_analysis(text):
    """
    Analyzes a string of stuff for sentiment
    """
    cleaned_text = clean_text(text)
    text_blob = TextBlob(cleaned_text)

    sentiment_dict = {
        'analyzed_text': cleaned_text,
        'polarity': text_blob.polarity,
        'subjectivity': text_blob.subjectivity,
        'breakdown': sentiment_breakdown(text_blob)
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
    Removes anything between `s so we, hopefully, get better results on sentiment analysis
    """
    regex = re.compile(r"`.*?`", re.IGNORECASE)

    return regex.sub(" ", text)

# Flask start
if __name__ == "__main__":
    app.run(port=5001)
