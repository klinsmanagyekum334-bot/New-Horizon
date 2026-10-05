import os
import uuid
from functools import wraps
from dotenv import load_dotenv
from supabase import create_client, Client
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort, jsonify
)

load_dotenv()

# ============================================================
# CONFIG
# ============================================================
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://soeenrjxrspfsexdiuip.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_mYvFcs9_OSA0PTIbcj4djg_NHGB8DXC")

SECRET_KEY     = os.environ.get("SECRET_KEY", "newhorizon-secret-2026-klinsman")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Klinsman@ophyser1")

# Secondary admin password (kept from original)
ADMIN_PASSWORD_SECONDARY = os.environ.get("ADMIN_PASSWORD_SECONDARY", "horizon6202")
ADMIN_PASSWORDS = [ADMIN_PASSWORD] + ([ADMIN_PASSWORD_SECONDARY] if ADMIN_PASSWORD_SECONDARY else [])

WHATSAPP_NUMBER = "233243444343"
PHONE_NUMBER    = "+233243444343"
PHONE_DISPLAY   = "+233 24 344 4343"
EMAIL_ADDRESS   = "info@newhorizongh.com"
ADDRESS         = "Tema Community 25, Ghana"

MAX_VIDEOS      = 10
MAX_VIDEO_BYTES = 20 * 1024 * 1024
MAX_IMAGE_BYTES = 5  * 1024 * 1024

BUCKET_IMAGES  = "nh-images"
BUCKET_GALLERY = "nh-gallery"
BUCKET_VIDEOS  = "nh-videos"

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

