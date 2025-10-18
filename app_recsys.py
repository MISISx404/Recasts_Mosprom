from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from collections import defaultdict
import numpy as np
import uvicorn

app = FastAPI(title="RecSys API", version="1.0.0")

# Модели данных
class UserAction(BaseModel):
    weight: int  # 2 - подписка, 1 - лайк, 0 - просмотр, -1 - дизлайк
    categories: List[str]
    age_segment: int

class UserProfile(BaseModel):
    selected_categories: List[str]
    age_segment: int
    subscriptions: List[int]
    viewed_posts: Optional[List[int]] = []


class Post(BaseModel):
    id: int
    title: str
    categories: List[str]
    age_segment: int
    community_id: int
    created_at: datetime

class RecommendationRequest(BaseModel):
    user_actions: List[UserAction]
    user_profile: UserProfile
    n_feed: Optional[int] = 10

def load_categories():
    """Загрузка категорий из файла"""
    with open('categories.txt', 'r', encoding='utf-8') as f:
        categories = [line.strip() for line in f.readlines() if line.strip()]
    return categories

CATEGORIES = load_categories()

communities = [
    {"id": 1, "name": "ML Клуб", "categories": ["Машинное обучение (ML)", "Анализ данных (Data Analysis)"]},
    {"id": 2, "name": "Backend Devs", "categories": ["Backend", "Node.js"]},
    {"id": 3, "name": "Frontend Heroes", "categories": ["Frontend", "React"]},
    {"id": 4, "name": "UI/UX Дизайн", "categories": ["UX/UI дизайн"]},
    {"id": 5, "name": "DevOps Space", "categories": ["DevOps", "Docker и контейнеризация"]},
]

now = datetime.now()
posts = [
    {"id": 1, "title": "Как обучить нейросеть на PyTorch", "categories": ["Машинное обучение (ML)"], "age_segment": 22, "community_id": 1, "created_at": now - timedelta(days=1)},
    {"id": 2, "title": "Основы Docker и CI/CD", "categories": ["DevOps", "Backend"], "age_segment": 25, "community_id": 5, "created_at": now - timedelta(days=2)},
    {"id": 3, "title": "UX/UI тренды 2025 года", "categories": ["UX/UI дизайн"], "age_segment": 21, "community_id": 4, "created_at": now - timedelta(days=1)},
    {"id": 4, "title": "Junior Backend стартовый гайд", "categories": ["Backend"], "age_segment": 20, "community_id": 2, "created_at": now - timedelta(days=4)},
    {"id": 5, "title": "Фронтенд на React", "categories": ["Frontend", "React"], "age_segment": 19, "community_id": 3, "created_at": now - timedelta(days=1)},
    {"id": 6, "title": "Data Science: первые шаги", "categories": ["Анализ данных (Data Analysis)", "Машинное обучение (ML)"], "age_segment": 23, "community_id": 1, "created_at": now - timedelta(days=1)},
    {"id": 7, "title": "Как стать продуктовым аналитиком", "categories": ["Управление продуктом (Product Management)", "Анализ данных (Data Analysis)"], "age_segment": 24, "community_id": 1, "created_at": now - timedelta(days=3)},
    {"id": 8, "title": "TensorFlow vs PyTorch: что выбрать?", "categories": ["Машинное обучение (ML)"], "age_segment": 23, "community_id": 1, "created_at": now - timedelta(days=5)},
    {"id": 9, "title": "Kubernetes для начинающих", "categories": ["DevOps"], "age_segment": 26, "community_id": 5, "created_at": now - timedelta(days=2)},
    {"id": 10, "title": "Vue.js vs React: сравнение", "categories": ["Frontend"], "age_segment": 22, "community_id": 3, "created_at": now - timedelta(days=1)},
    {"id": 11, "title": "Figma: продвинутые техники", "categories": ["UX/UI дизайн"], "age_segment": 20, "community_id": 4, "created_at": now - timedelta(days=3)},
    {"id": 12, "title": "PostgreSQL оптимизация", "categories": ["Backend", "Базы данных"], "age_segment": 25, "community_id": 2, "created_at": now - timedelta(days=4)},
    {"id": 13, "title": "A/B тестирование в продукте", "categories": ["Управление продуктом (Product Management)", "Анализ данных (Data Analysis)"], "age_segment": 24, "community_id": 1, "created_at": now - timedelta(days=2)},
    {"id": 14, "title": "Docker Compose для разработки", "categories": ["DevOps", "Docker и контейнеризация"], "age_segment": 23, "community_id": 5, "created_at": now - timedelta(days=1)},
    {"id": 15, "title": "TypeScript в React проектах", "categories": ["Frontend", "JavaScript / TypeScript"], "age_segment": 21, "community_id": 3, "created_at": now - timedelta(days=2)},
    {"id": 16, "title": "Scikit-learn: практические примеры", "categories": ["Машинное обучение (ML)", "Python"], "age_segment": 22, "community_id": 1, "created_at": now - timedelta(days=3)},
    {"id": 17, "title": "Микросервисы на Node.js", "categories": ["Backend", "Node.js", "Микросервисная архитектура"], "age_segment": 26, "community_id": 2, "created_at": now - timedelta(days=5)},
    {"id": 18, "title": "Адаптивный дизайн 2025", "categories": ["UX/UI дизайн", "Frontend"], "age_segment": 20, "community_id": 4, "created_at": now - timedelta(days=1)},
    {"id": 19, "title": "Метрики продукта: что измерять", "categories": ["Управление продуктом (Product Management)"], "age_segment": 25, "community_id": 1, "created_at": now - timedelta(days=4)},
    {"id": 20, "title": "GitLab CI/CD пайплайны", "categories": ["DevOps"], "age_segment": 24, "community_id": 5, "created_at": now - timedelta(days=2)},
]

