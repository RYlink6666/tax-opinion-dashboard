import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))
from utils.data_loader import load_analysis_data, get_sentiment_distribution

df = load_analysis_data()
print("Records:", len(df))
sentiment = get_sentiment_distribution(df)
print("Sentiments:", sentiment)
print("OK")