app.config["SESSION_COOKIE_SECURE"]   = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1, x_proto=1, x_host=1, x_prefix=1
)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================
# SITE SCHEMA (Restored Full Schema from original)
# ============================================================
SITE_SCHEMA = [
    {
        "section": "Branding",
        "icon": "fa-solid fa-tag",
        "fields": [
            {"key": "brand_name",    "label": "Brand Name (full)",           "type": "text",  "default": "New Horizon Coopers Limited"},
            {"key": "brand_new",     "label": "Logo Word 1 (NEW)",           "type": "text",  "default": "NEW"},
            {"key": "brand_horizon", "label": "Logo Word 2 (HORIZON)",       "type": "text",  "default": "HORIZON"},
            {"key": "brand_coopers", "label": "Coopers Limited line",        "type": "text",  "default": "Coopers Limited"},
            {"key": "brand_tagline", "label": "Tagline (below logo)",        "type": "text",  "default": "Real Estate & Pharmaceutical Agency"},
            {"key": "logo_path",     "label": "Site Logo",                   "type": "image", "default": ""},
        ],
    },
    {
        "section": "Header",
        "icon": "fa-solid fa-bars",
        "fields": [
            {"key": "header_cta_text",  "label": "Header Button Text",      "type": "text", "default": "Book Consultation"},
            {"key": "header_search_ph", "label": "Search box placeholder",  "type": "text", "default": "Search properties, products, pages…"},
            {"key": "mobile_cta_text",  "label": "Mobile Menu Button Text", "type": "text", "default": "Book a Consultation"},
        ],
    },
    {
        "section": "Search Drawer",
        "icon": "fa-solid fa-magnifying-glass",
        "fields": [
            {"key": "search_eyebrow",    "label": "Small label above input", "type": "text", "default": "Search the site"},
            {"key": "search_hint",       "label": "Hint text (empty state)", "type": "text", "default": "Start typing to search pages, projects, and products."},
            {"key": "search_loading",    "label": "Loading message",         "type": "text", "default": "Searching…"},
            {"key": "search_no_results", "label": "No results message",      "type": "text", "default": "No results found."},
            {"key": "search_unavailable","label": "Unavailable message",     "type": "text", "default": "Search unavailable."},
        ],
    },
    {
        "section": "Hero Section",
        "icon": "fa-solid fa-house-chimney",
        "fields": [
            {"key": "hero_eyebrow",  "label": "Hero Eyebrow (pill above title)", "type": "text",  "default": "About New Horizon"},
            {"key": "hero_title",    "label": "Hero Title (first part)",         "type": "text",  "default": "New Horizon is a company which deals with"},
            {"key": "hero_title_em", "label": "Hero Title (italic accent)",      "type": "text",  "default": "Real Estate & Pharmaceutical products."},
            {"key": "hero_subtitle", "label": "Hero Subtitle",                   "type": "text",  "default": "Most trusted Agency in Ghana"},
            {"key": "hero_image",    "label": "Hero Background Image",           "type": "image", "default": ""},

            {"key": "hero_meta_1_key", "label": "Info Card · Row 1 · Left",  "type": "text", "default": "24/7"},
            {"key": "hero_meta_1_val", "label": "Info Card · Row 1 · Right", "type": "text", "default": "Client Support"},
            {"key": "hero_meta_2_key", "label": "Info Card · Row 2 · Left",  "type": "text", "default": "FDA"},
            {"key": "hero_meta_2_val", "label": "Info Card · Row 2 · Right", "type": "text", "default": "Ghana Licensed"},
            {"key": "hero_meta_3_key", "label": "Info Card · Row 3 · Left",  "type": "text", "default": "16"},
            {"key": "hero_meta_3_val", "label": "Info Card · Row 3 · Right", "type": "text", "default": "Regions Covered"},
            {"key": "hero_meta_4_key", "label": "Info Card · Row 4 · Left",  "type": "text", "default": "Est."},
            {"key": "hero_meta_4_val", "label": "Info Card · Row 4 · Right", "type": "text", "default": "2017 · Tema"},

            {"key": "hero_pill_1_small", "label": "Pill 1 · Small text", "type": "text", "default": "Division 01"},
            {"key": "hero_pill_1_main",  "label": "Pill 1 · Main text",  "type": "text", "default": "Real Estate"},

            {"key": "hero_pill_2_small", "label": "Pill 2 · Small text", "type": "text", "default": "Division 02"},
            {"key": "hero_pill_2_main",  "label": "Pill 2 · Main text",  "type": "text", "default": "Pharmaceuticals"},

            {"key": "hero_pill_3_small", "label": "Pill 3 · Small text", "type": "text", "default": "Explore"},
            {"key": "hero_pill_3_main",  "label": "Pill 3 · Main text",  "type": "text", "default": "All Projects"},

            {"key": "hero_pill_4_small", "label": "Pill 4 · Small text", "type": "text", "default": "See"},
            {"key": "hero_pill_4_main",  "label": "Pill 4 · Main text",  "type": "text", "default": "Gallery"},

            {"key": "hero_pill_cta",     "label": "Pill 5 · CTA text",   "type": "text", "default": "About New Horizon"},
        ],
    },
    {
        "section": "Services Strip",
        "icon": "fa-solid fa-list-check",
        "fields": [
            {"key": "services_heading", "label": "Services Heading", "type": "text", "default": "[ Our Services ]"},
            {"key": "services_items",   "label": "Services List (one per line)", "type": "textarea",
             "default": "Estate Development\nArchitectural Designs\nBuilding & Construction\nHouse Sales\nBuilding Plans\nand all Your Building Solutions"},
        ],
    },
    {
        "section": "Video Section",
        "icon": "fa-solid fa-video",
        "fields": [
            {"key": "video_section_heading",    "label": "Video Heading",    "type": "text", "default": "Watch Our Story"},
            {"key": "video_section_subheading", "label": "Video Subheading", "type": "text", "default": "See our developments come to life."},
        ],
    },
    {
        "section": "Estates Section",
        "icon": "fa-solid fa-house-chimney-window",
        "fields": [
            {"key": "estates_title",    "label": "Estates Title (dark part)",   "type": "text", "default": "NEW HORIZON"},
            {"key": "estates_title_em", "label": "Estates Title (italic part)", "type": "text", "default": "REAL ESTATES"},
            {"key": "estates_sub",      "label": "Estates Subtext",             "type": "text", "default": "We have the following"},
            {"key": "estates_chip_all",         "label": "Chip · All",                     "type": "text", "default": "All"},
            {"key": "estates_chip_commercial",  "label": "Chip · Commercial",              "type": "text", "default": "Commercial"},
            {"key": "estates_chip_residential", "label": "Chip · Residential",             "type": "text", "default": "Residential"},
            {"key": "estates_chip_gallery",     "label": "Chip · Gallery",                 "type": "text", "default": "Gallery"},
            {"key": "estates_chip_estates",     "label": "Chip · Estates",                 "type": "text", "default": "Estates"},
            {"key": "estates_chip_build",       "label": "Chip · Building & Construction", "type": "text", "default": "Building & Construction"},
            {"key": "estates_cta",      "label": "See-all button text",         "type": "text", "default": "See all properties"},
        ],
    },
    {
        "section": "Pharma Section",
        "icon": "fa-solid fa-prescription-bottle-medical",
        "fields": [
            {"key": "pharma_title",    "label": "Pharma Title (dark part)",   "type": "text", "default": "NEW HORIZON"},
            {"key": "pharma_title_em", "label": "Pharma Title (italic part)", "type": "text", "default": "PHARMACEUTICALS"},
            {"key": "pharma_sub",      "label": "Pharma Subtext",             "type": "text", "default": "We stock the following"},
            {"key": "pharma_chip_all",      "label": "Chip · All",              "type": "text", "default": "All"},
            {"key": "pharma_chip_otc",      "label": "Chip · Over the Counter", "type": "text", "default": "Over the Counter"},
            {"key": "pharma_chip_herbal",   "label": "Chip · Herbal Products",  "type": "text", "default": "Herbal Products"},
            {"key": "pharma_chip_rx",       "label": "Chip · Prescription",     "type": "text", "default": "Prescription"},
            {"key": "pharma_chip_wellness", "label": "Chip · Wellness",         "type": "text", "default": "Wellness"},
            {"key": "pharma_chip_devices",  "label": "Chip · Medical Devices",  "type": "text", "default": "Medical Devices"},
            {"key": "pharma_cta",      "label": "Pharma button text",         "type": "text", "default": "Request full catalogue"},
        ],
    },
    {
        "section": "CTA Band",
        "icon": "fa-solid fa-bullhorn",
        "fields": [
            {"key": "cta_eyebrow",       "label": "CTA Eyebrow",            "type": "text", "default": "Let's talk"},
            {"key": "cta_title",         "label": "CTA Title (line 1)",     "type": "text", "default": "Ready to find your"},
            {"key": "cta_title_em",      "label": "CTA Title (italic line)", "type": "text", "default": "next address?"},
            {"key": "cta_sub",           "label": "CTA Subtext",            "type": "text", "default": "Whether you're buying a home, supplying a pharmacy, or exploring a partnership — our team is one call away."},
            {"key": "cta_btn_primary",   "label": "Primary button text",    "type": "text", "default": "Book a consultation"},
            {"key": "cta_btn_secondary", "label": "Secondary button text",  "type": "text", "default": "Contact us"},
        ],
    },
    {
        "section": "Contact & Location",
        "icon": "fa-solid fa-address-book",
        "fields": [
            {"key": "contact_email",         "label": "Email Address",              "type": "text", "default": EMAIL_ADDRESS},
            {"key": "contact_phone_display", "label": "Phone (displayed)",          "type": "text", "default": PHONE_DISPLAY},
            {"key": "contact_whatsapp_num",  "label": "WhatsApp (no +, no spaces)", "type": "text", "default": WHATSAPP_NUMBER},
            {"key": "contact_heading",       "label": "Contact Section Heading",    "type": "text", "default": "Contact Us"},
            {"key": "contact_subheading",    "label": "Contact Section Subheading", "type": "text", "default": "We're here to help — reach out anytime."},
            {"key": "location_heading",      "label": "Location Heading",           "type": "text", "default": "Our Location"},
            {"key": "location_address",      "label": "Location Address",           "type": "text", "default": ADDRESS},
            {"key": "location_maps_url",     "label": "Google Maps Link",           "type": "text", "default": "https://www.google.com/maps/search/?api=1&query=Tema+Community+25+Ghana"},
        ],
    },
    {
        "section": "Footer",
        "icon": "fa-solid fa-shoe-prints",
        "fields": [
            {"key": "footer_blurb",          "label": "Footer Blurb",                   "type": "textarea",
             "default": "New Horizon Coopers Limited — building sustainable, modern communities across Ghana since 2017."},
            {"key": "footer_suffix",         "label": "Below logo — small suffix line", "type": "text", "default": "Coopers Limited · Est. 2017"},

            {"key": "footer_col_company",    "label": "Column 1 heading",               "type": "text", "default": "Company"},
            {"key": "footer_link_about",     "label": "Column 1 · Link 1",              "type": "text", "default": "About"},
            {"key": "footer_link_projects",  "label": "Column 1 · Link 2",              "type": "text", "default": "Projects"},
            {"key": "footer_link_gallery",   "label": "Column 1 · Link 3",              "type": "text", "default": "Gallery"},
            {"key": "footer_link_contact",   "label": "Column 1 · Link 4",              "type": "text", "default": "Contact"},

            {"key": "footer_col_divisions",  "label": "Column 2 heading",               "type": "text", "default": "Divisions"},
            {"key": "footer_link_realestate","label": "Column 2 · Link 1",              "type": "text", "default": "Real Estate"},
            {"key": "footer_link_pharma",    "label": "Column 2 · Link 2",              "type": "text", "default": "Pharmaceuticals"},

            {"key": "footer_col_contact",    "label": "Column 3 heading",               "type": "text", "default": "Contact"},

            {"key": "footer_copyright",      "label": "Bottom bar — copyright",         "type": "text", "default": "© 2026 New Horizon Coopers Limited"},
        ],
    },
]


