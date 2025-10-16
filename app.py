import streamlit as st
import pandas as pd
from textblob import TextBlob
from deep_translator import GoogleTranslator
from langdetect import detect
import matplotlib.pyplot as plt # type: ignore

# Page setup
st.set_page_config(page_title="🌍 Cross-Language Feedback Analysis Dashboard", layout="wide")

st.title("🌍 Cross-Language Feedback Analysis using NLP")
st.write("Analyze multilingual customer feedback with automatic translation and sentiment visualization.")

# --- Single feedback section ---
st.header("🗣 Single Feedback Analysis")
feedback_text = st.text_area("Enter feedback in any language:")

if st.button("Analyze Feedback"):
    if feedback_text.strip():
        try:
            # Detect and translate
            detected_lang = detect(feedback_text)
            translated = GoogleTranslator(source='auto', target='en').translate(feedback_text)

            # Sentiment analysis
            blob = TextBlob(translated)
            sentiment = blob.sentiment.polarity # type: ignore

            # Display results
            st.subheader("🔍 Analysis Result")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"*Detected Language:* {detected_lang.upper()}")
                st.write(f"*Original Feedback:* {feedback_text}")
            with col2:
                st.write(f"*Translated Feedback:* {translated}")

            # Sentiment result
            if sentiment > 0:
                st.success(f"😊 Positive Sentiment (Score: {sentiment:.2f})")
            elif sentiment < 0:
                st.error(f"😠 Negative Sentiment (Score: {sentiment:.2f})")
            else:
                st.info(f"😐 Neutral Sentiment (Score: {sentiment:.2f})")
        except Exception as e:
            st.error(f"Error during processing: {e}")
    else:
        st.warning("Please enter feedback text.")

st.markdown("---")

# --- Bulk file upload section ---
st.header("📂 Bulk Feedback Upload & Dashboard")
uploaded_file = st.file_uploader("Upload a CSV or Excel file (must contain a 'feedback' column)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Read file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if 'feedback' not in df.columns:
            st.error("The file must contain a 'feedback' column.")
        else:
            st.write("### Preview of Uploaded Data")
            st.dataframe(df.head())

            if st.button("Run Bulk Analysis"):
                translated_texts, sentiments, sentiment_labels, detected_langs = [], [], [], []

                with st.spinner("Processing all feedback..."):
                    for text in df['feedback']:
                        try:
                            lang = detect(str(text))
                            translated = GoogleTranslator(source='auto', target='en').translate(str(text))
                            blob = TextBlob(translated)
                            sentiment_score = blob.sentiment.polarity # type: ignore

                            detected_langs.append(lang)
                            translated_texts.append(translated)
                            sentiments.append(sentiment_score)
                            sentiment_labels.append(
                                "Positive" if sentiment_score > 0 else
                                "Negative" if sentiment_score < 0 else
                                "Neutral"
                            )
                        except Exception:
                            detected_langs.append("error")
                            translated_texts.append("Translation error")
                            sentiments.append(0)
                            sentiment_labels.append("Neutral")

                # Append results to dataframe
                df['detected_language'] = detected_langs
                df['translated_feedback'] = translated_texts
                df['sentiment_score'] = sentiments
                df['sentiment'] = sentiment_labels

                st.success("✅ Analysis Completed!")

                # --- Dashboard Section ---
                st.subheader("📊 Sentiment Dashboard")
                col1, col2, col3 = st.columns(3)
                total = len(df)
                positives = len(df[df['sentiment'] == 'Positive'])
                negatives = len(df[df['sentiment'] == 'Negative'])
                neutrals = len(df[df['sentiment'] == 'Neutral'])

                col1.metric("😊 Positive", positives)
                col2.metric("😐 Neutral", neutrals)
                col3.metric("😠 Negative", negatives)

                # Bar chart visualization
                st.write("### Sentiment Distribution")
                sentiment_counts = df['sentiment'].value_counts()
                st.bar_chart(sentiment_counts)

                # Pie chart
                fig, ax = plt.subplots()
                ax.pie(sentiment_counts, labels= sentiment_counts.index, autopct="%1.1f%%", startangle=90) # type: ignore
                ax.axis("equal")
                st.pyplot(fig)

                # Language distribution
                st.write("### Detected Language Distribution")
                lang_counts = df['detected_language'].value_counts()
                st.bar_chart(lang_counts)

                # Show analyzed data
                st.write("### Full Analysis Data")
                st.dataframe(df[['feedback', 'detected_language', 'translated_feedback', 'sentiment', 'sentiment_score']])

                # Download option
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("⬇ Download Results as CSV", data=csv, file_name="feedback_analysis_results.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error: {e}")