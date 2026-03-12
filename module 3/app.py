from flask import Flask, request, jsonify, render_template
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

app = Flask(__name__)

# Load model
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
    
    return {
        "sentiment": "positive" if prediction == 1 else "negative",
        "confidence": float(probabilities[prediction])
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    result = predict_sentiment(text)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