def get_schema_defaults():
    out = {}
    for sec in SITE_SCHEMA:
        for f in sec["fields"]:
            out[f["key"]] = f["default"]
    return out


# ============================================================
# INIT — seed tables (Supabase)
# ============================================================
def seed_if_empty(table, rows):
    try:
        res = supabase.table(table).select("id").limit(1).execute()
        if res.data:
            return
        supabase.table(table).insert(rows).execute()
        print(f"[INIT] Seeded {table} with {len(rows)} rows")
    except Exception as e:
        print(f"seed {table} error:", e)


def init_db():
    # site_content
    try:
        res = supabase.table("nh_site_content").select("key").limit(1).execute()
        if not res.data:
            defaults = get_schema_defaults()
            supabase.table("nh_site_content").insert(
                [{"key": k, "value": v} for k, v in defaults.items()]
            ).execute()
            print("[INIT] Seeded nh_site_content")
    except Exception as e:
        print("seed site_content error:", e)

    # nav
    seed_if_empty("nh_nav_links", [
        {"label": "Home",       "url": "/",         "sort_order": 1, "is_locked": True, "visible": True},
        {"label": "About Us",   "url": "/about",    "sort_order": 2, "is_locked": False, "visible": True},
        {"label": "Housing",    "url": "/projects", "sort_order": 3, "is_locked": False, "visible": True},
        {"label": "Gallery",    "url": "/gallery",  "sort_order": 4, "is_locked": False, "visible": True},
        {"label": "Contact Us", "url": "/contact",  "sort_order": 5, "is_locked": False, "visible": True},
    ])

    # property types
    seed_if_empty("nh_property_types", [
        {"label": "Villa",     "sort_order": 1, "is_active": True},
        {"label": "Townhouse", "sort_order": 2, "is_active": True},
        {"label": "Apartment", "sort_order": 3, "is_active": True},
        {"label": "Warehouse", "sort_order": 4, "is_active": True},
    ])

    # drug types
    seed_if_empty("nh_drug_types", [
        {"label": "Pain Killer",       "sort_order": 1, "is_active": True},
        {"label": "Over the Counter",  "sort_order": 2, "is_active": True},
        {"label": "Supplement",        "sort_order": 3, "is_active": True},
        {"label": "Herbal",            "sort_order": 4, "is_active": True},
        {"label": "Prescription",      "sort_order": 5, "is_active": True},
    ])

    # projects
    seed_if_empty("nh_projects", [
        {"slug":"east-legon-villas","name":"East Legon Villas","category":"residential","custom_type":"",
         "status":"ongoing","currency":"USD","short_desc":"2 Bedrooms · 2 Baths · 180 sqm",
         "long_desc":"East Legon Villas is an exclusive collection of modern luxury villas nestled in the heart of Accra.",
         "location":"East Legon, Accra","units":"48 Villas","price_from":420000,
         "image":"https://picsum.photos/seed/eastlegon/600/400",
         "hero_image":"https://picsum.photos/seed/eastlegon/1600/900",
         "video":"","featured":True,"sort_order":1},

        {"slug":"tema-eco-townhomes","name":"Tema Eco Townhomes","category":"residential","custom_type":"",
         "status":"fully-complete","currency":"USD","short_desc":"3 Bedrooms · 2 Baths · 220 sqm",
         "long_desc":"Tema Eco Townhomes offers a new standard of sustainable family living.",
         "location":"Tema, Greater Accra","units":"32 Townhomes","price_from":385000,
         "image":"https://picsum.photos/seed/temaeco/600/400",
         "hero_image":"https://picsum.photos/seed/temaeco/1600/900",
         "video":"","featured":True,"sort_order":2},

        {"slug":"airport-city-lofts","name":"Airport City Lofts","category":"commercial","custom_type":"",
         "status":"partially-complete","currency":"USD","short_desc":"Modern commercial space · 120 sqm",
         "long_desc":"Airport City Lofts is a landmark commercial development near Kotoka International Airport.",
         "location":"Airport City, Accra","units":"12 Units","price_from":220000,
         "image":"https://picsum.photos/seed/airportcity/600/400",
         "hero_image":"https://picsum.photos/seed/airportcity/1600/900",
         "video":"","featured":True,"sort_order":3},

        {"slug":"kumasi-garden-estate","name":"Kumasi Garden Estate","category":"residential","custom_type":"",
         "status":"ongoing","currency":"GHS","short_desc":"4 Bedrooms · 3 Baths · 320 sqm",
         "long_desc":"Kumasi Garden Estate is a master-planned community in Asokwa, Kumasi.",
         "location":"Asokwa, Kumasi","units":"60 Homes","price_from":310000,
         "image":"https://picsum.photos/seed/kumasigarden/600/400",
         "hero_image":"https://picsum.photos/seed/kumasigarden/1600/900",
         "video":"","featured":False,"sort_order":4},

        {"slug":"takoradi-business-park","name":"Takoradi Business Park","category":"commercial","custom_type":"",
         "status":"about-to-start","currency":"GHS","short_desc":"Office & retail space · 90 sqm",
         "long_desc":"Takoradi Business Park is a mixed-use commercial development in Ghana's oil city.",
         "location":"Takoradi, Western Region","units":"24 Units","price_from":195000,
         "image":"https://picsum.photos/seed/takoradipark/600/400",
         "hero_image":"https://picsum.photos/seed/takoradipark/1600/900",
         "video":"","featured":False,"sort_order":5},
    ])

    # drugs
    seed_if_empty("nh_drugs", [
        {"slug":"paracetamol-500mg","name":"Paracetamol 500mg","drug_type":"Pain Killer",
         "price":12,"currency":"GHS",
         "description":"Fast-acting relief for headaches, fever and mild pain. 24 tablets per pack.",
         "image":"https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=800&q=80",
         "video":"","featured":True,"sort_order":1},

        {"slug":"multivitamin-complex","name":"Multivitamin Complex","drug_type":"Supplement",
         "price":85,"currency":"GHS",
         "description":"Complete daily multivitamin with 25 essential vitamins & minerals. 30 capsules.",
         "image":"https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=800&q=80",
         "video":"","featured":True,"sort_order":2},

        {"slug":"herbal-cough-syrup","name":"Herbal Cough Syrup","drug_type":"Herbal",
         "price":45,"currency":"GHS",
         "description":"Natural honey and herbal cough relief. Family-safe. 200ml bottle.",
         "image":"https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=800&q=80",
         "video":"","featured":False,"sort_order":3},

        {"slug":"amoxicillin-250mg","name":"Amoxicillin 250mg","drug_type":"Prescription",
         "price":38,"currency":"GHS",
         "description":"Broad-spectrum antibiotic. Prescription required. 21 capsules.",
         "image":"https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&w=800&q=80",
         "video":"","featured":False,"sort_order":4},

        {"slug":"vitamin-c-1000mg","name":"Vitamin C 1000mg","drug_type":"Supplement",
         "price":55,"currency":"GHS",
         "description":"High-strength immune support. Effervescent tablets. 60 per tube.",
         "image":"https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?auto=format&fit=crop&w=800&q=80",
         "video":"","featured":True,"sort_order":5},
    ])

    # video placeholder
    seed_if_empty("nh_videos", [
        {"title":"New Horizon Showreel",
         "description":"A glimpse into our latest developments across Ghana.",
         "filename":"","is_featured": True,"sort_order":1}
    ])


