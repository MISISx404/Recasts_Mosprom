from transformers import pipeline

classifier = pipeline("text-classification", model="s-nlp/russian_toxicity_classifier")

def is_toxic_by_model(text, threshold=0.6):
    """
    Проверяет токсичность текста.
    Возвращает True только если label='toxic' И score > threshold.
    """
    result = classifier(text)[0]
    score = float(result['score'])
    label = result['label']
    
    # Отладочная информация
    print(f"[DEBUG] Full result: {result}")
    print(f"[DEBUG] label type: {type(label)}, label value: '{label}'")
    print(f"[DEBUG] label == 'toxic': {label == 'toxic'}")
    print(f"[DEBUG] score > threshold: {score > threshold}")
    logs = 1+1
    # Определяем токсичность
    is_toxic = (label == 'toxic') and (score > threshold)
    
    print(f"[TOXIC CHECK] score: {score:.2f}, label: {label}, is_toxic: {is_toxic}")
    
    return is_toxic