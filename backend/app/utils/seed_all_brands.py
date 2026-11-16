"""
AMIT HOSPITALITY LLP — AUTHORITATIVE MULTI-BRAND SEEDING SCRIPT
Official Brands Portfolio Seeding:
1. Lord of the Drinks (South City Mall, Kolkata) - LOTD
2. Veneto Kitchen & Bar (South City Mall, Kolkata)
3. The Warehouse Cafe (South City Mall, Kolkata)
4. Deliite (Diamond Plaza Mall, Kolkata)

Reference: https://amithospitality.com/
Corporate Entity: Amit Hospitality LLP (Amit Bajoria & Vanita Bajoria, Founded 2018)
"""

import sys
import os
import logging

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models.outlet import Restaurant, Outlet, MenuCategory, MenuItem
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk, Policy, FAQ
from app.models.audit import AuditLog
from app.services.embedding_service import generate_embedding

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_all_brands")

BRAND_SEEDS = [
    {
        "name": "Veneto Kitchen and Bar",
        "slug": "veneto",
        "outlet_type": "Artisanal Kitchen, Pizzeria & Cocktail Bar",
        "cuisine_type": "Contemporary Italian, Mediterranean & Handcrafted Cocktails",
        "opening_time": "12:00",
        "closing_time": "23:30",
        "dress_code": "Smart Casual",
        "seating_capacity": 120,
        "location": "4th Floor, South City Mall, 375 Prince Anwar Shah Road, Kolkata - 700068",
        "description": "Authentic wood-fired culinary artistry, hand-rolled pasta, artisanal Neapolitan pizzas, and Mediterranean hospitality overlooking South City Mall.",
        "is_popular": True,
        "categories": [
            {
                "name": "Artisanal Neapolitan Pizzas",
                "display_order": 1,
                "items": [
                    {"name": "Burrata & San Marzano Margherita", "price": 795.0, "dietary": "VEG", "desc": "24-hr fermented dough, San Marzano D.O.P. tomato sauce, fresh creamy burrata, basil olive oil.", "signature": True},
                    {"name": "Tartufo Funghi & Smoked Scamorza", "price": 895.0, "dietary": "VEG", "desc": "Wild porcini, cremini mushrooms, white truffle oil, smoked scamorza, micro herbs.", "signature": True},
                    {"name": "Prosciutto di Parma & Arugula", "price": 995.0, "dietary": "NON_VEG", "desc": "Aged prosciutto, fresh baby arugula, shaved Parmigiano Reggiano 24 months, balsamic glaze.", "signature": False},
                ]
            },
            {
                "name": "Hand-Rolled Fresh Pasta",
                "display_order": 2,
                "items": [
                    {"name": "Handmade Spinach & Ricotta Ravioli", "price": 745.0, "dietary": "VEG", "desc": "Brown butter, crispy sage, toasted pine nuts, aged parmesan fonduta.", "signature": True},
                    {"name": "Slow-Braised Lamb Ragu Tagliatelle", "price": 845.0, "dietary": "NON_VEG", "desc": "Eight-hour braised lamb shoulder, fresh egg tagliatelle, rosemary gremolata.", "signature": True},
                    {"name": "Classic Spaghetti Aglio Olio e Peperoncino", "price": 625.0, "dietary": "VEG", "desc": "Extra virgin olive oil, confit garlic, peperoncino flakes, fresh parsley.", "signature": False},
                ]
            },
            {
                "name": "Mediterranean Small Plates & Antipasti",
                "display_order": 3,
                "items": [
                    {"name": "Truffle Arancini al Forno", "price": 545.0, "dietary": "VEG", "desc": "Crispy arborio rice croquettes, molten fontina center, truffle aioli.", "signature": False},
                    {"name": "Gamberi al Limone e Aglio", "price": 725.0, "dietary": "NON_VEG", "desc": "Sautéed tiger prawns, Amalfi lemon butter, garlic confit, grilled ciabatta.", "signature": True},
                ]
            },
            {
                "name": "Signature Handcrafted Cocktails",
                "display_order": 4,
                "items": [
                    {"name": "Veneto Smoked Negroni", "price": 695.0, "dietary": "VEG", "desc": "Botanical gin, Campari, artisanal sweet vermouth, smoked with applewood essence.", "signature": True},
                    {"name": "Amalfi Spritz Royale", "price": 645.0, "dietary": "VEG", "desc": "Limoncello di Capri, elderflower liqueur, prosecco, fresh mint spritz.", "signature": False},
                ]
            }
        ]
    },
    {
        "name": "The Warehouse Cafe",
        "slug": "the-warehouse-cafe",
        "outlet_type": "Contemporary Urban Industrial Cafe & Lounge",
        "cuisine_type": "Global Comfort Food, Gourmet Burgers, Asian Bowls & Sunday Brunch",
        "opening_time": "12:00",
        "closing_time": "00:00",
        "dress_code": "Casual / Smart Casual",
        "seating_capacity": 180,
        "location": "4th Floor, South City Mall, 375 Prince Anwar Shah Road, Kolkata - 700068",
        "description": "Opened in June 2022. Contemporary industrial café featuring chef-created recipes, craft cocktails, live music gigs, and Kolkata's favorite Sunday brunch.",
        "is_popular": True,
        "categories": [
            {
                "name": "Sunday Brunch Buffet (12 PM - 4 PM)",
                "display_order": 1,
                "items": [
                    {"name": "Sunday Grand Brunch Experience", "price": 999.0, "dietary": "VEG", "desc": "All-inclusive buffet spread: fluffy buttermilk pancakes, artisanal eggs made-to-order, deli sandwiches, gourmet salads, fruit platters, and decadent desserts (taxes applicable).", "signature": True},
                    {"name": "Brunch Craft Cocktail Add-On", "price": 499.0, "dietary": "VEG", "desc": "Free-flowing mimosas, bellinis, and warehouse craft beer flight during brunch hours.", "signature": False},
                ]
            },
            {
                "name": "Artisanal Burgers & Handhelds",
                "display_order": 2,
                "items": [
                    {"name": "The Warehouse Truffle Smash Burger", "price": 625.0, "dietary": "NON_VEG", "desc": "Double smashed tenderloin patties, sharp cheddar, truffle mushroom compote, brioche.", "signature": True},
                    {"name": "Crispy Panko Katsu Burger", "price": 545.0, "dietary": "VEG", "desc": "Crisp panko-crusted cottage cheese steak, spicy sriracha slaw, pickled cucumber.", "signature": False},
                ]
            },
            {
                "name": "Global Street Food & Small Plates",
                "display_order": 3,
                "items": [
                    {"name": "Gochujang Glazed Chicken Wings", "price": 525.0, "dietary": "NON_VEG", "desc": "Twice-fried crispy wings, Korean chili glaze, toasted sesame, spring scallions.", "signature": True},
                    {"name": "Avocado & Edamame Crostini", "price": 475.0, "dietary": "VEG", "desc": "Smashed Hass avocado, yuzu dressing, edamame beans, toasted sourdough.", "signature": False},
                ]
            },
            {
                "name": "Craft Mixology & Shakes",
                "display_order": 4,
                "items": [
                    {"name": "Smoked Hickory Bourbon Sour", "price": 675.0, "dietary": "VEG", "desc": "Kentucky bourbon, charred maple syrup, lemon bitters, flamed citrus peel.", "signature": True},
                    {"name": "Lotus Biscoff Freakshake", "price": 395.0, "dietary": "VEG", "desc": "Thick Belgian biscoff shake, whipped cream, caramel drizzle, crushed cookies.", "signature": False},
                ]
            }
        ]
    },
    {
        "name": "Deliite",
        "slug": "deliite",
        "outlet_type": "Premium Lifestyle Liquor, Beverage & Refreshment Retail",
        "cuisine_type": "Craft Beers, Fine Single Malts, Curated Wines, Gourmet Snacks & Munchies",
        "opening_time": "11:00",
        "closing_time": "22:00",
        "dress_code": "Casual",
        "seating_capacity": 30,
        "location": "3rd Floor, Diamond Plaza Mall, 68 Jessore Road, Kolkata - 700055",
        "description": "Kolkata's premier lifestyle beverage boutique on Diamond Plaza Mall's 3rd Floor, curating top domestic and international spirits, craft brews, mixers, and artisanal snacks.",
        "is_popular": True,
        "categories": [
            {
                "name": "Premium Craft Beers & Ciders",
                "display_order": 1,
                "items": [
                    {"name": "Belgian Witbier Craft Selection (Demonstration)", "price": 280.0, "dietary": "VEG", "desc": "Refreshing wheat ale brewed with coriander seeds and Curacao orange peel (Retail demo).", "signature": True},
                    {"name": "Hazy IPA Craft Can (Demonstration)", "price": 340.0, "dietary": "VEG", "desc": "Tropical fruit aromatics with soft bitterness and velvety mouthfeel.", "signature": False},
                ]
            },
            {
                "name": "Artisanal Mixers, Tonics & Beverages",
                "display_order": 2,
                "items": [
                    {"name": "Botanical Elderflower Tonic Water", "price": 120.0, "dietary": "VEG", "desc": "Natural quinine infused with handpicked wild English elderflower.", "signature": True},
                    {"name": "Sparkling Himalayan Mineral Spring Water", "price": 110.0, "dietary": "VEG", "desc": "Pristine mountain mineral water, light effervescence.", "signature": False},
                ]
            },
            {
                "name": "Gourmet Bar Snacks & Munchies",
                "display_order": 3,
                "items": [
                    {"name": "Truffle & Rosemary Roasted Cashews", "price": 350.0, "dietary": "VEG", "desc": "Slow-roasted jumbo Goan cashews tossed in black truffle salt and rosemary.", "signature": True},
                    {"name": "Wasabi Green Pea Crisps", "price": 180.0, "dietary": "VEG", "desc": "Crunchy roasted green peas coated in authentic Japanese wasabi seasoning.", "signature": False},
                ]
            }
        ]
    }
]