# ============================================================
# HELPERS
# ============================================================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("update_login"))
        return f(*args, **kwargs)
    return wrapper


def fetch_site():
    defaults = get_schema_defaults()
    try:
        res = supabase.table("nh_site_content").select("key, value").execute()
        for row in (res.data or []):
            defaults[row["key"]] = row["value"]
    except Exception as e:
        print("fetch_site error:", e)
    return defaults


def fetch_nav():
    try:
        res = supabase.table("nh_nav_links").select("*").eq("visible", True) \
            .order("sort_order").order("id").execute()
        return res.data or []
    except Exception as e:
        print("fetch_nav error:", e)
        return []


def fetch_projects(category=None, featured_only=False, custom_type=None):
    try:
        q = supabase.table("nh_projects").select("*")
        if category:
            q = q.eq("category", category)
        if custom_type:
            q = q.ilike("custom_type", custom_type)
        if featured_only:
            q = q.eq("featured", True)
        q = q.order("sort_order").order("id")
        res = q.execute()
        return res.data or []
    except Exception as e:
        print("fetch_projects error:", e)
        return []


def fetch_project(slug):
    try:
        res = supabase.table("nh_projects").select("*").eq("slug", slug).single().execute()
        return res.data
    except Exception:
        return None


def fetch_property_types(only_active=False):
    try:
        q = supabase.table("nh_property_types").select("*")
        if only_active:
            q = q.eq("is_active", True)
        q = q.order("sort_order").order("id")
        res = q.execute()
        return res.data or []
    except Exception as e:
        print("fetch_property_types error:", e)
        return []


def ensure_property_type(label):
    label = (label or "").strip()
    if not label:
        return
    try:
        res = supabase.table("nh_property_types").select("id").ilike("label", label).limit(1).execute()
        if res.data:
            return
        max_res = supabase.table("nh_property_types").select("sort_order").order("sort_order", desc=True).limit(1).execute()
        next_order = (max_res.data[0]["sort_order"] + 1) if max_res.data else 1
        supabase.table("nh_property_types").insert({
            "label": label, "sort_order": next_order, "is_active": True,
        }).execute()
    except Exception as e:
        print("ensure_property_type error:", e)


def fetch_custom_types():
    return [t["label"] for t in fetch_property_types(only_active=True)]


def fetch_drugs(drug_type=None, featured_only=False):
    try:
        q = supabase.table("nh_drugs").select("*")
        if drug_type:
            q = q.ilike("drug_type", drug_type)
        if featured_only:
            q = q.eq("featured", True)
        q = q.order("sort_order").order("id")
        res = q.execute()
        return res.data or []
    except Exception as e:
        print("fetch_drugs error:", e)
        return []


def fetch_drug(drug_id):
    try:
        res = supabase.table("nh_drugs").select("*").eq("id", drug_id).single().execute()
        return res.data
    except Exception:
        return None


def fetch_drug_types(only_active=False):
    try:
        q = supabase.table("nh_drug_types").select("*")
        if only_active:
            q = q.eq("is_active", True)
        q = q.order("sort_order").order("id")
        res = q.execute()
        return res.data or []
    except Exception as e:
        print("fetch_drug_types error:", e)
        return []


def fetch_active_drug_type_labels():
    return [t["label"] for t in fetch_drug_types(only_active=True)]


def ensure_drug_type(label):
    label = (label or "").strip()
    if not label:
        return
    try:
        res = supabase.table("nh_drug_types").select("id").ilike("label", label).limit(1).execute()
        if res.data:
            return
        max_res = supabase.table("nh_drug_types").select("sort_order").order("sort_order", desc=True).limit(1).execute()
        next_order = (max_res.data[0]["sort_order"] + 1) if max_res.data else 1
        supabase.table("nh_drug_types").insert({
            "label": label, "sort_order": next_order, "is_active": True,
        }).execute()
    except Exception as e:
        print("ensure_drug_type error:", e)


def fetch_videos():
    try:
        res = supabase.table("nh_videos").select("*").order("sort_order").order("id").execute()
        return res.data or []
    except Exception as e:
        print("fetch_videos error:", e)
        return []


def fetch_featured_video():
    try:
        res = supabase.table("nh_videos").select("*").eq("is_featured", True) \
            .order("sort_order").limit(1).execute()
        if res.data:
            return res.data[0]
        res = supabase.table("nh_videos").select("*").order("sort_order").limit(1).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print("fetch_featured_video error:", e)
        return None


def fetch_gallery():
    combined = []
    try:
        res = supabase.table("nh_gallery_images").select("*").order("sort_order").order("id").execute()
        for g in (res.data or []):
            combined.append({
                "id":     f"u-{g['id']}",
                "db_id":  g["id"],
                "title":  g.get("title") or "",
                "src":    g["filename"],
                "source": "upload",
            })
    except Exception as e:
        print("fetch_gallery upload error:", e)

    try:
        res = supabase.table("nh_projects").select("id, name, image, sort_order") \
            .not_.is_("image", "null").order("sort_order").order("id").execute()
        for p in (res.data or []):
            if p.get("image"):
                combined.append({
                    "id":     f"p-{p['id']}",
                    "db_id":  None,
                    "title":  p["name"],
                    "src":    p["image"],
                    "source": "project",
                })
    except Exception as e:
        print("fetch_gallery project error:", e)

    return combined


def upload_to_bucket(file_storage, bucket, allowed_exts, max_bytes):
    if not file_storage or not file_storage.filename:
        return None
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed_exts:
        return None
    data = file_storage.read()
    if len(data) > max_bytes:
        return None
    name = f"{uuid.uuid4().hex}.{ext}"
    try:
        supabase.storage.from_(bucket).upload(
            path=name,
            file=data,
            file_options={"content-type": file_storage.mimetype or "application/octet-stream"},
        )
        return supabase.storage.from_(bucket).get_public_url(name)
    except Exception as e:
        print(f"upload to {bucket} error:", e)
        return None


def save_image(file_storage, bucket=BUCKET_IMAGES):
    return upload_to_bucket(
        file_storage, bucket,
        {"png", "jpg", "jpeg", "gif", "webp", "svg"},
        MAX_IMAGE_BYTES,
    )