# ML модель
class RecommendationModel:
    def __init__(self):
        self.model = LogisticRegression(random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def collect_training_data(self, user_profile):
        """Сбор данных для обучения под конкретного пользователя"""
        interactions = []
        
        for post in posts:
            same_cat = len(set(post["categories"]) & set(user_profile.selected_categories))
            age_diff = abs(post["age_segment"] - user_profile.age_segment)
            subscribed = 1 if post["community_id"] in user_profile.subscriptions else 0
            days_old = (now - post["created_at"]).days
            
            label = 0
            if same_cat >= 1 and age_diff <= 5 and subscribed == 1:
                label = 1
            elif same_cat >= 1 and days_old <= 2:
                label = 1
            elif subscribed == 1:
                label = 1
                
            interactions.append([same_cat, age_diff, subscribed, days_old])
            
            # Добавляем вариации для увеличения обучающей выборки
            age_variation = user_profile.age_segment + 1
            age_diff_var = abs(post["age_segment"] - age_variation)
            interactions.append([same_cat, age_diff_var, subscribed, days_old])
            
            interactions.append([same_cat, age_diff, 0, days_old])
                
        return np.array(interactions)
    
    def train(self, user_profile):
        """Обучение модели под конкретного пользователя"""
        features = self.collect_training_data(user_profile)
        
        labels = []
        for row in features:
            same_cat, age_diff, subscribed, days_old = row
            
            label = 0
            if same_cat >= 1 and age_diff <= 5 and subscribed == 1:
                label = 1
            elif same_cat >= 1 and days_old <= 2:
                label = 1
            elif subscribed == 1:
                label = 1
                
            labels.append(label)
        
        labels = np.array(labels)
        
        X_scaled = self.scaler.fit_transform(features)
        
        self.model.fit(X_scaled, labels)
        
        self.is_trained = True
        return True
    
    def predict(self, user_profile, post):
        """Предсказание для конкретного поста"""
        self.train(user_profile)
            
        same_cat = len(set(post["categories"]) & set(user_profile.selected_categories))
        age_diff = abs(post["age_segment"] - user_profile.age_segment)
        subscribed = 1 if post["community_id"] in user_profile.subscriptions else 0
        days_old = (now - post["created_at"]).days
        
        features = np.array([[same_cat, age_diff, subscribed, days_old]])
        
        features_scaled = self.scaler.transform(features)
        prob = self.model.predict_proba(features_scaled)[0][1]
        
        return prob

# Инициализация модели
model = RecommendationModel()

def recommend_for_user(user_actions: List[UserAction], user_profile: UserProfile, posts: List[Dict], min_actions_heuristic=5, min_actions_ml=10, n_feed=10):
    subscribed_posts = [
        p for p in posts 
        if p.get("community_id") in user_profile.subscriptions
        and p["id"] not in user_profile.viewed_posts
    ]
    subscribed_posts.sort(key=lambda p: p["created_at"], reverse=True)

    # Определяем стратегию
    if len(user_actions) < min_actions_heuristic:
        recs = [
            p for p in posts
            if any(cat in user_profile.selected_categories for cat in p["categories"])
            and abs(p["age_segment"] - user_profile.age_segment) <= 5
            and p["id"] not in user_profile.viewed_posts
        ]
    elif len(user_actions) < min_actions_ml:
        category_weights = defaultdict(int)
        for action in user_actions:
            for cat in action.categories:
                category_weights[cat] += action.weight

        scored_posts = []
        for post in posts:
            if post["id"] in user_profile.viewed_posts:
                continue
            score = sum(category_weights.get(cat, 0) for cat in post["categories"])
            score -= 0.1 * abs(post["age_segment"] - user_profile.age_segment)
            days_old = (now - post["created_at"]).days
            score += max(0, 2 - 0.2 * days_old)
            scored_posts.append((score, post))
        scored_posts.sort(key=lambda x: x[0], reverse=True)
        recs = [p for s, p in scored_posts if s > 0]
    else:
        recs = []
        for post in posts:
            if post["id"] in user_profile.viewed_posts:
                continue
            prob = model.predict(user_profile, post)
            recs.append((prob, post))
        recs.sort(key=lambda x: x[0], reverse=True)
        recs = [p for prob, p in recs]

    feed = []
    i, j = 0, 0
    while len(feed) < n_feed and (i < len(subscribed_posts) or j < len(recs)):
        for _ in range(3):
            if i < len(subscribed_posts) and len(feed) < n_feed:
                feed.append(subscribed_posts[i])
                i += 1
        if j < len(recs) and len(feed) < n_feed:
            rec = recs[j]
            if rec["id"] not in [p["id"] for p in feed]:
                feed.append(rec)
            j += 1

    return feed

@app.get("/posts")
async def get_posts():
    return {"posts": posts}

@app.get("/communities")
async def get_communities():
    return {"communities": communities}

@app.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    try:
        feed = recommend_for_user(
            request.user_actions, 
            request.user_profile, 
            posts, 
            n_feed=request.n_feed
        )
        
        # Добавляем информацию о сообществах
        result = []
        for post in feed:
            community = next((c["name"] for c in communities if c["id"] == post.get("community_id")), "Без сообщества")
            result.append({
                **post,
                "community_name": community
            })
        
        return {"feed": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
