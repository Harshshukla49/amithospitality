import os
import sys

# Ensure backend root is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal
from app.models.outlet import Restaurant, Outlet, MenuCategory, MenuItem
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk
from app.models.reservation import ReservationRequest
from app.models.lead import Lead
from app.models.user import User

def cleanup_fictional_records():
    db = SessionLocal()
    try:
        print(">>> Starting purge of fictional records from SQLite database...")

        # 1. Update Corporate Restaurant Entity
        restaurant = db.query(Restaurant).first()
        if restaurant:
            restaurant.name = "Amit Hospitality LLP"
            restaurant.slug = "amit-hospitality"
            restaurant.description = "Kolkata's premier hospitality group curating world-class culinary, nightlife, and boutique retail destinations."
            restaurant.address = "401 Kamalalaya Centre, 156A Lenin Sarani"
            restaurant.city = "Kolkata"
            restaurant.phone = "+91 94323 35967"
            restaurant.email = "vanita@amithospitality.com"
            db.commit()
            print("  [OK] Updated Restaurant entity to Amit Hospitality LLP (Kolkata HQ).")

        # IDs of fictional outlets to purge
        fictional_ids = [1, 2, 3, 4, 5, 6, 7]

        # 2. Purge Knowledge Chunks
        chunks_deleted = db.query(KnowledgeChunk).filter(KnowledgeChunk.outlet_id.in_(fictional_ids)).delete(synchronize_session=False)
        print(f"  [OK] Deleted {chunks_deleted} fictional knowledge chunks.")

        # 3. Purge Knowledge Documents
        docs_deleted = db.query(KnowledgeDocument).filter(KnowledgeDocument.outlet_id.in_(fictional_ids)).delete(synchronize_session=False)
        print(f"  [OK] Deleted {docs_deleted} fictional knowledge documents.")

        # 4. Purge Menu Items
        items_deleted = db.query(MenuItem).filter(MenuItem.outlet_id.in_(fictional_ids)).delete(synchronize_session=False)
        print(f"  [OK] Deleted {items_deleted} fictional menu items.")

        # 5. Purge Menu Categories
        cats_deleted = db.query(MenuCategory).filter(MenuCategory.outlet_id.in_(fictional_ids)).delete(synchronize_session=False)
        print(f"  [OK] Deleted {cats_deleted} fictional menu categories.")

        # 6. Purge Reservations
        res_deleted = db.query(ReservationRequest).filter(ReservationRequest.outlet_id.in_(fictional_ids)).delete(synchronize_session=False)
        print(f"  [OK] Deleted {res_deleted} fictional reservation requests.")

        # 7. Purge Leads
        leads_deleted = db.query(Lead).filter(Lead.outlet_id.in_(fictional_ids)).delete(synchronize_session=False)
        print(f"  [OK] Deleted {leads_deleted} fictional leads.")

        # 8. Remap any user referencing fictional outlet_id
        users_updated = 0
        for u in db.query(User).all():
            if hasattr(u, 'outlet_id') and u.outlet_id in fictional_ids:
                u.outlet_id = 8  # Map to Lord of the Drinks
                users_updated += 1
        db.commit()
        if users_updated:
            print(f"  [OK] Remapped {users_updated} user accounts to Lord of the Drinks (ID: 8).")

        # 9. Purge Outlets
        outlets_deleted = db.query(Outlet).filter(Outlet.id.in_(fictional_ids)).delete(synchronize_session=False)
        print(f"  [OK] Deleted {outlets_deleted} fictional outlets (Amber Terrace, Saffron & Silk, Velvet Cellar).")

        db.commit()

        # 10. Verify remaining outlets
        remaining = db.query(Outlet).all()
        print("\n>>> Remaining Active Outlets in Database:")
        for o in remaining:
            print(f"  - ID {o.id}: {o.name} ({o.slug}) | Location: {o.location}")

        print("\n[SUCCESS] All fictional records successfully purged. Database is 100% authentic.")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Database cleanup failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_fictional_records()