def save_video(file_storage):
    return upload_to_bucket(
        file_storage, BUCKET_VIDEOS,
        {"mp4", "webm", "mov", "m4v"},
        MAX_VIDEO_BYTES,
    )


def delete_supabase_file(url, bucket):
    if not url or f"/storage/v1/object/public/{bucket}/" not in url:
        return
    try:
        name = url.rsplit("/", 1)[-1]
        supabase.storage.from_(bucket).remove([name])
    except Exception as e:
        print(f"delete supabase file error ({bucket}):", e)


# ============================================================
# GLOBAL TEMPLATE CONTEXT
# ============================================================
@app.context_processor
def inject_globals():
    try:
        return {
            "site":      fetch_site(),
            "nav_links": fetch_nav(),
        }
    except Exception as e:
        print("context_processor error:", e)
        return {
            "site":      {},
            "nav_links": [],
        }


# ============================================================
# SEARCH
# ============================================================
def _normalize(text):
    if text is None:
        return ""
    text = str(text).lower()
    for ch in "-_,./|•·()[]":
        text = text.replace(ch, " ")
    return " ".join(text.split())


def _matches(query, *texts):
    if not query:
        return False
    q = _normalize(query)
    if not q:
        return False
    joined = " ".join(_normalize(t) for t in texts)
    if q in joined:
        return True
    words = [w for w in q.split() if len(w) >= 2]
    if not words:
        return False
    return all(w in joined for w in words)


# ============================================================
# PUBLIC ROUTES
# ============================================================
@app.route("/")
def index():
    all_projects = fetch_projects()
    featured = [p for p in all_projects if p.get("featured")]
    others   = [p for p in all_projects if not p.get("featured")]
    carousel = (featured + others)[:8]
    grid     = all_projects[:10]

    return render_template(
        "index.html",
        carousel_projects=carousel,
        grid_projects=grid,
        featured_video=fetch_featured_video(),
        custom_types=fetch_custom_types(),
        drugs=fetch_drugs()[:8],
        drug_types=fetch_active_drug_type_labels(),
    )


@app.route("/videos")
def videos_page():
    return render_template("videos.html", videos=fetch_videos())


@app.route("/gallery")
def gallery_page():
    return render_template("gallery.html", images=fetch_gallery())


@app.route("/projects")
def projects():
    custom_type = (request.args.get("type") or "").strip()

    if custom_type:
        project_list = fetch_projects(custom_type=custom_type)
        page_heading = custom_type.title()
        page_sub = f"All {custom_type.lower()} properties we have."
    else:
        project_list = fetch_projects()
        page_heading = None
        page_sub = None

    return render_template(
        "projects.html",
        projects=project_list,
        active_category=None,
        active_custom_type=custom_type or None,
        page_heading=page_heading,
        page_sub=page_sub,
        custom_types=fetch_custom_types(),
    )


@app.route("/projects/<slug>")
def project_detail(slug):
    project = fetch_project(slug)
    if not project:
        abort(404)
    return render_template("project_detail.html",
                           project=project,
                           related=fetch_projects(category=project["category"])[:3])


@app.route("/residentials")
def residentials():
    return render_template("projects.html",
                           projects=fetch_projects(category="residential"),
                           active_category="residential",
                           active_custom_type=None,
                           page_heading=None,
                           page_sub=None,
                           custom_types=fetch_custom_types())


@app.route("/commercial")
def commercial():
    return render_template("projects.html",
                           projects=fetch_projects(category="commercial"),
                           active_category="commercial",
                           active_custom_type=None,
                           page_heading=None,
                           page_sub=None,
                           custom_types=fetch_custom_types())


@app.route("/drugs")
def drugs_page():
    drug_type = (request.args.get("type") or "").strip()
    if drug_type:
        drugs = fetch_drugs(drug_type=drug_type)
    else:
        drugs = fetch_drugs()

    return render_template(
        "drugs.html",
        drugs=drugs,
        drug_types=fetch_active_drug_type_labels(),
        active_type=drug_type or None,
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name    = (request.form.get("name") or "").strip()
        email   = (request.form.get("email") or "").strip()
        phone   = (request.form.get("phone") or "").strip()
        subject = (request.form.get("subject") or "").strip()
        message = (request.form.get("message") or "").strip()
        if name and message:
            try:
                supabase.table("nh_inquiries").insert({
                    "kind": "contact", "name": name, "email": email,
                    "phone": phone, "subject": subject, "message": message,
                }).execute()
                flash("Thank you! Your message has been received.", "success")
            except Exception as e:
                print("contact insert error:", e)
                flash("Error sending message.", "error")
        else:
            flash("Please fill in your name and message.", "error")
        return redirect(url_for("contact"))
    return render_template("contact.html")


@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name           = (request.form.get("name") or "").strip()
        email          = (request.form.get("email") or "").strip()
        phone          = (request.form.get("phone") or "").strip()
        preferred_date = (request.form.get("preferred_date") or "").strip()
        message        = (request.form.get("message") or "").strip()
        if name and (email or phone):
            try:
                supabase.table("nh_inquiries").insert({
                    "kind": "booking", "name": name, "email": email,
                    "phone": phone, "message": message,
                    "preferred_date": preferred_date,
                }).execute()
                flash("Booking received!", "success")
            except Exception as e:
                print("book insert error:", e)
                flash("Error saving booking.", "error")
        else:
            flash("Please provide your name and either an email or phone number.", "error")
        return redirect(url_for("book"))
    return render_template("book.html")


# ============================================================
# SEARCH API
# ============================================================
@app.route("/api/search")
def api_search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify([])

    results = []
    site = fetch_site()

    for link in fetch_nav():
        if _matches(q, link["label"], link["url"]):
            results.append({"type": "page", "title": link["label"],
                            "subtitle": "Page", "url": link["url"],
                            "icon": "fa-solid fa-file"})

    for sec in SITE_SCHEMA:
        for field in sec["fields"]:
            if field["type"] == "image":
                continue
            val = site.get(field["key"], "")
            if _matches(q, val, field["label"], sec["section"]):
                target = "/"
                if "contact" in field["key"] or "location" in field["key"]:
                    target = "/#contact-section"
                results.append({"type": "content", "title": field["label"],
                                "subtitle": (val or "")[:70], "url": target,
                                "icon": sec.get("icon", "fa-solid fa-circle-info")})

    for p in fetch_projects():
        price_str = f"{p.get('price_from', 0):,}"
        if _matches(q, p["name"], p.get("short_desc",""), p.get("long_desc",""),
                    p.get("location",""), p.get("units",""), p.get("category",""),
                    p.get("custom_type",""),
                    price_str, str(p.get("price_from","")), p.get("status","")):
            results.append({"type": "project", "title": p["name"],
                            "subtitle": f"{p.get('location','')} · from {price_str}",
                            "url": url_for("project_detail", slug=p["slug"]),
                            "icon": "fa-solid fa-building"})

    for d in fetch_drugs():
        price_str = f"{d.get('price', 0):,}"
        if _matches(q, d["name"], d.get("drug_type",""), d.get("description",""),
                    price_str, str(d.get("price",""))):
            results.append({"type": "project", "title": d["name"],
                            "subtitle": f"{d.get('drug_type','')} · {price_str}",
                            "url": url_for("drugs_page"),
                            "icon": "fa-solid fa-prescription-bottle-medical"})

    for v in fetch_videos():
        if _matches(q, v["title"], v.get("description","")):
            results.append({"type": "video", "title": v["title"],
                            "subtitle": (v.get("description") or "")[:70],
                            "url": url_for("videos_page"),
                            "icon": "fa-solid fa-video"})

    for g in fetch_gallery():
        if _matches(q, g.get("title","")):
            results.append({"type": "gallery", "title": g.get("title") or "Gallery image",
                            "subtitle": "Gallery", "url": url_for("gallery_page"),
                            "icon": "fa-solid fa-image"})

    return jsonify(results[:30])


# ============================================================
# ADMIN — AUTH
# ============================================================
@app.route("/update/login", methods=["GET", "POST"])
def update_login():
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd in ADMIN_PASSWORDS:
            session["admin_logged_in"] = True
            session.permanent = True
            return redirect(url_for("update_dashboard"))
        flash("Wrong password", "error")
    return render_template("update/login.html")


@app.route("/update/logout")
def update_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("update_login"))


