import os
import uuid
import sqlite3
from functools import wraps
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort, jsonify
)

load_dotenv()

# ============================================================
# CONFIG
# ============================================================
SECRET_KEY     = os.environ.get("SECRET_KEY", "newhorizon-secret-2026-klinsman")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Klinsman@ophyser1")

WHATSAPP_NUMBER = "233243444343"
PHONE_NUMBER    = "+233243444343"
PHONE_DISPLAY   = "+233 24 344 4343"
EMAIL_ADDRESS   = "info@newhorizongh.com"
ADDRESS         = "Tema Community 25, Ghana"

MAX_VIDEOS              = 10
MAX_VIDEO_BYTES         = 20 * 1024 * 1024      # 20 MB (global video band)
MAX_IMAGE_BYTES         = 15 * 1024 * 1024      # 15 MB (phone photos safe)
MAX_PROJECT_IMAGES      = 7
MAX_PROJECT_VIDEO_BYTES = 20 * 1024 * 1024      # 20 MB (per-project video)

# LOCAL STORAGE
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DB_PATH    = os.path.join(BASE_DIR, "nh.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
UPLOAD_URL = "/static/uploads"

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024   # 30 MB request cap


# ============================================================
# SITE SCHEMA — only fields that render on the site
# ============================================================
SITE_SCHEMA = [
    {
        "section": "Branding",
        "icon": "fa-solid fa-tag",
        "fields": [
            {"key": "brand_name",    "label": "Brand Name (browser tab)", "type": "text",  "default": "New Horizon Coopers Limited"},
            {"key": "brand_new",     "label": "Logo Word 1 (dark)",       "type": "text",  "default": "NEW"},
            {"key": "brand_horizon", "label": "Logo Word 2 (orange)",     "type": "text",  "default": "HORIZON"},
            {"key": "brand_coopers", "label": "Coopers Limited line",     "type": "text",  "default": "Coopers Limited"},
            {"key": "brand_tagline", "label": "Tagline (below logo)",     "type": "text",  "default": "Real Estate & Pharmaceutical Agency"},
            {"key": "logo_path",     "label": "Admin Sidebar Logo",       "type": "image", "default": ""},
        ],
    },
    {
        "section": "Homepage — Hero Images",
        "icon": "fa-solid fa-image",
        "fields": [
            {"key": "hero_image1", "label": "Hero 1 — Top Image",   "type": "image", "default": ""},
            {"key": "hero_image2", "label": "Hero 2 — Below Image", "type": "image", "default": ""},
        ],
    },
    {
        "section": "Header",
        "icon": "fa-solid fa-bars",
        "fields": [
            {"key": "header_cta_text",  "label": "Header Button Text",     "type": "text", "default": "Book Consultation"},
            {"key": "header_search_ph", "label": "Search box placeholder", "type": "text", "default": "Search properties, products, pages…"},
        ],
    },
    {
        "section": "Search Bar Messages",
        "icon": "fa-solid fa-magnifying-glass",
        "fields": [
            {"key": "search_hint",        "label": "Hint (empty state)",  "type": "text", "default": "Start typing to search pages, projects, and products."},
            {"key": "search_loading",     "label": "Loading message",     "type": "text", "default": "Searching…"},
            {"key": "search_no_results",  "label": "No results message",  "type": "text", "default": "No results found."},
            {"key": "search_unavailable", "label": "Unavailable message", "type": "text", "default": "Search unavailable."},
        ],
    },
    {
        "section": "Real Estates Section (homepage)",
        "icon": "fa-solid fa-house-chimney-window",
        "fields": [
            {"key": "estates_title",    "label": "Title — dark part",   "type": "text", "default": "NEW HORIZON"},
            {"key": "estates_title_em", "label": "Title — italic part", "type": "text", "default": "REAL ESTATES"},
            {"key": "estates_sub",      "label": "Subtext",             "type": "text", "default": "We have the following"},
            {"key": "estates_cta",      "label": "See-all button text", "type": "text", "default": "See all properties"},
        ],
    },
    {
        "section": "CTA Band (bottom of homepage)",
        "icon": "fa-solid fa-bullhorn",
        "fields": [
            {"key": "cta_eyebrow",       "label": "Eyebrow",               "type": "text", "default": "Let's talk"},
            {"key": "cta_title",         "label": "Title — line 1",        "type": "text", "default": "Ready to find your"},
            {"key": "cta_title_em",      "label": "Title — italic line",   "type": "text", "default": "next address?"},
            {"key": "cta_sub",           "label": "Subtext",               "type": "text", "default": "Whether you're buying a home, supplying a pharmacy, or exploring a partnership — our team is one call away."},
            {"key": "cta_btn_primary",   "label": "Primary button text",   "type": "text", "default": "Book a consultation"},
            {"key": "cta_btn_secondary", "label": "Secondary button text", "type": "text", "default": "Contact us"},
        ],
    },
    {
        "section": "Contact Info (footer + contact page)",
        "icon": "fa-solid fa-address-book",
        "fields": [
            {"key": "contact_email",         "label": "Email Address",              "type": "text", "default": EMAIL_ADDRESS},
            {"key": "contact_phone_display", "label": "Phone (displayed)",          "type": "text", "default": PHONE_DISPLAY},
            {"key": "contact_whatsapp_num",  "label": "WhatsApp (no +, no spaces)", "type": "text", "default": WHATSAPP_NUMBER},
            {"key": "location_address",      "label": "Office Address",             "type": "text", "default": ADDRESS},
        ],
    },
    {
        "section": "Footer",
        "icon": "fa-solid fa-shoe-prints",
        "fields": [
            {"key": "footer_blurb", "label": "Blurb (under logo)", "type": "textarea",
             "default": "New Horizon Coopers Limited — building sustainable, modern communities across Ghana since 2017."},

            {"key": "footer_col_company",   "label": "Col 1 — heading", "type": "text", "default": "Company"},
            {"key": "footer_link_about",    "label": "Col 1 — Link 1",  "type": "text", "default": "About"},
            {"key": "footer_link_projects", "label": "Col 1 — Link 2",  "type": "text", "default": "Projects"},
            {"key": "footer_link_gallery",  "label": "Col 1 — Link 3",  "type": "text", "default": "Gallery"},
            {"key": "footer_link_contact",  "label": "Col 1 — Link 4",  "type": "text", "default": "Contact"},

            {"key": "footer_col_divisions",   "label": "Col 2 — heading", "type": "text", "default": "Divisions"},
            {"key": "footer_link_realestate", "label": "Col 2 — Link 1",  "type": "text", "default": "Real Estate"},

            {"key": "footer_col_contact", "label": "Col 3 — heading", "type": "text", "default": "Contact"},

            {"key": "footer_copyright", "label": "Bottom bar — copyright", "type": "text", "default": "© 2026 New Horizon Coopers Limited"},
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
# SQLITE HELPERS
# ============================================================
def _conn():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def query(sql, params=(), one=False):
    conn = _conn()
    try:
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        if one:
            return dict(rows[0]) if rows else None
        return [dict(r) for r in rows]
    finally:
        conn.close()


def execute(sql, params=()):
    conn = _conn()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def insert_row(table, data):
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    return execute(
        f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
        tuple(data.values()),
    )


def update_row(table, data, where_col, where_val):
    set_clause = ", ".join(f"{k} = ?" for k in data.keys())
    execute(
        f"UPDATE {table} SET {set_clause} WHERE {where_col} = ?",
        tuple(data.values()) + (where_val,),
    )


# ============================================================
# INIT — create tables + seed
# ============================================================
def create_tables():
    conn = _conn()
    try:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS nh_site_content (
            key   TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS nh_nav_links (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            label       TEXT NOT NULL,
            url         TEXT NOT NULL,
            sort_order  INTEGER DEFAULT 99,
            is_locked   INTEGER DEFAULT 0,
            visible     INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS nh_property_types (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            label       TEXT NOT NULL,
            sort_order  INTEGER DEFAULT 99,
            is_active   INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS nh_projects (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            slug              TEXT UNIQUE NOT NULL,
            name              TEXT NOT NULL,
            category          TEXT NOT NULL DEFAULT 'residential',
            custom_type       TEXT,
            status            TEXT,
            currency          TEXT DEFAULT 'GHS',
            short_desc        TEXT,
            long_desc         TEXT,
            location          TEXT,
            units             TEXT,
            price_from        INTEGER DEFAULT 0,
            image             TEXT,
            hero_image        TEXT,
            video             TEXT,
            video_description TEXT,
            featured          INTEGER DEFAULT 0,
            sort_order        INTEGER DEFAULT 99
        );

        CREATE TABLE IF NOT EXISTS nh_project_images (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id  INTEGER NOT NULL,
            image_url   TEXT NOT NULL,
            description TEXT,
            sort_order  INTEGER DEFAULT 99,
            FOREIGN KEY (project_id) REFERENCES nh_projects(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS nh_videos (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT NOT NULL,
            description  TEXT,
            filename     TEXT,
            is_featured  INTEGER DEFAULT 0,
            sort_order   INTEGER DEFAULT 99
        );

        CREATE TABLE IF NOT EXISTS nh_gallery_images (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT,
            filename    TEXT NOT NULL,
            source      TEXT DEFAULT 'upload',
            sort_order  INTEGER DEFAULT 99
        );

        CREATE TABLE IF NOT EXISTS nh_inquiries (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            kind            TEXT NOT NULL,
            name            TEXT NOT NULL,
            email           TEXT,
            phone           TEXT,
            subject         TEXT,
            message         TEXT,
            preferred_date  TEXT,
            created_at      TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
    finally:
        conn.close()


def seed_if_empty(table, rows):
    try:
        existing = query(f"SELECT id FROM {table} LIMIT 1")
        if existing:
            return
        for row in rows:
            insert_row(table, row)
        print(f"[INIT] Seeded {table} with {len(rows)} rows")
    except Exception as e:
        print(f"seed {table} error:", e)


def init_db():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    create_tables()

    # Seed site_content
    try:
        defaults = get_schema_defaults()
        for k, v in defaults.items():
            execute(
                "INSERT OR IGNORE INTO nh_site_content (key, value) VALUES (?, ?)",
                (k, v),
            )
    except Exception as e:
        print("seed site_content error:", e)

    # Nav links
    seed_if_empty("nh_nav_links", [
        {"label": "Home",       "url": "/",         "sort_order": 1, "is_locked": 1, "visible": 1},
        {"label": "About Us",   "url": "/about",    "sort_order": 2, "is_locked": 0, "visible": 1},
        {"label": "Housing",    "url": "/projects", "sort_order": 3, "is_locked": 0, "visible": 1},
        {"label": "Gallery",    "url": "/gallery",  "sort_order": 4, "is_locked": 0, "visible": 1},
        {"label": "Contact Us", "url": "/contact",  "sort_order": 5, "is_locked": 0, "visible": 1},
    ])

    # Property types
    seed_if_empty("nh_property_types", [
        {"label": "Villa",     "sort_order": 1, "is_active": 1},
        {"label": "Townhouse", "sort_order": 2, "is_active": 1},
        {"label": "Apartment", "sort_order": 3, "is_active": 1},
        {"label": "Warehouse", "sort_order": 4, "is_active": 1},
    ])

    # Demo projects
    seed_if_empty("nh_projects", [
        {"slug":"east-legon-villas","name":"East Legon Villas","category":"residential","custom_type":"",
         "status":"ongoing","currency":"USD","short_desc":"2 Bedrooms · 2 Baths · 180 sqm",
         "long_desc":"East Legon Villas is an exclusive collection of modern luxury villas nestled in the heart of Accra.",
         "location":"East Legon, Accra","units":"48 Villas","price_from":420000,
         "image":"https://picsum.photos/seed/eastlegon/600/400",
         "hero_image":"https://picsum.photos/seed/eastlegon/1600/900",
         "video":"","video_description":"","featured":1,"sort_order":1},

        {"slug":"tema-eco-townhomes","name":"Tema Eco Townhomes","category":"residential","custom_type":"",
         "status":"fully-complete","currency":"USD","short_desc":"3 Bedrooms · 2 Baths · 220 sqm",
         "long_desc":"Tema Eco Townhomes offers a new standard of sustainable family living.",
         "location":"Tema, Greater Accra","units":"32 Townhomes","price_from":385000,
         "image":"https://picsum.photos/seed/temaeco/600/400",
         "hero_image":"https://picsum.photos/seed/temaeco/1600/900",
         "video":"","video_description":"","featured":1,"sort_order":2},

        {"slug":"airport-city-lofts","name":"Airport City Lofts","category":"commercial","custom_type":"",
         "status":"partially-complete","currency":"USD","short_desc":"Modern commercial space · 120 sqm",
         "long_desc":"Airport City Lofts is a landmark commercial development near Kotoka International Airport.",
         "location":"Airport City, Accra","units":"12 Units","price_from":220000,
         "image":"https://picsum.photos/seed/airportcity/600/400",
         "hero_image":"https://picsum.photos/seed/airportcity/1600/900",
         "video":"","video_description":"","featured":1,"sort_order":3},

        {"slug":"kumasi-garden-estate","name":"Kumasi Garden Estate","category":"residential","custom_type":"",
         "status":"ongoing","currency":"GHS","short_desc":"4 Bedrooms · 3 Baths · 320 sqm",
         "long_desc":"Kumasi Garden Estate is a master-planned community in Asokwa, Kumasi.",
         "location":"Asokwa, Kumasi","units":"60 Homes","price_from":310000,
         "image":"https://picsum.photos/seed/kumasigarden/600/400",
         "hero_image":"https://picsum.photos/seed/kumasigarden/1600/900",
         "video":"","video_description":"","featured":0,"sort_order":4},

        {"slug":"takoradi-business-park","name":"Takoradi Business Park","category":"commercial","custom_type":"",
         "status":"about-to-start","currency":"GHS","short_desc":"Office & retail space · 90 sqm",
         "long_desc":"Takoradi Business Park is a mixed-use commercial development in Ghana's oil city.",
         "location":"Takoradi, Western Region","units":"24 Units","price_from":195000,
         "image":"https://picsum.photos/seed/takoradipark/600/400",
         "hero_image":"https://picsum.photos/seed/takoradipark/1600/900",
         "video":"","video_description":"","featured":0,"sort_order":5},
    ])

    # Video placeholder
    seed_if_empty("nh_videos", [
        {"title":"New Horizon Showreel",
         "description":"A glimpse into our latest developments across Ghana.",
         "filename":"", "is_featured": 1, "sort_order": 1}
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
        rows = query("SELECT key, value FROM nh_site_content")
        for row in rows:
            defaults[row["key"]] = row["value"]
    except Exception as e:
        print("fetch_site error:", e)
    return defaults


def fetch_nav():
    try:
        return query(
            "SELECT * FROM nh_nav_links WHERE visible = 1 "
            "ORDER BY sort_order ASC, id ASC"
        )
    except Exception as e:
        print("fetch_nav error:", e)
        return []


def fetch_projects(category=None, featured_only=False, custom_type=None):
    try:
        sql = "SELECT * FROM nh_projects WHERE 1=1"
        params = []
        if category:
            sql += " AND category = ?"
            params.append(category)
        if custom_type:
            sql += " AND LOWER(custom_type) = LOWER(?)"
            params.append(custom_type)
        if featured_only:
            sql += " AND featured = 1"
        sql += " ORDER BY sort_order ASC, id ASC"
        return query(sql, tuple(params))
    except Exception as e:
        print("fetch_projects error:", e)
        return []


def fetch_project(slug):
    try:
        return query("SELECT * FROM nh_projects WHERE slug = ? LIMIT 1",
                     (slug,), one=True)
    except Exception:
        return None


def fetch_project_images(project_id):
    try:
        return query(
            "SELECT * FROM nh_project_images WHERE project_id = ? "
            "ORDER BY sort_order ASC, id ASC", (project_id,)
        )
    except Exception as e:
        print("fetch_project_images error:", e)
        return []


def fetch_property_types(only_active=False):
    try:
        sql = "SELECT * FROM nh_property_types"
        if only_active:
            sql += " WHERE is_active = 1"
        sql += " ORDER BY sort_order ASC, id ASC"
        return query(sql)
    except Exception as e:
        print("fetch_property_types error:", e)
        return []


def ensure_property_type(label):
    label = (label or "").strip()
    if not label:
        return
    try:
        existing = query(
            "SELECT id FROM nh_property_types WHERE LOWER(label) = LOWER(?) LIMIT 1",
            (label,), one=True
        )
        if existing:
            return
        row = query("SELECT MAX(sort_order) AS m FROM nh_property_types", one=True)
        next_order = (row["m"] or 0) + 1 if row else 1
        insert_row("nh_property_types", {
            "label": label, "sort_order": next_order, "is_active": 1,
        })
    except Exception as e:
        print("ensure_property_type error:", e)


def fetch_custom_types():
    return [t["label"] for t in fetch_property_types(only_active=True)]


def fetch_videos():
    try:
        return query("SELECT * FROM nh_videos ORDER BY sort_order ASC, id ASC")
    except Exception as e:
        print("fetch_videos error:", e)
        return []


def fetch_featured_video():
    try:
        row = query(
            "SELECT * FROM nh_videos WHERE is_featured = 1 "
            "ORDER BY sort_order ASC LIMIT 1", one=True
        )
        if row:
            return row
        return query("SELECT * FROM nh_videos ORDER BY sort_order ASC LIMIT 1",
                     one=True)
    except Exception as e:
        print("fetch_featured_video error:", e)
        return None


def fetch_gallery():
    combined = []
    try:
        rows = query("SELECT * FROM nh_gallery_images ORDER BY sort_order ASC, id ASC")
        for g in rows:
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
        rows = query(
            "SELECT id, name, image, sort_order FROM nh_projects "
            "WHERE image IS NOT NULL AND image != '' "
            "ORDER BY sort_order ASC, id ASC"
        )
        for p in rows:
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
    """Save file to static/uploads/<bucket>/. Returns public URL or None."""
    if not file_storage or not file_storage.filename:
        return None
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed_exts:
        return None
    data = file_storage.read()
    if len(data) > max_bytes:
        return None

    subdir = os.path.join(UPLOAD_DIR, bucket)
    os.makedirs(subdir, exist_ok=True)

    name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(subdir, name)
    try:
        with open(filepath, "wb") as f:
            f.write(data)
        return f"{UPLOAD_URL}/{bucket}/{name}"
    except Exception as e:
        print(f"upload to {bucket} error:", e)
        return None


def delete_local_upload(url):
    if not url or not url.startswith(UPLOAD_URL + "/"):
        return
    rel = url[len(UPLOAD_URL) + 1:]
    filepath = os.path.join(UPLOAD_DIR, rel)
    try:
        if os.path.isfile(filepath):
            os.remove(filepath)
    except Exception as e:
        print("delete_local_upload error:", e)


def save_image(file_storage, bucket="nh-images"):
    return upload_to_bucket(
        file_storage, bucket,
        {"png", "jpg", "jpeg", "gif", "webp", "svg"},
        MAX_IMAGE_BYTES,
    )


def save_video(file_storage):
    return upload_to_bucket(
        file_storage, "nh-videos",
        {"mp4", "webm", "mov", "m4v"},
        MAX_VIDEO_BYTES,
    )


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
        return {"site": {}, "nav_links": []}


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


def _matches(query_str, *texts):
    if not query_str:
        return False
    q = _normalize(query_str)
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
    grid     = all_projects[:6]

    return render_template(
        "index.html",
        carousel_projects=carousel,
        grid_projects=grid,
        featured_video=fetch_featured_video(),
        custom_types=fetch_custom_types(),
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
    return render_template(
        "project_detail.html",
        project=project,
        images=fetch_project_images(project["id"]),
        related=fetch_projects(category=project["category"])[:3],
        max_images=MAX_PROJECT_IMAGES,
    )


@app.route("/residentials")
def residentials():
    return render_template(
        "projects.html",
        projects=fetch_projects(category="residential"),
        active_category="residential",
        active_custom_type=None,
        page_heading=None,
        page_sub=None,
        custom_types=fetch_custom_types(),
    )


@app.route("/commercial")
def commercial():
    return render_template(
        "projects.html",
        projects=fetch_projects(category="commercial"),
        active_category="commercial",
        active_custom_type=None,
        page_heading=None,
        page_sub=None,
        custom_types=fetch_custom_types(),
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
                insert_row("nh_inquiries", {
                    "kind": "contact", "name": name, "email": email,
                    "phone": phone, "subject": subject, "message": message,
                })
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
                insert_row("nh_inquiries", {
                    "kind": "booking", "name": name, "email": email,
                    "phone": phone, "message": message,
                    "preferred_date": preferred_date,
                })
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
        if pwd == ADMIN_PASSWORD:
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
            row = query(f"SELECT COUNT(*) AS n FROM {table}", one=True)
            return row["n"] if row else 0
        except Exception:
            return 0
    stats = {
        "projects":   count("nh_projects"),
        "videos":     count("nh_videos"),
        "gallery":    count("nh_gallery_images"),
        "inquiries":  count("nh_inquiries"),
        "nav":        count("nh_nav_links"),
        "types":      count("nh_property_types"),
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
                        url = save_image(request.files[file_field], "nh-images")
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
            for r in rows:
                execute(
                    "INSERT OR REPLACE INTO nh_site_content (key, value) VALUES (?, ?)",
                    (r["key"], r["value"]),
                )
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
    return render_template("update/property_types.html", types=fetch_property_types())


@app.route("/update/property-types/new", methods=["POST"])
@login_required
def update_property_type_new():
    label = (request.form.get("label") or "").strip()
    order = request.form.get("sort_order", 99, type=int)
    if not label:
        flash("Type name is required.", "error")
        return redirect(url_for("update_property_types"))
    try:
        existing = query(
            "SELECT id FROM nh_property_types WHERE LOWER(label) = LOWER(?) LIMIT 1",
            (label,), one=True
        )
        if existing:
            flash("That type already exists.", "error")
            return redirect(url_for("update_property_types"))
        insert_row("nh_property_types", {
            "label": label, "sort_order": order, "is_active": 1,
        })
        flash("Type added.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_property_types"))


@app.route("/update/property-types/edit/<int:tid>", methods=["POST"])
@login_required
def update_property_type_edit(tid):
    label  = (request.form.get("label") or "").strip()
    order  = request.form.get("sort_order", 99, type=int)
    active = 1 if request.form.get("is_active") == "on" else 0
    if not label:
        flash("Type name is required.", "error")
        return redirect(url_for("update_property_types"))
    try:
        old = query("SELECT label FROM nh_property_types WHERE id = ? LIMIT 1",
                    (tid,), one=True)
        old_label = (old or {}).get("label", "")
        update_row("nh_property_types", {
            "label": label, "sort_order": order, "is_active": active,
        }, "id", tid)
        if old_label and old_label != label:
            execute(
                "UPDATE nh_projects SET custom_type = ? WHERE LOWER(custom_type) = LOWER(?)",
                (label, old_label)
            )
        flash("Type updated.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_property_types"))


@app.route("/update/property-types/delete/<int:tid>", methods=["POST"])
@login_required
def update_property_type_delete(tid):
    try:
        execute("DELETE FROM nh_property_types WHERE id = ?", (tid,))
        flash("Type deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_property_types"))


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
    return render_template(
        "update/project_form.html",
        project=None,
        property_types=fetch_property_types(only_active=True),
        gallery_images=[],
        max_images=MAX_PROJECT_IMAGES,
        max_video_mb=MAX_PROJECT_VIDEO_BYTES // (1024 * 1024),
    )


@app.route("/update/projects/edit/<int:pid>", methods=["GET", "POST"])
@login_required
def update_project_edit(pid):
    project = query("SELECT * FROM nh_projects WHERE id = ? LIMIT 1",
                    (pid,), one=True)
    if not project:
        abort(404)
    if request.method == "POST":
        return _save_project(project)
    return render_template(
        "update/project_form.html",
        project=project,
        property_types=fetch_property_types(only_active=True),
        gallery_images=fetch_project_images(pid),
        max_images=MAX_PROJECT_IMAGES,
        max_video_mb=MAX_PROJECT_VIDEO_BYTES // (1024 * 1024),
    )


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
    featured = 1 if request.form.get("featured") == "on" else 0

    video_description = (request.form.get("video_description") or "").strip()

    image_uploaded = None
    if "image_file" in request.files and request.files["image_file"].filename:
        image_uploaded = save_image(request.files["image_file"], "nh-images")
        if not image_uploaded:
            flash(f"Card image upload failed — check format/size (max "
                  f"{MAX_IMAGE_BYTES // (1024*1024)}MB).", "error")

    hero_uploaded = None
    if "hero_file" in request.files and request.files["hero_file"].filename:
        hero_uploaded = save_image(request.files["hero_file"], "nh-images")
        if not hero_uploaded:
            flash(f"Hero image upload failed — check format/size (max "
                  f"{MAX_IMAGE_BYTES // (1024*1024)}MB).", "error")

    video_uploaded = None
    if "video_file" in request.files and request.files["video_file"].filename:
        video_uploaded = save_video(request.files["video_file"])
        if not video_uploaded:
            flash(f"Video upload failed — check format/size (max "
                  f"{MAX_VIDEO_BYTES // (1024*1024)}MB).", "error")

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
        "video": video, "video_description": video_description,
        "featured": featured,
    }

    try:
        if project:
            update_row("nh_projects", payload, "id", project["id"])
            flash("Property updated.", "success")
        else:
            payload["sort_order"] = 99
            insert_row("nh_projects", payload)
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
        # Clean up gallery files first
        for img in fetch_project_images(pid):
            if img.get("image_url"):
                delete_local_upload(img["image_url"])
        execute("DELETE FROM nh_project_images WHERE project_id = ?", (pid,))
        execute("DELETE FROM nh_projects WHERE id = ?", (pid,))
        flash("Property deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_projects"))


# ─────────────────────────────────────────────────────────
# ADMIN — PROJECT GALLERY
# ─────────────────────────────────────────────────────────
@app.route("/update/projects/<int:pid>/gallery/add", methods=["POST"])
@login_required
def update_project_gallery_add(pid):
    project = query("SELECT * FROM nh_projects WHERE id = ? LIMIT 1",
                    (pid,), one=True)
    if not project:
        abort(404)

    existing = fetch_project_images(pid)
    if len(existing) >= MAX_PROJECT_IMAGES:
        flash(f"Maximum of {MAX_PROJECT_IMAGES} images per project.", "error")
        return redirect(url_for("update_project_edit", pid=pid))

    file = request.files.get("gallery_image")
    desc = (request.form.get("gallery_description") or "").strip()

    if not file or not file.filename:
        flash("Please choose an image file.", "error")
        return redirect(url_for("update_project_edit", pid=pid))

    url = save_image(file, "nh-images")
    if not url:
        flash(f"Invalid image or exceeds {MAX_IMAGE_BYTES // (1024*1024)}MB limit.", "error")
        return redirect(url_for("update_project_edit", pid=pid))

    try:
        insert_row("nh_project_images", {
            "project_id":  pid,
            "image_url":   url,
            "description": desc,
            "sort_order":  len(existing) + 1,
        })
        flash("Image added to gallery.", "success")
    except Exception as e:
        print("gallery add error:", e)
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_project_edit", pid=pid))


@app.route("/update/projects/gallery/<int:img_id>/delete", methods=["POST"])
@login_required
def update_project_gallery_delete(img_id):
    try:
        row = query(
            "SELECT image_url, project_id FROM nh_project_images WHERE id = ? LIMIT 1",
            (img_id,), one=True
        )
        if row:
            pid = row["project_id"]
            if row["image_url"]:
                delete_local_upload(row["image_url"])
            execute("DELETE FROM nh_project_images WHERE id = ?", (img_id,))
            flash("Gallery image deleted.", "success")
            return redirect(url_for("update_project_edit", pid=pid))
    except Exception as e:
        print("gallery delete error:", e)
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_projects"))


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

    featured = 1 if request.form.get("is_featured") == "on" else 0
    try:
        if featured:
            execute("UPDATE nh_videos SET is_featured = 0")
        insert_row("nh_videos", {
            "title": title, "description": desc, "filename": url,
            "is_featured": featured, "sort_order": len(existing) + 1,
        })
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
    featured = 1 if request.form.get("is_featured") == "on" else 0
    try:
        if featured:
            execute("UPDATE nh_videos SET is_featured = 0 WHERE id != ?", (vid,))
        update_row("nh_videos", {
            "title": title, "description": desc, "is_featured": featured,
        }, "id", vid)
        flash("Video updated.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_videos"))


@app.route("/update/videos/delete/<int:vid>", methods=["POST"])
@login_required
def update_video_delete(vid):
    try:
        row = query("SELECT filename FROM nh_videos WHERE id = ? LIMIT 1",
                    (vid,), one=True)
        filename = (row or {}).get("filename", "")
        if filename:
            delete_local_upload(filename)
        execute("DELETE FROM nh_videos WHERE id = ?", (vid,))
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
    url   = save_image(file, "nh-gallery")
    if not url:
        flash("Invalid image or exceeds size limit.", "error")
        return redirect(url_for("update_gallery"))
    try:
        insert_row("nh_gallery_images", {
            "title": title, "filename": url, "source": "upload", "sort_order": 99,
        })
        flash("Image uploaded.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_gallery"))


@app.route("/update/gallery/delete/<int:img_id>", methods=["POST"])
@login_required
def update_gallery_delete(img_id):
    try:
        row = query("SELECT filename FROM nh_gallery_images WHERE id = ? LIMIT 1",
                    (img_id,), one=True)
        url = (row or {}).get("filename", "")
        if url:
            delete_local_upload(url)
        execute("DELETE FROM nh_gallery_images WHERE id = ?", (img_id,))
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
        links = query("SELECT * FROM nh_nav_links ORDER BY sort_order ASC, id ASC")
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
            insert_row("nh_nav_links", {
                "label": label, "url": url, "sort_order": order,
                "is_locked": 0, "visible": 1,
            })
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
        row = query("SELECT * FROM nh_nav_links WHERE id = ? LIMIT 1",
                    (lid,), one=True)
        if not row:
            abort(404)
        if row.get("is_locked"):
            flash("This link is locked.", "error")
            return redirect(url_for("update_nav"))
        update_row("nh_nav_links", {
            "label": (request.form.get("label") or "").strip(),
            "url":   (request.form.get("url") or "").strip(),
            "sort_order": request.form.get("sort_order", row["sort_order"], type=int),
        }, "id", lid)
        flash("Nav link updated.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_nav"))


@app.route("/update/nav/delete/<int:lid>", methods=["POST"])
@login_required
def update_nav_delete(lid):
    try:
        row = query("SELECT is_locked FROM nh_nav_links WHERE id = ? LIMIT 1",
                    (lid,), one=True)
        if (row or {}).get("is_locked"):
            flash("This link is locked.", "error")
            return redirect(url_for("update_nav"))
        execute("DELETE FROM nh_nav_links WHERE id = ?", (lid,))
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
        inquiries = query("SELECT * FROM nh_inquiries ORDER BY id DESC")
    except Exception:
        inquiries = []
    return render_template("update/inquiries.html", inquiries=inquiries)


@app.route("/update/inquiries/delete/<int:iid>", methods=["POST"])
@login_required
def update_inquiry_delete(iid):
    try:
        execute("DELETE FROM nh_inquiries WHERE id = ?", (iid,))
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