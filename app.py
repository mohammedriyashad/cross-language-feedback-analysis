# Save this code as app.py

import streamlit as st # type: ignore
from langdetect import detect # type: ignore
from googletrans import Translator
import nltk # type: ignore
from nltk.corpus import stopwords # type: ignore
from nltk.stem import PorterStemmer # type: ignore
from nltk.tokenize import word_tokenize # type: ignore
from nltk.stem import WordNetLemmatizer # type: ignore
from nltk.sentiment.vader import SentimentIntensityAnalyzer # type: ignore
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.decomposition import NMF

# Download necessary NLTK data (if not already downloaded)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')


def detect_language(text):
    """
    Detects the language of the input text.

    Args:
      text: The input string (feedback text).

    Returns:
      The detected language code as a string.
    """
    try:
        return detect(text)
    except:
        return "unknown"


def translate_to_english(text):
    """
    Translates the input text to English.

    Args:
      text: The input string (feedback text) to be translated.

    Returns:
      The translated text in English, or the original text if translation fails.
    """
    try:
        translator = Translator()
        translated_text = translator.translate(text, dest='en').text
        return translated_text
    except Exception as e:
        print(f"Translation error: {e}")
        return text


def preprocess_text(text):
    """
    Cleans and preprocesses the translated English text for NLP analysis.

    Args:
      text: The input string (translated English text).

    Returns:
      A string containing the processed text with tokens joined by spaces,
      or an empty string if an error occurs.
    """
    try:
        # Convert to lowercase
        text = text.lower()

        # Tokenize text
        tokens = word_tokenize(text)

        # Remove stop words
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word not in stop_words]

        # Apply lemmatization
        lemmatizer = WordNetLemmatizer()
        lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]

        # Join tokens back into a string
        processed_text = " ".join(lemmatized_tokens)

        return processed_text
    except Exception as e:
        print(f"Preprocessing error: {e}")
        return ""


def analyze_sentiment(text):
    """
    Analyzes the sentiment of the preprocessed English text.

    Args:
      text: The preprocessed English text string.

    Returns:
      A string indicating the sentiment ('positive', 'negative', 'neutral')
      or 'unknown' if analysis fails.
    """
    try:
        analyzer = SentimentIntensityAnalyzer()
        sentiment_scores = analyzer.polarity_scores(text)

        # Determine sentiment based on compound score
        if sentiment_scores['compound'] >= 0.05:
            return 'positive'
        elif sentiment_scores['compound'] <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return "unknown"

# Optional Topic Modeling functions (uncomment if you want to include this feature)
# def get_top_words(model, feature_names, n_top_words):
#   """
#   Prints the top words for each topic in the NMF model.

#   Args:
#     model: The fitted NMF model.
#     feature_names: A list of feature names (words) from the TF-IDF vectorizer.
#     n_top_words: The number of top words to display per topic.
#   """
#   for topic_idx, topic in enumerate(model.components_):
#     print(f"Topic #{topic_idx + 1}:")
#     print(" ".join([feature_names[i]
#                     for i in topic.argsort()[:-n_top_words - 1:-1]]))
#   print()

def analyze_bulk_feedback(feedback_list):
    """
    Analyzes a list of feedback entries.

    Args:
      feedback_list: A list of strings, where each string is a feedback entry.

    Returns:
      A list of dictionaries, where each dictionary contains the original
      feedback, detected language, translated text (if applicable),
      preprocessed text, and sentiment.
    """
    results = []
    for feedback in feedback_list:
        detected_lang = detect_language(feedback)
        translated_text = feedback
        if detected_lang != 'en':
            translated_text = translate_to_english(feedback)

        preprocessed_text = preprocess_text(translated_text)
        sentiment = analyze_sentiment(preprocessed_text)

        results.append({
            'original_feedback': feedback,
            'detected_language': detected_lang,
            'translated_text': translated_text,
            'preprocessed_text': preprocessed_text,
            'sentiment': sentiment
        })
    return results


def main():
    st.title("Cross-Language Feedback Analysis")

    feedback_input = st.text_area("Enter customer feedback (one entry per line):", height=200)

    if st.button("Analyze Feedback"):
        if feedback_input:
            feedback_list = feedback_input.strip().split('\n')
            results = analyze_bulk_feedback(feedback_list)

            st.subheader("Analysis Results:")
            for result in results:
                st.write(f"**Original Feedback:** {result['original_feedback']}")
                st.write(f"**Detected Language:** {result['detected_language']}")
                st.write(f"**Translated Text:** {result['translated_text']}")
                st.write(f"**Sentiment:** {result['sentiment']}")
                st.write("---")
        else:
            st.warning("Please enter feedback to analyze.")

if __name__ == "__main__":
    main()