# ============================================================
# ADMIN — DASHBOARD
# ============================================================
@app.route("/update")
@login_required
def update_dashboard():
    def count(table):
        try:
            res = supabase.table(table).select("id").execute()
            return len(res.data or [])
        except Exception:
            return 0
    stats = {
        "projects":    count("nh_projects"),
        "drugs":       count("nh_drugs"),
        "videos":      count("nh_videos"),
        "gallery":     count("nh_gallery_images"),
        "inquiries":   count("nh_inquiries"),
        "nav":         count("nh_nav_links"),
        "types":       count("nh_property_types"),
        "drug_types":  count("nh_drug_types"),
    }
    return render_template("update/dashboard.html", stats=stats)


# ============================================================
# ADMIN — SITE CONTENT
# ============================================================
@app.route("/update/site", methods=["GET", "POST"])
@login_required
def update_site():
    if request.method == "POST":
        rows = []
        for sec in SITE_SCHEMA:
            for f in sec["fields"]:
                key = f["key"]
                if f["type"] == "image":
                    val = None
                    file_field = f"file_{key}"
                    url_field  = f"url_{key}"
                    if file_field in request.files and request.files[file_field].filename:
                        url = save_image(request.files[file_field], BUCKET_IMAGES)
                        if url:
                            val = url
                    if val is None and url_field in request.form:
                        url_val = request.form.get(url_field, "").strip()
                        if url_val:
                            val = url_val
                    if val is not None:
                        rows.append({"key": key, "value": val})
                else:
                    val = request.form.get(key, "").strip()
                    rows.append({"key": key, "value": val})
        try:
            if rows:
                supabase.table("nh_site_content").upsert(rows).execute()
            flash("Site content updated.", "success")
        except Exception as e:
            print("update_site error:", e)
            flash(f"Error: {e}", "error")
        return redirect(url_for("update_site"))
    return render_template("update/site.html", schema=SITE_SCHEMA)


# ============================================================
# ADMIN — PROPERTY TYPES
# ============================================================
@app.route("/update/property-types")
@login_required
def update_property_types():
    types = fetch_property_types()
    return render_template("update/property_types.html", types=types)


@app.route("/update/property-types/new", methods=["POST"])
@login_required
def update_property_type_new():
    label = (request.form.get("label") or "").strip()
    order = request.form.get("sort_order", 99, type=int)
    if not label:
        flash("Type name is required.", "error")
        return redirect(url_for("update_property_types"))
    try:
        res = supabase.table("nh_property_types").select("id").ilike("label", label).limit(1).execute()
        if res.data:
            flash("That type already exists.", "error")
            return redirect(url_for("update_property_types"))
        supabase.table("nh_property_types").insert({
            "label": label, "sort_order": order, "is_active": True,
        }).execute()
        flash("Type added.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_property_types"))


@app.route("/update/property-types/edit/<int:tid>", methods=["POST"])
@login_required
def update_property_type_edit(tid):
    label  = (request.form.get("label") or "").strip()
    order  = request.form.get("sort_order", 99, type=int)
    active = request.form.get("is_active") == "on"

    if not label:
        flash("Type name is required.", "error")
        return redirect(url_for("update_property_types"))

    try:
        old_res = supabase.table("nh_property_types").select("label").eq("id", tid).single().execute()
        old_label = (old_res.data or {}).get("label", "")
        supabase.table("nh_property_types").update({
            "label": label, "sort_order": order, "is_active": active,
        }).eq("id", tid).execute()
        if old_label and old_label != label:
            supabase.table("nh_projects").update({"custom_type": label}).ilike("custom_type", old_label).execute()
        flash("Type updated.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_property_types"))


@app.route("/update/property-types/delete/<int:tid>", methods=["POST"])
@login_required
def update_property_type_delete(tid):
    try:
        supabase.table("nh_property_types").delete().eq("id", tid).execute()
        flash("Type deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_property_types"))


# ============================================================
# ADMIN — DRUG TYPES
# ============================================================
@app.route("/update/drug-types")
@login_required
def update_drug_types():
    types = fetch_drug_types()
    return render_template("update/drug_types.html", types=types)


@app.route("/update/drug-types/new", methods=["POST"])
@login_required
def update_drug_type_new():
    label = (request.form.get("label") or "").strip()
    order = request.form.get("sort_order", 99, type=int)
    if not label:
        flash("Type name is required.", "error")
        return redirect(url_for("update_drug_types"))
    try:
        res = supabase.table("nh_drug_types").select("id").ilike("label", label).limit(1).execute()
        if res.data:
            flash("That type already exists.", "error")
            return redirect(url_for("update_drug_types"))
        supabase.table("nh_drug_types").insert({
            "label": label, "sort_order": order, "is_active": True,
        }).execute()
        flash("Type added.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_drug_types"))


