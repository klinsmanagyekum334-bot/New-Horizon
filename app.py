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

# ============================================================
# PRODUCTION SESSION & PROXY CONFIG
# ============================================================
app.config["SESSION_COOKIE_SECURE"]   = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1, x_proto=1, x_host=1, x_prefix=1
)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================
# SITE SCHEMA
# ============================================================
SITE_SCHEMA = [
    {
        "section": "Branding",
        "icon": "fa-solid fa-tag",
        "fields": [
            {"key": "brand_name",   "label": "Brand Name",         "type": "text",  "default": "New Horizon Coopers Limited"},
            {"key": "brand_new",    "label": "Brand Word 1 (dark)", "type": "text",  "default": "NEW"},
            {"key": "brand_horizon","label": "Brand Word 2 (orange)","type":"text",  "default": "HORIZON"},
            {"key": "brand_suffix", "label": "Brand Suffix (small)", "type": "text", "default": "Coopers Limited"},
            {"key": "logo_path",    "label": "Site Logo",            "type": "image", "default": ""},
        ],
    },
    {
        "section": "Hero Section",
        "icon": "fa-solid fa-house-chimney",
        "fields": [
            {"key": "hero_title_l1", "label": "Hero Title — Line 1",    "type": "text",  "default": "Plan"},
            {"key": "hero_title_l2", "label": "Hero Title — Line 2",    "type": "text",  "default": "A perfect"},
            {"key": "hero_title_l3", "label": "Hero Title — Line 3",    "type": "text",  "default": "Home for"},
            {"key": "hero_title_l4", "label": "Hero Title — Line 4",    "type": "text",  "default": "Your family"},
            {"key": "hero_subtitle", "label": "Hero Subtitle",          "type": "text",  "default": "Most trusted Agency in Ghana"},
            {"key": "hero_image",    "label": "Hero Background Image",  "type": "image", "default": ""},
            {"key": "hero_cta_text", "label": "Hero Button Text",       "type": "text",  "default": "Explore Projects"},
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
            {"key": "footer_blurb", "label": "Footer Blurb", "type": "textarea",
             "default": "New Horizon Coopers Limited — building sustainable, modern communities across Ghana since 2017."},
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


def fetch_projects(category=None, featured_only=False):
    try:
        q = supabase.table("nh_projects").select("*")
        if category:
            q = q.eq("category", category)
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
    """Upload file to Supabase Storage. Returns public URL or None."""
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


# ============================================================
# GLOBAL TEMPLATE CONTEXT
# Makes `site` and `nav_links` available in EVERY template
# (including all /update/* pages that were crashing with 500)
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
    )


@app.route("/videos")
def videos_page():
    return render_template("videos.html", videos=fetch_videos())


@app.route("/gallery")
def gallery_page():
    return render_template("gallery.html", images=fetch_gallery())


@app.route("/projects")
def projects():
    return render_template("projects.html",
                           projects=fetch_projects(), active_category=None)


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
                           active_category="residential")


@app.route("/commercial")
def commercial():
    return render_template("projects.html",
                           projects=fetch_projects(category="commercial"),
                           active_category="commercial")


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
                    price_str, str(p.get("price_from","")), p.get("status","")):
            results.append({"type": "project", "title": p["name"],
                            "subtitle": f"{p.get('location','')} · from ${price_str}",
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
        print(f"[LOGIN] POST received, pwd_len={len(pwd)}, match={pwd == ADMIN_PASSWORD}")
        if pwd == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            session.permanent = True
            print(f"[LOGIN] Session set: {dict(session)}")
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
    print(f"[DASHBOARD] Session: {dict(session)}")
    def count(table):
        try:
            res = supabase.table(table).select("id").execute()
            return len(res.data or [])
        except Exception:
            return 0
    stats = {
        "projects":  count("nh_projects"),
        "videos":    count("nh_videos"),
        "gallery":   count("nh_gallery_images"),
        "inquiries": count("nh_inquiries"),
        "nav":       count("nh_nav_links"),
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
    return render_template("update/project_form.html", project=None)


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
    return render_template("update/project_form.html", project=project)


def _save_project(project):
    name     = (request.form.get("name") or "").strip()
    slug     = (request.form.get("slug") or "").strip().lower().replace(" ", "-")
    category = (request.form.get("category") or "residential").strip()
    status   = (request.form.get("status") or "ongoing").strip()
    short_desc = (request.form.get("short_desc") or "").strip()
    long_desc  = (request.form.get("long_desc") or "").strip()
    location   = (request.form.get("location") or "").strip()
    units      = (request.form.get("units") or "").strip()
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

    image = image_uploaded or request.form.get("image_url","").strip() or \
            (project["image"] if project else "")
    hero  = hero_uploaded  or request.form.get("hero_url","").strip() or \
            (project.get("hero_image") if project else "")

    payload = {
        "name": name, "slug": slug, "category": category, "status": status,
        "short_desc": short_desc, "long_desc": long_desc,
        "location": location, "units": units,
        "price_from": price_from, "image": image, "hero_image": hero,
        "featured": featured,
    }

    try:
        if project:
            supabase.table("nh_projects").update(payload).eq("id", project["id"]).execute()
            flash("Project updated.", "success")
        else:
            payload["sort_order"] = 99
            supabase.table("nh_projects").insert(payload).execute()
            flash("Project created.", "success")
    except Exception as e:
        print("save project error:", e)
        flash(f"Error: {e}", "error")
    return redirect(url_for("update_projects"))


@app.route("/update/projects/delete/<int:pid>", methods=["POST"])
@login_required
def update_project_delete(pid):
    try:
        supabase.table("nh_projects").delete().eq("id", pid).execute()
        flash("Project deleted.", "success")
    except Exception as e:
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
        if filename and "/storage/v1/object/public/nh-videos/" in filename:
            storage_name = filename.rsplit("/", 1)[-1]
            supabase.storage.from_(BUCKET_VIDEOS).remove([storage_name])
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
        if url and "/storage/v1/object/public/nh-gallery/" in url:
            name = url.rsplit("/", 1)[-1]
            supabase.storage.from_(BUCKET_GALLERY).remove([name])
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
                "label": label, "url": url, "sort_order": order, "is_locked": False,
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
