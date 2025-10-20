import sys
import os

# Додаємо шлях до app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, engine
from app.models import Base, Location

def seed_locations():
    """Додаємо початкові локації"""
    
    # Створюємо таблиці
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Перевіряємо чи є вже локації
        existing = db.query(Location).count()
        if existing > 0:
            print(f"✅ База вже містить {existing} локацій. Пропускаємо seed.")
            return
        
        # Додаємо локації
        locations = [
            Location(
                name="Mark Mall",
                slug="mark-mall",
                address="Київська, 239, Бровари",
                city="Бровари",
                latitude=50.514794,
                longitude=30.782308,
                radius_meters=100,
                description="Кав'ярня в ТРЦ Mark Mall",
                is_active=True
            ),
            Location(
                name="Парк Приозерний",
                slug="park-priozerny",
                address="вул. Фіалковського, 27а, Бровари",
                city="Бровари",
                latitude=50.501265,
                longitude=30.754011,
                radius_meters=100,
                description="Кав'ярня біля парку Приозерний",
                is_active=True
            )
        ]
        
        for location in locations:
            db.add(location)
            print(f"➕ Додано: {location.name}")
        
        db.commit()
        print("✅ Seed завершено успішно!")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seed database...")
    seed_locations()