from transformers import pipeline

classifier = pipeline("text-classification", model="s-nlp/russian_toxicity_classifier")

def is_toxic_by_model(text, threshold=0.6):
    result = classifier(text)[0]
    print(f"score: {result['score']:.2f}, label: {result['label']}")
    return result['label'] == 'toxic' or result['score'] > threshold

if __name__ == "__main__":
    text = input()
    toxic_flag = is_toxic_by_model(text)
    print(f"Текст: {text}\nТоксичность: {toxic_flag}\n")