def seed_brands():
    db: Session = SessionLocal()
    try:
        restaurant = db.query(Restaurant).filter(Restaurant.slug == "amit-hospitality").first()
        if not restaurant:
            restaurant = Restaurant(
                name="Amit Hospitality LLP",
                slug="amit-hospitality",
                description="Parent hospitality enterprise operating luxury dining, nightlife, and lifestyle retail destinations across Kolkata.",
                address="401 Kamalalaya Centre, 156A Lenin Sarani, Kolkata - 700013",
                city="Kolkata",
                phone="+91 94323 35967",
                email="vanita@amithospitality.com",
                is_active=True,
            )
            db.add(restaurant)
            db.flush()
            logger.info("Created Amit Hospitality LLP parent restaurant entity.")

        for b_data in BRAND_SEEDS:
            outlet = db.query(Outlet).filter(Outlet.slug == b_data["slug"]).first()
            if not outlet:
                outlet = Outlet(
                    restaurant_id=restaurant.id,
                    name=b_data["name"],
                    slug=b_data["slug"],
                    outlet_type=b_data["outlet_type"],
                    cuisine_type=b_data["cuisine_type"],
                    opening_time=b_data["opening_time"],
                    closing_time=b_data["closing_time"],
                    dress_code=b_data["dress_code"],
                    seating_capacity=b_data["seating_capacity"],
                    location=b_data["location"],
                    description=b_data["description"],
                    is_popular=b_data["is_popular"],
                    is_active=True,
                )
                db.add(outlet)
                db.flush()
                logger.info(f"Seeded outlet: {outlet.name} (ID: {outlet.id})")
            else:
                logger.info(f"Outlet already exists: {outlet.name} (ID: {outlet.id})")

            # Seed Categories & Items for both DEMO and REAL environments
            for cat_data in b_data["categories"]:
                for env in ["DEMO", "REAL"]:
                    category = (
                        db.query(MenuCategory)
                        .filter(
                            MenuCategory.outlet_id == outlet.id,
                            MenuCategory.name == cat_data["name"],
                            MenuCategory.environment == env,
                        )
                        .first()
                    )
                    if not category:
                        category = MenuCategory(
                            outlet_id=outlet.id,
                            environment=env,
                            name=cat_data["name"],
                            display_order=cat_data["display_order"],
                            description=f"{cat_data['name']} at {outlet.name}",
                            is_active=True,
                        )
                        db.add(category)
                        db.flush()

                    for item_data in cat_data["items"]:
                        existing_item = (
                            db.query(MenuItem)
                            .filter(
                                MenuItem.outlet_id == outlet.id,
                                MenuItem.name == item_data["name"],
                                MenuItem.environment == env,
                            )
                            .first()
                        )
                        if not existing_item:
                            item = MenuItem(
                                category_id=category.id,
                                outlet_id=outlet.id,
                                environment=env,
                                name=item_data["name"],
                                description=item_data["desc"],
                                price=item_data["price"],
                                currency="INR",
                                dietary_flags=item_data["dietary"],
                                is_available=True,
                                is_signature=item_data.get("signature", False),
                                display_order=1,
                            )
                            db.add(item)

        db.commit()
        logger.info("Successfully seeded all 4 official Amit Hospitality brands into the database!")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding brands: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_brands()