@app.route("/update/drug-types/edit/<int:tid>", methods=["POST"])
@login_required
def update_drug_type_edit(tid):
    label  = (request.form.get("label") or "").strip()
    order  = request.form.get("sort_order", 99, type=int)
    active = request.form.get("is_active") == "on"

    if not label:
        flash("Type name is required.", "error")
        return redirect(url_for("update_drug_types"))

    try:
        old_res = supabase.table("nh_drug_types").select("label").eq("id", tid).single().execute()
        old_label = (old_res.data or {}).get("label", "")
        supabase.table("nh_drug_types").update({
            "label": label, "sort_order": order, "is_active": active,
        }).eq("id", tid).execute()
        if old_label and old_label != label:
            supabase.table("nh_drugs").update({"drug_type": label}).ilike("drug_type", old_label).execute()
        flash("Type updated.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_drug_types"))


@app.route("/update/drug-types/delete/<int:tid>", methods=["POST"])
@login_required
def update_drug_type_delete(tid):
    try:
        supabase.table("nh_drug_types").delete().eq("id", tid).execute()
        flash("Type deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_drug_types"))


# ============================================================
# ADMIN — PROJECTS
# ============================================================
@app.route("/update/projects")
@login_required
def update_projects():
    return render_template("update/projects.html", projects=fetch_projects())


@app.route("/update/projects/new", methods=["GET", "POST"])
@login_required
def update_project_new():
    if request.method == "POST":
        return _save_project(None)
    return render_template("update/project_form.html", project=None,
                           property_types=fetch_property_types(only_active=True))


@app.route("/update/projects/edit/<int:pid>", methods=["GET", "POST"])
@login_required
def update_project_edit(pid):
    try:
        res = supabase.table("nh_projects").select("*").eq("id", pid).single().execute()
        project = res.data
    except Exception:
        project = None
    if not project:
        abort(404)
    if request.method == "POST":
        return _save_project(project)
    return render_template("update/project_form.html", project=project,
                           property_types=fetch_property_types(only_active=True))


def _save_project(project):
    name        = (request.form.get("name") or "").strip()
    slug        = (request.form.get("slug") or "").strip().lower().replace(" ", "-")
    category    = (request.form.get("category") or "residential").strip()
    custom_type = (request.form.get("custom_type") or "").strip()
    if category != "other":
        custom_type = ""
    status      = (request.form.get("status") or "").strip()
    currency    = (request.form.get("currency") or "GHS").strip()
    short_desc  = (request.form.get("short_desc") or "").strip()
    long_desc   = (request.form.get("long_desc") or "").strip()
    location    = (request.form.get("location") or "").strip()
    units       = (request.form.get("units") or "").strip()
    try:
        price_from = int(float(request.form.get("price_from", 0) or 0))
    except (ValueError, TypeError):
        price_from = 0
    featured = request.form.get("featured") == "on"

    image_uploaded = None
    if "image_file" in request.files and request.files["image_file"].filename:
        image_uploaded = save_image(request.files["image_file"], BUCKET_IMAGES)

    hero_uploaded = None
    if "hero_file" in request.files and request.files["hero_file"].filename:
        hero_uploaded = save_image(request.files["hero_file"], BUCKET_IMAGES)

    video_uploaded = None
    if "video_file" in request.files and request.files["video_file"].filename:
        video_uploaded = save_video(request.files["video_file"])

    image = image_uploaded or request.form.get("image_url","").strip() or \
            (project["image"] if project else "")
    hero  = hero_uploaded  or request.form.get("hero_url","").strip() or \
            (project.get("hero_image") if project else "")
    video = video_uploaded or request.form.get("video_url","").strip() or \
            (project.get("video") if project else "")

    payload = {
        "name": name, "slug": slug, "category": category,
        "custom_type": custom_type, "status": status, "currency": currency,
        "short_desc": short_desc, "long_desc": long_desc,
        "location": location, "units": units,
        "price_from": price_from, "image": image, "hero_image": hero,
        "video": video, "featured": featured,
    }

    try:
        if project:
            supabase.table("nh_projects").update(payload).eq("id", project["id"]).execute()
            flash("Property updated.", "success")
        else:
            payload["sort_order"] = 99
            supabase.table("nh_projects").insert(payload).execute()
            flash("Property created.", "success")

        if custom_type:
            ensure_property_type(custom_type)

    except Exception as e:
        print("save project error:", e)
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_projects"))


@app.route("/update/projects/delete/<int:pid>", methods=["POST"])
@login_required
def update_project_delete(pid):
    try:
        supabase.table("nh_projects").delete().eq("id", pid).execute()
        flash("Property deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_projects"))


# ============================================================
# ADMIN — DRUGS
# ============================================================
@app.route("/update/drugs")
@login_required
def update_drugs():
    return render_template("update/drugs.html", drugs=fetch_drugs())


@app.route("/update/drugs/new", methods=["GET", "POST"])
@login_required
def update_drug_new():
    if request.method == "POST":
        return _save_drug(None)
    return render_template("update/drug_form.html", drug=None,
                           drug_types=fetch_drug_types(only_active=True))


@app.route("/update/drugs/edit/<int:did>", methods=["GET", "POST"])
@login_required
def update_drug_edit(did):
    drug = fetch_drug(did)
    if not drug:
        abort(404)
    if request.method == "POST":
        return _save_drug(drug)
    return render_template("update/drug_form.html", drug=drug,
                           drug_types=fetch_drug_types(only_active=True))


def _save_drug(drug):
    name        = (request.form.get("name") or "").strip()
    slug        = (request.form.get("slug") or "").strip().lower().replace(" ", "-")
    drug_type   = (request.form.get("drug_type") or "").strip()
    currency    = (request.form.get("currency") or "GHS").strip()
    description = (request.form.get("description") or "").strip()
    try:
        price = int(float(request.form.get("price", 0) or 0))
    except (ValueError, TypeError):
        price = 0
    featured = request.form.get("featured") == "on"

    image_uploaded = None
    if "image_file" in request.files and request.files["image_file"].filename:
        image_uploaded = save_image(request.files["image_file"], BUCKET_IMAGES)

    video_uploaded = None
    if "video_file" in request.files and request.files["video_file"].filename:
        video_uploaded = save_video(request.files["video_file"])

    image = image_uploaded or request.form.get("image_url","").strip() or \
            (drug["image"] if drug else "")
    video = video_uploaded or request.form.get("video_url","").strip() or \
            (drug.get("video") if drug else "")

    payload = {
        "name": name, "slug": slug, "drug_type": drug_type,
        "price": price, "currency": currency,
        "description": description,
        "image": image, "video": video,
        "featured": featured,
    }

    try:
        if drug:
            supabase.table("nh_drugs").update(payload).eq("id", drug["id"]).execute()
            flash("Product updated.", "success")
        else:
            payload["sort_order"] = 99
            supabase.table("nh_drugs").insert(payload).execute()
            flash("Product created.", "success")

        if drug_type:
            ensure_drug_type(drug_type)

    except Exception as e:
        print("save drug error:", e)
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_drugs"))


@app.route("/update/drugs/delete/<int:did>", methods=["POST"])
@login_required
def update_drug_delete(did):
    try:
        supabase.table("nh_drugs").delete().eq("id", did).execute()
        flash("Product deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_drugs"))


