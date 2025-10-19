from transformers import pipeline

classifier = pipeline("text-classification", model="s-nlp/russian_toxicity_classifier")

def is_toxic_by_model(text, threshold = 0.6):
    result = classifier(text)[0]
    score = result['score']
    label = result['label']
    print(f"score: {score:.2f}, label: {label}")
    return label == 'neutral' and float(score) > threshold 