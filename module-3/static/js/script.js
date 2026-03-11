const examples = [
    "This movie was absolutely fantastic! The acting was superb, the cinematography was breathtaking, and the story kept me engaged from start to finish. A true masterpiece!",
    "Terrible waste of time and money. The plot was predictable, the acting was wooden, and the special effects looked cheap. I walked out halfway through.",
    "It was okay, nothing special. Some parts were good but overall it felt a bit slow and could have been better with tighter editing."
];

function setExample(index) {
    document.getElementById('review').value = examples[index];
}

async function analyzeSentiment() {
    const review = document.getElementById('review').value.trim();
    const resultDiv = document.getElementById('result');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (!review) {
        alert('Please enter a review');
        return;
    }

    // Disable button and show loading state
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analyzing...';
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: review })
        });

        if (!response.ok) {
            throw new Error('Failed to analyze sentiment');
        }

        const data = await response.json();
        
        // Show result
        resultDiv.classList.remove('hidden');
        
        // Update sentiment badge
        const sentimentBadge = document.getElementById('sentimentBadge');
        sentimentBadge.textContent = data.sentiment.toUpperCase();
        sentimentBadge.className = 'sentiment-badge ' + data.sentiment;
        
        // Update confidence bar
        const confidencePercent = (data.confidence * 100).toFixed(2);
        const progressFill = document.getElementById('progressFill');
        progressFill.style.width = confidencePercent + '%';
        
        document.getElementById('confidenceText').textContent = confidencePercent + '%';
        
        // Scroll to result
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (error) {
        alert('Error: ' + error.message);
        console.error('Error:', error);
    } finally {
        // Re-enable button
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyze Sentiment';
    }
}

// Allow Enter key to submit (with Ctrl/Cmd)
document.getElementById('review').addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        analyzeSentiment();
    }
});
