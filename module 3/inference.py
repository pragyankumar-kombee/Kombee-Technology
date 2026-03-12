import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

# Load trained model
tokenizer = DistilBertTokenizer.from_pretrained('./imdb_distilbert_model')
model = DistilBertForSequenceClassification.from_pretrained('./imdb_distilbert_model')
model.eval()

def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=-1).item()
    return "positive" if prediction == 1 else "negative"

# Example usage
if __name__ == "__main__":
    reviews = [
        "This movie was absolutely fantastic! I loved every minute of it.",
        "Terrible film, waste of time and money."
    ]
    
    for review in reviews:
        sentiment = predict_sentiment(review)
        print(f"Review: {review[:50]}...")
        print(f"Sentiment: {sentiment}\n")