# ============================================================
# ADMIN — VIDEOS
# ============================================================
@app.route("/update/videos")
@login_required
def update_videos():
    return render_template("update/videos.html", videos=fetch_videos(),
                           max_videos=MAX_VIDEOS,
                           max_mb=MAX_VIDEO_BYTES // (1024 * 1024))


@app.route("/update/videos/upload", methods=["POST"])
@login_required
def update_video_upload():
    existing = fetch_videos()
    if len(existing) >= MAX_VIDEOS:
        flash(f"Maximum of {MAX_VIDEOS} videos reached.", "error")
        return redirect(url_for("update_videos"))

    title = (request.form.get("title") or "").strip() or "Untitled"
    desc  = (request.form.get("description") or "").strip()
    file  = request.files.get("video_file")
    if not file or not file.filename:
        flash("Please choose a video file.", "error")
        return redirect(url_for("update_videos"))

    url = save_video(file)
    if not url:
        flash(f"Invalid video or exceeds {MAX_VIDEO_BYTES // (1024*1024)}MB limit.", "error")
        return redirect(url_for("update_videos"))

    featured = request.form.get("is_featured") == "on"
    try:
        if featured:
            supabase.table("nh_videos").update({"is_featured": False}).neq("id", 0).execute()
        supabase.table("nh_videos").insert({
            "title": title, "description": desc, "filename": url,
            "is_featured": featured, "sort_order": len(existing) + 1,
        }).execute()
        flash("Video uploaded.", "success")
    except Exception as e:
        print("video upload error:", e)
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_videos"))


@app.route("/update/videos/edit/<int:vid>", methods=["POST"])
@login_required
def update_video_edit(vid):
    title = (request.form.get("title") or "").strip() or "Untitled"
    desc  = (request.form.get("description") or "").strip()
    featured = request.form.get("is_featured") == "on"
    try:
        if featured:
            supabase.table("nh_videos").update({"is_featured": False}).neq("id", vid).execute()
        supabase.table("nh_videos").update({
            "title": title, "description": desc, "is_featured": featured,
        }).eq("id", vid).execute()
        flash("Video updated.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_videos"))


@app.route("/update/videos/delete/<int:vid>", methods=["POST"])
@login_required
def update_video_delete(vid):
    try:
        res = supabase.table("nh_videos").select("filename").eq("id", vid).single().execute()
        filename = (res.data or {}).get("filename", "")
        delete_supabase_file(filename, BUCKET_VIDEOS)
        supabase.table("nh_videos").delete().eq("id", vid).execute()
        flash("Video deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_videos"))


# ============================================================
# ADMIN — GALLERY
# ============================================================
@app.route("/update/gallery")
@login_required
def update_gallery():
    return render_template("update/gallery.html", images=fetch_gallery())


@app.route("/update/gallery/upload", methods=["POST"])
@login_required
def update_gallery_upload():
    title = (request.form.get("title") or "").strip()
    file  = request.files.get("image")
    url   = save_image(file, BUCKET_GALLERY)
    if not url:
        flash("Invalid image or exceeds 5MB.", "error")
        return redirect(url_for("update_gallery"))
    try:
        supabase.table("nh_gallery_images").insert({
            "title": title, "filename": url, "source": "upload", "sort_order": 99,
        }).execute()
        flash("Image uploaded.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_gallery"))


@app.route("/update/gallery/delete/<int:img_id>", methods=["POST"])
@login_required
def update_gallery_delete(img_id):
    try:
        res = supabase.table("nh_gallery_images").select("filename").eq("id", img_id).single().execute()
        url = (res.data or {}).get("filename", "")
        delete_supabase_file(url, BUCKET_GALLERY)
        supabase.table("nh_gallery_images").delete().eq("id", img_id).execute()
        flash("Image deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_gallery"))


# ============================================================
# ADMIN — NAV
# ============================================================
@app.route("/update/nav")
@login_required
def update_nav():
    try:
        res = supabase.table("nh_nav_links").select("*").order("sort_order").order("id").execute()
        links = res.data or []
    except Exception:
        links = []
    return render_template("update/nav.html", links=links)


@app.route("/update/nav/new", methods=["POST"])
@login_required
def update_nav_new():
    label = (request.form.get("label") or "").strip()
    url   = (request.form.get("url") or "").strip()
    order = request.form.get("sort_order", 99, type=int)
    if label and url:
        try:
            supabase.table("nh_nav_links").insert({
                "label": label, "url": url, "sort_order": order, "is_locked": False, "visible": True,
            }).execute()
            flash("Nav link added.", "success")
        except Exception as e:
            flash(f"Error: {e}", "error")
    else:
        flash("Label and URL required.", "error")
    return redirect(url_for("update_nav"))


@app.route("/update/nav/edit/<int:lid>", methods=["POST"])
@login_required
def update_nav_edit(lid):
    try:
        res = supabase.table("nh_nav_links").select("*").eq("id", lid).single().execute()
        row = res.data
        if not row:
            abort(404)
        if row.get("is_locked"):
            flash("This link is locked.", "error")
            return redirect(url_for("update_nav"))
        supabase.table("nh_nav_links").update({
            "label": (request.form.get("label") or "").strip(),
            "url":   (request.form.get("url") or "").strip(),
            "sort_order": request.form.get("sort_order", row["sort_order"], type=int),
        }).eq("id", lid).execute()
        flash("Nav link updated.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_nav"))


@app.route("/update/nav/delete/<int:lid>", methods=["POST"])
@login_required
def update_nav_delete(lid):
    try:
        res = supabase.table("nh_nav_links").select("is_locked").eq("id", lid).single().execute()
        if (res.data or {}).get("is_locked"):
            flash("This link is locked.", "error")
            return redirect(url_for("update_nav"))
        supabase.table("nh_nav_links").delete().eq("id", lid).execute()
        flash("Nav link deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_nav"))


# ============================================================
# ADMIN — INQUIRIES
# ============================================================
@app.route("/update/inquiries")
@login_required
def update_inquiries():
    try:
        res = supabase.table("nh_inquiries").select("*").order("id", desc=True).execute()
        inquiries = res.data or []
    except Exception:
        inquiries = []
    return render_template("update/inquiries.html", inquiries=inquiries)


@app.route("/update/inquiries/delete/<int:iid>", methods=["POST"])
@login_required
def update_inquiry_delete(iid):
    try:
        supabase.table("nh_inquiries").delete().eq("id", iid).execute()
        flash("Inquiry deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_inquiries"))


# ============================================================
# ERROR HANDLERS
# ============================================================
@app.errorhandler(413)
def too_large(e):
    flash("File too large.", "error")
    return redirect(request.referrer or url_for("index"))


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# ============================================================
# INIT + RUN
# ============================================================
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)