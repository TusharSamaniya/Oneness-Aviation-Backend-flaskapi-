"""
Seed script — populates the database with initial data.

Run from the project root:
    python -m scripts.seed

Prerequisites:
    - .env file configured
    - Database running
    - Tables created (run the app once in DEBUG mode or run alembic upgrade head)
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database import AsyncSessionLocal, engine, Base
from app.models.aircraft import Aircraft, AircraftCategory, AirportDistance
from app.models.membership import MembershipPlan, MembershipTier
from app.models.blog import FAQ, Testimonial, BlogPost
from app.models.user import User, UserRole
from app.services.auth_service import hash_password


# ── Aircraft Categories ───────────────────────────────────────────────────────
CATEGORIES = [
    {"slug": "light-jet",    "label": "Light Jets",        "icon": "✈", "sort_order": 1},
    {"slug": "midsize-jet",  "label": "Midsize Jets",       "icon": "✈", "sort_order": 2},
    {"slug": "heavy-jet",    "label": "Heavy Jets",         "icon": "✈", "sort_order": 3},
    {"slug": "ulr",          "label": "Ultra Long Range",   "icon": "✈", "sort_order": 4},
    {"slug": "helicopter",   "label": "Helicopters",        "icon": "🚁", "sort_order": 5},
]

# ── Aircraft Fleet ────────────────────────────────────────────────────────────
AIRCRAFT = [
    # Light Jets
    {
        "slug": "cessna-citation-xls", "category": "light-jet", "category_label": "Light Jet",
        "name": "Cessna Citation XLS", "tagline": "The benchmark light jet for regional travel",
        "passengers": 9, "range_km": 3700, "range_nm": 2000, "speed_kmh": 795,
        "ceiling_ft": 45000, "baggage_kg": 180,
        "price_per_hour": 220000, "price_from_display": "₹2.2L / hr",
        "image": "https://images.unsplash.com/photo-1474302770737-173ee21bab63?w=900&q=80",
        "cabin_features": ["Leather seating", "Club-4 configuration", "In-flight Wi-Fi", "Refreshment centre"],
        "ideal_for": ["Regional hops", "Small business groups", "Quick turnarounds"],
        "is_popular": True,
    },
    {
        "slug": "embraer-phenom-300", "category": "light-jet", "category_label": "Light Jet",
        "name": "Embraer Phenom 300", "tagline": "World's best-selling light jet, four years running",
        "passengers": 9, "range_km": 3650, "range_nm": 1971, "speed_kmh": 834,
        "ceiling_ft": 45000, "baggage_kg": 198,
        "price_per_hour": 240000, "price_from_display": "₹2.4L / hr",
        "image": "https://images.unsplash.com/photo-1540962351504-03099e0a754b?w=900&q=80",
        "cabin_features": ["Ergonomic seating", "Flat-floor cabin", "Baggage access inflight", "HD entertainment"],
        "ideal_for": ["Business travel", "Weekend getaways", "Short international hops"],
        "is_popular": False,
    },
    {
        "slug": "pilatus-pc-12", "category": "light-jet", "category_label": "Turboprop",
        "name": "Pilatus PC-12 NGX", "tagline": "The turboprop that accesses runways jets cannot",
        "passengers": 9, "range_km": 3417, "range_nm": 1845, "speed_kmh": 528,
        "ceiling_ft": 30000, "baggage_kg": 320,
        "price_per_hour": 160000, "price_from_display": "₹1.6L / hr",
        "image": "https://images.unsplash.com/photo-1556388158-158ea5ccacbd?w=900&q=80",
        "cabin_features": ["Large cargo door", "Short-field capability", "Single-pilot ops", "Medical config available"],
        "ideal_for": ["Remote locations", "Air ambulance", "Cargo + passenger mix"],
        "is_popular": False,
    },
    # Midsize Jets
    {
        "slug": "hawker-800xp", "category": "midsize-jet", "category_label": "Midsize Jet",
        "name": "Hawker 800XP", "tagline": "The workhorse of Indian private aviation",
        "passengers": 8, "range_km": 4800, "range_nm": 2593, "speed_kmh": 820,
        "ceiling_ft": 41000, "baggage_kg": 295,
        "price_per_hour": 340000, "price_from_display": "₹3.4L / hr",
        "image": "https://images.unsplash.com/photo-1585893153434-b1e9ff59e87b?w=900&q=80",
        "cabin_features": ["Stand-up cabin", "Club seating", "Galley", "Private lavatory"],
        "ideal_for": ["Domestic + SE Asia", "Corporate delegations", "VIP movement"],
        "is_popular": True,
    },
    {
        "slug": "cessna-citation-sovereign", "category": "midsize-jet", "category_label": "Midsize Jet",
        "name": "Cessna Citation Sovereign", "tagline": "Transatlantic reach in a midsize frame",
        "passengers": 9, "range_km": 5185, "range_nm": 2800, "speed_kmh": 833,
        "ceiling_ft": 47000, "baggage_kg": 306,
        "price_per_hour": 380000, "price_from_display": "₹3.8L / hr",
        "image": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=900&q=80",
        "cabin_features": ["Flat-floor cabin", "Belted lavatory", "Ethernet + Wi-Fi", "Full galley"],
        "ideal_for": ["India–Middle East", "India–Europe short", "Extended missions"],
        "is_popular": False,
    },
    {
        "slug": "learjet-75", "category": "midsize-jet", "category_label": "Midsize Jet",
        "name": "Learjet 75 Liberty", "tagline": "Iconic speed and agility in its class",
        "passengers": 8, "range_km": 3779, "range_nm": 2040, "speed_kmh": 861,
        "ceiling_ft": 51000, "baggage_kg": 249,
        "price_per_hour": 310000, "price_from_display": "₹3.1L / hr",
        "image": "https://images.unsplash.com/photo-1530521954074-e64f6810b32d?w=900&q=80",
        "cabin_features": ["6 + 2 seating", "High-speed internet", "Dual-zone climate", "Sky-high ceiling"],
        "ideal_for": ["Fast regional travel", "Executive transport", "Sports team movement"],
        "is_popular": False,
    },
    # Heavy Jets
    {
        "slug": "gulfstream-g450", "category": "heavy-jet", "category_label": "Heavy Jet",
        "name": "Gulfstream G450", "tagline": "Long-range capability with first-class comfort",
        "passengers": 14, "range_km": 7778, "range_nm": 4200, "speed_kmh": 942,
        "ceiling_ft": 45000, "baggage_kg": 680,
        "price_per_hour": 600000, "price_from_display": "₹6L / hr",
        "image": "https://images.unsplash.com/photo-1570710891163-6d3b5c47248b?w=900&q=80",
        "cabin_features": ["3-zone cabin", "Lie-flat beds", "Conference table", "Dual-zone galley", "Satellite phone"],
        "ideal_for": ["India–Europe", "India–North America", "VVIP travel"],
        "is_popular": True,
    },
    {
        "slug": "bombardier-challenger-604", "category": "heavy-jet", "category_label": "Heavy Jet",
        "name": "Bombardier Challenger 604", "tagline": "Canada's flagship wide-body business jet",
        "passengers": 12, "range_km": 7408, "range_nm": 4000, "speed_kmh": 882,
        "ceiling_ft": 41000, "baggage_kg": 1650,
        "price_per_hour": 550000, "price_from_display": "₹5.5L / hr",
        "image": "https://images.unsplash.com/photo-1585893153434-b1e9ff59e87b?w=900&q=80",
        "cabin_features": ["Wide-body cabin", "Refreshment centre", "Enclosed lavatory", "High-speed internet"],
        "ideal_for": ["Long international", "Large groups", "Cargo transport"],
        "is_popular": False,
    },
    {
        "slug": "gulfstream-g650", "category": "heavy-jet", "category_label": "Heavy Jet",
        "name": "Gulfstream G650ER", "tagline": "The pinnacle of large-cabin business aviation",
        "passengers": 19, "range_km": 12964, "range_nm": 7000, "speed_kmh": 956,
        "ceiling_ft": 51000, "baggage_kg": 1770,
        "price_per_hour": 900000, "price_from_display": "₹9L / hr",
        "image": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=900&q=80",
        "cabin_features": ["4-zone cabin", "Lie-flat beds × 10", "Full galley + chef option", "18 Oval Windows", "Bose sound"],
        "ideal_for": ["VVIP", "Around the world", "Head of state travel"],
        "is_popular": False,
    },
    # Ultra Long Range
    {
        "slug": "bombardier-global-7500", "category": "ulr", "category_label": "Ultra Long Range",
        "name": "Bombardier Global 7500", "tagline": "The world's largest and longest-range purpose-built business jet",
        "passengers": 14, "range_km": 14260, "range_nm": 7700, "speed_kmh": 956,
        "ceiling_ft": 51000, "baggage_kg": 1950,
        "price_per_hour": 1800000, "price_from_display": "₹18L / hr",
        "image": "https://images.unsplash.com/photo-1556388158-158ea5ccacbd?w=900&q=80",
        "cabin_features": ["4 living spaces", "Full bedroom", "Full galley", "Walk-in wardrobe"],
        "ideal_for": ["Non-stop ultra-long-haul", "Heads of state", "Celebrity travel"],
        "is_popular": False,
    },
    {
        "slug": "gulfstream-g700", "category": "ulr", "category_label": "Ultra Long Range",
        "name": "Gulfstream G700", "tagline": "Gulfstream's largest, most capable aircraft",
        "passengers": 19, "range_km": 13890, "range_nm": 7500, "speed_kmh": 956,
        "ceiling_ft": 51000, "baggage_kg": 2000,
        "price_per_hour": 2200000, "price_from_display": "₹22L / hr",
        "image": "https://images.unsplash.com/photo-1585893153434-b1e9ff59e87b?w=900&q=80",
        "cabin_features": ["5 living areas", "Ultra-galley", "Master stateroom", "Shower"],
        "ideal_for": ["Ultra VIP", "Long-haul non-stop", "Presidential travel"],
        "is_popular": False,
    },
    # Helicopters
    {
        "slug": "bell-430", "category": "helicopter", "category_label": "Helicopter",
        "name": "Bell 430", "tagline": "The city-hopper with executive comfort",
        "passengers": 7, "range_km": 651, "range_nm": 351, "speed_kmh": 260,
        "ceiling_ft": 20000, "baggage_kg": 155,
        "price_per_hour": 110000, "price_from_display": "₹1.1L / hr",
        "image": "https://images.unsplash.com/photo-1530521954074-e64f6810b32d?w=900&q=80",
        "cabin_features": ["VIP leather interior", "Air conditioning", "Low vibration", "Glass cockpit"],
        "ideal_for": ["City hops", "Joy rides", "Election flying"],
        "is_popular": True,
    },
    {
        "slug": "airbus-h145", "category": "helicopter", "category_label": "Helicopter",
        "name": "Airbus H145", "tagline": "Twin-engine safety for every mission",
        "passengers": 9, "range_km": 670, "range_nm": 362, "speed_kmh": 268,
        "ceiling_ft": 20000, "baggage_kg": 180,
        "price_per_hour": 140000, "price_from_display": "₹1.4L / hr",
        "image": "https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?w=900&q=80",
        "cabin_features": ["Medical config available", "Hoist-ready", "Night vision capable", "Bearingless rotor"],
        "ideal_for": ["Air ambulance", "Offshore ops", "VIP transfer"],
        "is_popular": False,
    },
    {
        "slug": "sikorsky-s76", "category": "helicopter", "category_label": "Helicopter",
        "name": "Sikorsky S-76D", "tagline": "The benchmark VIP helicopter worldwide",
        "passengers": 12, "range_km": 833, "range_nm": 450, "speed_kmh": 287,
        "ceiling_ft": 13800, "baggage_kg": 235,
        "price_per_hour": 180000, "price_from_display": "₹1.8L / hr",
        "image": "https://images.unsplash.com/photo-1540962351504-03099e0a754b?w=900&q=80",
        "cabin_features": ["VIP leather", "Noise-cancelling headsets", "Climate control", "Infotainment"],
        "ideal_for": ["Executive transfer", "Election campaigns", "Medical emergency"],
        "is_popular": False,
    },
]

# ── Airport Distances (India key routes + international) ──────────────────────
DISTANCES = [
    # Domestic
    {"from_code": "DEL", "to_code": "BOM", "from_city": "Delhi",     "to_city": "Mumbai",    "distance_km": 1148, "is_international": False},
    {"from_code": "BOM", "to_code": "DEL", "from_city": "Mumbai",    "to_city": "Delhi",     "distance_km": 1148, "is_international": False},
    {"from_code": "DEL", "to_code": "BLR", "from_city": "Delhi",     "to_city": "Bengaluru", "distance_km": 1740, "is_international": False},
    {"from_code": "BLR", "to_code": "DEL", "from_city": "Bengaluru", "to_city": "Delhi",     "distance_km": 1740, "is_international": False},
    {"from_code": "BOM", "to_code": "BLR", "from_city": "Mumbai",    "to_city": "Bengaluru", "distance_km": 843,  "is_international": False},
    {"from_code": "BLR", "to_code": "BOM", "from_city": "Bengaluru", "to_city": "Mumbai",    "distance_km": 843,  "is_international": False},
    {"from_code": "DEL", "to_code": "MAA", "from_city": "Delhi",     "to_city": "Chennai",   "distance_km": 1754, "is_international": False},
    {"from_code": "MAA", "to_code": "DEL", "from_city": "Chennai",   "to_city": "Delhi",     "distance_km": 1754, "is_international": False},
    {"from_code": "DEL", "to_code": "HYD", "from_city": "Delhi",     "to_city": "Hyderabad", "distance_km": 1267, "is_international": False},
    {"from_code": "HYD", "to_code": "DEL", "from_city": "Hyderabad", "to_city": "Delhi",     "distance_km": 1267, "is_international": False},
    {"from_code": "BOM", "to_code": "GOI", "from_city": "Mumbai",    "to_city": "Goa",       "distance_km": 450,  "is_international": False},
    {"from_code": "GOI", "to_code": "BOM", "from_city": "Goa",       "to_city": "Mumbai",    "distance_km": 450,  "is_international": False},
    {"from_code": "DEL", "to_code": "JAI", "from_city": "Delhi",     "to_city": "Jaipur",    "distance_km": 261,  "is_international": False},
    {"from_code": "DEL", "to_code": "LKO", "from_city": "Delhi",     "to_city": "Lucknow",   "distance_km": 504,  "is_international": False},
    {"from_code": "DEL", "to_code": "AMD", "from_city": "Delhi",     "to_city": "Ahmedabad", "distance_km": 897,  "is_international": False},
    {"from_code": "DEL", "to_code": "CCU", "from_city": "Delhi",     "to_city": "Kolkata",   "distance_km": 1303, "is_international": False},
    {"from_code": "BOM", "to_code": "MAA", "from_city": "Mumbai",    "to_city": "Chennai",   "distance_km": 1031, "is_international": False},
    {"from_code": "DEL", "to_code": "PAT", "from_city": "Delhi",     "to_city": "Patna",     "distance_km": 998,  "is_international": False},
    # International
    {"from_code": "DEL", "to_code": "DXB", "from_city": "Delhi",     "to_city": "Dubai",     "distance_km": 2192, "is_international": True},
    {"from_code": "BOM", "to_code": "DXB", "from_city": "Mumbai",    "to_city": "Dubai",     "distance_km": 1934, "is_international": True},
    {"from_code": "DEL", "to_code": "LHR", "from_city": "Delhi",     "to_city": "London",    "distance_km": 6730, "is_international": True},
    {"from_code": "DEL", "to_code": "SIN", "from_city": "Delhi",     "to_city": "Singapore", "distance_km": 4150, "is_international": True},
    {"from_code": "BOM", "to_code": "SIN", "from_city": "Mumbai",    "to_city": "Singapore", "distance_km": 3916, "is_international": True},
    {"from_code": "DEL", "to_code": "BKK", "from_city": "Delhi",     "to_city": "Bangkok",   "distance_km": 2983, "is_international": True},
    {"from_code": "DEL", "to_code": "CDG", "from_city": "Delhi",     "to_city": "Paris",     "distance_km": 6598, "is_international": True},
    {"from_code": "DEL", "to_code": "JFK", "from_city": "Delhi",     "to_city": "New York",  "distance_km": 11749,"is_international": True},
    {"from_code": "BOM", "to_code": "AUH", "from_city": "Mumbai",    "to_city": "Abu Dhabi", "distance_km": 1858, "is_international": True},
    {"from_code": "BOM", "to_code": "LHR", "from_city": "Mumbai",    "to_city": "London",    "distance_km": 7186, "is_international": True},
    {"from_code": "DEL", "to_code": "KUL", "from_city": "Delhi",     "to_city": "Kuala Lumpur","distance_km": 4240,"is_international": True},
]

# ── Membership Plans ──────────────────────────────────────────────────────────
MEMBERSHIP_PLANS = [
    {
        "tier": MembershipTier.silver,
        "tagline": "Your first class in private aviation",
        "annual_fee": 25000000,           # ₹2,50,000 in paise
        "annual_fee_display": "₹2,50,000",
        "flight_credit": 20000000,        # ₹2,00,000 in paise
        "flight_credit_display": "₹2,00,000",
        "discount_pct": 5,
        "color": "#9CA3AF",
        "is_popular": False,
        "features": [
            "Priority booking — 24-hour advance access",
            "Dedicated account manager",
            "Digital Oneness membership card",
            "5% discount on all charter bookings",
            "Flight credit: ₹2,00,000 per year",
            "Complimentary inflight catering (up to 4 pax)",
            "Access to 60+ aircraft across India",
            "Quarterly aviation briefing newsletter",
        ],
        "not_included": [
            "International route discounts",
            "Lounge access at private terminals",
            "Companion upgrade vouchers",
        ],
    },
    {
        "tier": MembershipTier.gold,
        "tagline": "For the frequent flyer who values time",
        "annual_fee": 50000000,           # ₹5,00,000 in paise
        "annual_fee_display": "₹5,00,000",
        "flight_credit": 45000000,        # ₹4,50,000 in paise
        "flight_credit_display": "₹4,50,000",
        "discount_pct": 10,
        "color": "#C9A84C",
        "is_popular": True,
        "features": [
            "Priority booking — 12-hour advance access",
            "Dedicated senior account manager",
            "Physical embossed Gold membership card",
            "10% discount on all charter bookings",
            "Flight credit: ₹4,50,000 per year",
            "Complimentary premium catering (any pax count)",
            "Access to full fleet including heavy jets",
            "5% discount on international routes",
            "FBO lounge access at Delhi & Mumbai",
            "2 companion upgrade vouchers per year",
            "Monthly aviation market report",
        ],
        "not_included": [
            "Global lounge network",
            "Unlimited companion vouchers",
        ],
    },
    {
        "tier": MembershipTier.platinum,
        "tagline": "Unlimited access. Zero compromises.",
        "annual_fee": 120000000,          # ₹12,00,000 in paise
        "annual_fee_display": "₹12,00,000",
        "flight_credit": 120000000,       # ₹12,00,000 in paise
        "flight_credit_display": "₹12,00,000",
        "discount_pct": 15,
        "color": "#E2C97E",
        "is_popular": False,
        "features": [
            "Priority booking — instant availability",
            "Exclusive concierge — WhatsApp & phone 24/7",
            "Metal Platinum membership card (couriered)",
            "15% discount on all charter bookings",
            "Flight credit: ₹12,00,000 per year",
            "Unlimited premium catering on every flight",
            "Entire global fleet access including VVIP aircraft",
            "10% discount on international routes",
            "Global FBO lounge access (35+ airports)",
            "Unlimited companion upgrade vouchers",
            "Custom cabin configuration on request",
            "Annual aviation portfolio review with MD",
            "Priority medical evacuation coordination",
        ],
        "not_included": [],
    },
]

# ── FAQs ─────────────────────────────────────────────────────────────────────
FAQS = [
    {"question": "How do I book a private charter flight?", "answer": "Simply fill out our charter enquiry form on the website or call us directly. Our team will respond within 2 hours with aircraft options and pricing.", "category": "Booking Process", "sort_order": 1},
    {"question": "How much does a private charter cost?", "answer": "Charter prices depend on the route, aircraft type, and dates. Use our Flight Cost Estimator for an instant estimate, or contact us for a detailed quote.", "category": "Flight Pricing", "sort_order": 2},
    {"question": "What is your cancellation policy?", "answer": "Cancellations made 48+ hours before departure receive a full refund. Within 48 hours, a 25% cancellation fee applies. Within 12 hours, 50% of the charter fee is charged.", "category": "Cancellation Policy", "sort_order": 3},
    {"question": "What documents do I need for a charter flight?", "answer": "For domestic flights: government-issued photo ID. For international: valid passport and visa for destination country. Our team will advise on any specific requirements.", "category": "Documents Required", "sort_order": 4},
    {"question": "What payment methods do you accept?", "answer": "We accept all major credit/debit cards, UPI, net banking, and bank wire transfers via Razorpay. Corporate clients can arrange invoiced billing.", "category": "Payment Methods", "sort_order": 5},
    {"question": "How safe are your charter flights?", "answer": "All our aircraft are DGCA-certified and maintained to international standards. We operate under a valid Air Operator Certificate (AOC) and all crew are licensed by DGCA.", "category": "Safety Standards", "sort_order": 6},
    {"question": "Can I arrange special catering or inflight services?", "answer": "Absolutely. We offer customised catering from standard refreshments to full fine-dining menus. Special dietary requirements, floral arrangements, and entertainment can all be arranged in advance.", "category": "Booking Process", "sort_order": 7},
    {"question": "What is the minimum notice required to book a charter?", "answer": "Standard charters require 24–48 hours notice. We can often accommodate same-day requests for aircraft based at major hubs. Emergency and medical flights are available on immediate notice.", "category": "Booking Process", "sort_order": 8},
    {"question": "Do you offer empty leg flights?", "answer": "Yes. Empty leg flights are significantly discounted repositioning flights. Check our website or call us for current availability.", "category": "Flight Pricing", "sort_order": 9},
    {"question": "Can I bring pets on board?", "answer": "Yes, most aircraft can accommodate pets with advance notice. Specific requirements vary by aircraft type. Please mention this when making your booking.", "category": "Booking Process", "sort_order": 10},
]

# ── Testimonials ─────────────────────────────────────────────────────────────
TESTIMONIALS = [
    {
        "name": "Vikram Singhania", "role": "Managing Director", "company": "Singhania Group",
        "quote": "I fly Delhi–Mumbai twice a week. The Platinum membership pays for itself in the first month. My account manager knows my preferences — she books before I even ask.",
        "rating": 5, "plan": "Platinum Member", "initials": "VS", "sort_order": 1,
    },
    {
        "name": "Ananya Kapoor", "role": "Founder", "company": "Luxe Events Co.",
        "quote": "For corporate events and wedding charters, the Gold membership is non-negotiable. The 10% discount and dedicated manager make every event seamless from the air down.",
        "rating": 5, "plan": "Gold Member", "initials": "AK", "sort_order": 2,
    },
    {
        "name": "Dr. Suresh Pillai", "role": "Senior Cardiologist", "company": "Apollo Group",
        "quote": "Medical emergencies don't wait for availability. The Silver membership guarantees I can charter a medical flight within hours — that peace of mind is invaluable.",
        "rating": 5, "plan": "Silver Member", "initials": "SP", "sort_order": 3,
    },
    {
        "name": "Priya Mehta", "role": "COO", "company": "TechVista India",
        "quote": "Last-minute board meeting in Singapore — Oneness had a heavy jet confirmed in under 90 minutes. That level of service is simply not possible with commercial airlines.",
        "rating": 5, "plan": "Gold Member", "initials": "PM", "sort_order": 4,
    },
    {
        "name": "Rajat Sharma", "role": "Film Producer", "company": "RS Productions",
        "quote": "We've used Oneness for 6 film shooting charters across Rajasthan and the Andamans. Flawless every time — the crew understands creative timelines.",
        "rating": 5, "plan": None, "initials": "RS", "sort_order": 5,
    },
    {
        "name": "Kavitha Reddy", "role": "Managing Partner", "company": "Reddy & Associates Law",
        "quote": "The discretion and privacy Oneness provides is unmatched. Our client travel details have never once been compromised. That trust is everything in our business.",
        "rating": 5, "plan": "Platinum Member", "initials": "KR", "sort_order": 6,
    },
]


async def seed():
    async with AsyncSessionLocal() as db:
        print("🌱 Starting database seed...")

        # ── Admin user ──────────────────────────────────────────────────────
        existing_admin = await db.execute(select(User).where(User.email == "admin@onenessaviation.com"))
        if not existing_admin.scalar_one_or_none():
            admin = User(
                name="Oneness Admin",
                email="admin@onenessaviation.com",
                phone="+91 99999 99999",
                hashed_password=hash_password("Admin@Oneness2024!"),
                role=UserRole.admin,
                is_verified=True,
            )
            db.add(admin)
            print("  ✓ Admin user created (admin@onenessaviation.com / Admin@Oneness2024!)")
        else:
            print("  · Admin user already exists")

        # ── Aircraft categories ─────────────────────────────────────────────
        for cat_data in CATEGORIES:
            existing = await db.execute(select(AircraftCategory).where(AircraftCategory.slug == cat_data["slug"]))
            if not existing.scalar_one_or_none():
                db.add(AircraftCategory(**cat_data))
        print(f"  ✓ {len(CATEGORIES)} aircraft categories seeded")

        # ── Aircraft ────────────────────────────────────────────────────────
        count = 0
        for ac_data in AIRCRAFT:
            existing = await db.execute(select(Aircraft).where(Aircraft.slug == ac_data["slug"]))
            if not existing.scalar_one_or_none():
                db.add(Aircraft(**ac_data))
                count += 1
        print(f"  ✓ {count} aircraft seeded")

        # ── Airport distances ───────────────────────────────────────────────
        count = 0
        for dist in DISTANCES:
            existing = await db.execute(
                select(AirportDistance).where(
                    AirportDistance.from_code == dist["from_code"],
                    AirportDistance.to_code == dist["to_code"],
                )
            )
            if not existing.scalar_one_or_none():
                db.add(AirportDistance(**dist))
                count += 1
        print(f"  ✓ {count} airport routes seeded")

        # ── Membership plans ────────────────────────────────────────────────
        for plan_data in MEMBERSHIP_PLANS:
            existing = await db.execute(select(MembershipPlan).where(MembershipPlan.tier == plan_data["tier"]))
            if not existing.scalar_one_or_none():
                db.add(MembershipPlan(**plan_data))
        print(f"  ✓ {len(MEMBERSHIP_PLANS)} membership plans seeded")

        # ── FAQs ────────────────────────────────────────────────────────────
        count = 0
        for faq_data in FAQS:
            existing = await db.execute(select(FAQ).where(FAQ.question == faq_data["question"]))
            if not existing.scalar_one_or_none():
                db.add(FAQ(**faq_data))
                count += 1
        print(f"  ✓ {count} FAQs seeded")

        # ── Testimonials ────────────────────────────────────────────────────
        count = 0
        for t_data in TESTIMONIALS:
            existing = await db.execute(select(Testimonial).where(Testimonial.name == t_data["name"]))
            if not existing.scalar_one_or_none():
                db.add(Testimonial(**t_data))
                count += 1
        print(f"  ✓ {count} testimonials seeded")

        await db.commit()
        print("\n✅ Seed complete! You can now start the server with: uvicorn app.main:app --reload")
        print("\n📋 Admin credentials:")
        print("   Email   : admin@onenessaviation.com")
        print("   Password: Admin@Oneness2024!")
        print("   ⚠️  Change the admin password immediately after first login!\n")


if __name__ == "__main__":
    asyncio.run(seed())
