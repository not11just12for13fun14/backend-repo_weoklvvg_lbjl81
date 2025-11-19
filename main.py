import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import Gift, Order, Testimonial

app = FastAPI(title="E‑Gifts Premium Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "E‑Gifts API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or ("✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Seed demo data if empty
@app.on_event("startup")
async def seed_demo():
    if db is None:
        return
    if db["gift"].count_documents({}) == 0:
        demo_gifts = [
            {
                "title": "Love Notes: Daily Reminders",
                "slug": "love-notes-daily",
                "tagline": "Нежные напоминания каждый день",
                "description": "Телеграм‑бот, который шлет ей персональные комплименты и напоминания, почему она самая лучшая.",
                "price": 14.99,
                "badge": "Хит",
                "category": "reminders",
                "cover": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?q=80&w=1200&auto=format&fit=crop",
                "gallery": [],
                "features": [
                    "Индивидуальные сообщения",
                    "Гибкий график",
                    "Теплый тон общения",
                ],
                "rating": 4.9,
            },
            {
                "title": "Mini‑Game: Catch the Hearts",
                "slug": "catch-the-hearts",
                "tagline": "Милый таймкиллер в браузере",
                "description": "Лёгкая аркада в розовом неоне — собери сердца и получи послание любви.",
                "price": 9.99,
                "badge": "Новинка",
                "category": "games",
                "cover": "https://images.unsplash.com/photo-1496302662116-35cc4f36df92?q=80&w=1200&auto=format&fit=crop",
                "gallery": [],
                "features": [
                    "Мягкие анимации",
                    "Секретные уровни",
                    "Поделиться результатом",
                ],
                "rating": 4.7,
            },
            {
                "title": "Memory Lane: Наши моменты",
                "slug": "memory-lane",
                "tagline": "Цифровой альбом с эффектами",
                "description": "Красивый веб‑альбом с плавной музыкой и эффектом параллакса, куда можно добавить ваши фото и подписи.",
                "price": 19.99,
                "badge": "Premium",
                "category": "notes",
                "cover": "https://images.unsplash.com/photo-1512428559087-560fa5ceab42?q=80&w=1200&auto=format&fit=crop",
                "gallery": [],
                "features": [
                    "Параллакс галерея",
                    "Музыка на фоне",
                    "Секретное послание",
                ],
                "rating": 5.0,
            },
        ]
        for g in demo_gifts:
            try:
                db["gift"].insert_one({**g})
            except Exception:
                pass

    if db["testimonial"].count_documents({}) == 0:
        testimonials = [
            {"author": "Анна", "role": "Москва", "content": "Бот с напоминаниями — это просто магия!", "rating": 5},
            {"author": "Игорь", "role": "СПб", "content": "Мини‑игра очень милая, идеальный сюрприз.", "rating": 5},
        ]
        for t in testimonials:
            try:
                db["testimonial"].insert_one({**t})
            except Exception:
                pass

# DTOs for responses
class GiftResponse(BaseModel):
    title: str
    slug: str
    tagline: str | None = None
    description: str
    price: float
    badge: str | None = None
    category: str
    cover: str | None = None
    rating: float | None = None

@app.get("/api/gifts", response_model=List[GiftResponse])
def list_gifts():
    if db is None:
        # Fallback fake data when DB is not configured
        return [
            GiftResponse(
                title="Love Notes: Daily Reminders",
                slug="love-notes-daily",
                tagline="Нежные напоминания каждый день",
                description="Телеграм‑бот с персональными комплиментами",
                price=14.99,
                badge="Хит",
                category="reminders",
                cover="https://images.unsplash.com/photo-1515879218367-8466d910aaa4?q=80&w=1200&auto=format&fit=crop",
                rating=4.9,
            ),
            GiftResponse(
                title="Mini‑Game: Catch the Hearts",
                slug="catch-the-hearts",
                tagline="Милый таймкиллер в браузере",
                description="Собери сердца и получи послание любви",
                price=9.99,
                badge="Новинка",
                category="games",
                cover="https://images.unsplash.com/photo-1496302662116-35cc4f36df92?q=80&w=1200&auto=format&fit=crop",
                rating=4.7,
            ),
        ]
    docs = get_documents("gift")
    result = []
    for d in docs:
        result.append(GiftResponse(
            title=d.get("title"),
            slug=d.get("slug"),
            tagline=d.get("tagline"),
            description=d.get("description"),
            price=float(d.get("price", 0)),
            badge=d.get("badge"),
            category=d.get("category"),
            cover=d.get("cover"),
            rating=float(d.get("rating", 0)) if d.get("rating") is not None else None,
        ))
    return result

class CreateOrderRequest(Order):
    pass

@app.post("/api/orders")
def create_order(payload: CreateOrderRequest):
    total_calc = round(sum(item.price * item.quantity for item in payload.items), 2)
    if abs(total_calc - payload.total) > 0.01:
        raise HTTPException(status_code=400, detail="Total mismatch")

    if db is None:
        # Simulate order accepted without persistence
        return {"status": "accepted", "order_id": "demo", "message": "Заказ принят. Мы свяжемся для доставки цифрового подарка."}

    order_id = create_document("order", payload)
    return {"status": "accepted", "order_id": order_id}

class TestimonialResponse(BaseModel):
    author: str
    role: str | None = None
    content: str
    rating: float | None = None

@app.get("/api/testimonials", response_model=List[TestimonialResponse])
def list_testimonials():
    if db is None:
        return [
            TestimonialResponse(author="Анна", role="Москва", content="Бот с напоминаниями — это просто магия!", rating=5),
            TestimonialResponse(author="Игорь", role="СПб", content="Мини‑игра очень милая, идеальный сюрприз.", rating=5),
        ]
    docs = get_documents("testimonial")
    return [TestimonialResponse(author=d.get("author"), role=d.get("role"), content=d.get("content"), rating=float(d.get("rating", 0)) if d.get("rating") is not None else None) for d in docs]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
