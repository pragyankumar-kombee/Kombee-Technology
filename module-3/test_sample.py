import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

# Load trained model
print("Loading model...")
tokenizer = DistilBertTokenizer.from_pretrained('./imdb_distilbert_model')
model = DistilBertForSequenceClassification.from_pretrained('./imdb_distilbert_model')
model.eval()

def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=-1).item()
        probabilities = torch.softmax(logits, dim=-1)[0]
    
    sentiment = "positive" if prediction == 1 else "negative"
    confidence = float(probabilities[prediction]) * 100
    
    return sentiment, confidence

# Sample movie reviews to test
sample_reviews = [
    "This movie was absolutely fantastic! The acting was superb and the plot kept me engaged throughout.",
    "Terrible waste of time. Poor acting, boring storyline, and awful special effects.",
    "One of the best films I've ever seen. A masterpiece of cinema!",
    "I fell asleep halfway through. Completely boring and predictable.",
    "Great movie with amazing visuals and a touching story. Highly recommend!",
    "The worst movie ever made. I want my money back.",
    "Decent film, nothing special but entertaining enough for a weekend watch.",
    "Absolutely loved it! The director did an incredible job bringing this story to life."
]

print("\n" + "="*80)
print("SENTIMENT ANALYSIS RESULTS")
print("="*80 + "\n")

for i, review in enumerate(sample_reviews, 1):
    sentiment, confidence = predict_sentiment(review)
    
    print(f"Review {i}:")
    print(f"Text: {review}")
    print(f"Sentiment: {sentiment.upper()} (Confidence: {confidence:.2f}%)")
    print("-" * 80)
