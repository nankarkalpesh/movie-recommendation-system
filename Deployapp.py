import streamlit as st
import pickle
import requests
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    _favicon = Image.open("favicon.png")
except:
    _favicon = "🎥"

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────
#  GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* ══════════════════════════════════════════════
   CSS VARIABLES — single source of truth
══════════════════════════════════════════════ */
:root{
    --page-pad-x : clamp(24px, 5vw, 96px);
    --page-pad-x-md : clamp(16px, 3vw, 48px);
    --page-pad-x-sm : 14px;

    --gap-card    : clamp(10px, 1.2vw, 18px);
    --gap-row     : clamp(20px, 2.5vw, 36px);

    --radius-card : 12px;
    --radius-btn  : 10px;

    --c-bg        : #0a0a0f;
    --c-surface   : #0d1020;
    --c-border    : #1a1f38;
    --c-border-hi : #2251c5;
    --c-accent    : #5b8def;
    --c-accent2   : #93c5fd;
    --c-text      : #d8e6ff;
    --c-muted     : #4a5e88;
    --c-dim       : #2a3a60;

    --transition  : 0.25s cubic-bezier(0.4,0,0.2,1);
}

/* ══════════════════════════════════════════════
   RESET & STREAMLIT OVERRIDES
══════════════════════════════════════════════ */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}

html,body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"],
section[data-testid="stMain"],
section[data-testid="stMain"]>div,
section[data-testid="stMain"]>div>div,
.main,.block-container,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stMarkdownContainer"]{
    background:var(--c-bg) !important;
    font-family:'Outfit',sans-serif !important;
    max-width:100% !important;
    width:100% !important;
    padding-left:0 !important;
    padding-right:0 !important;
}
section[data-testid="stMain"]>div{padding-top:0 !important;}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
#MainMenu,footer,header{display:none !important;}

/* ══════════════════════════════════════════════
   NAVBAR
══════════════════════════════════════════════ */
.navbar{
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:0 var(--page-pad-x);
    height:64px;
    background:rgba(10,10,15,0.97);
    border-bottom:1px solid rgba(91,141,239,0.13);
    position:sticky;top:0;z-index:1000;
    backdrop-filter:blur(14px);
    -webkit-backdrop-filter:blur(14px);
}
.nav-logo{
    font-size:clamp(13px,1.4vw,19px);
    font-weight:800;
    background:linear-gradient(120deg,#5b8def,#93c5fd);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    letter-spacing:-0.4px;
    white-space:nowrap;
}
.nav-tagline{
    font-size:clamp(9px,0.75vw,11px);
    letter-spacing:3px;
    text-transform:uppercase;
    color:var(--c-dim);
}

/* ══════════════════════════════════════════════
   HERO
══════════════════════════════════════════════ */
.hero{
    text-align:center;
    padding:clamp(32px,5vw,72px) var(--page-pad-x) clamp(20px,3vw,40px);
    background:radial-gradient(ellipse 80% 50% at 50% 0%,rgba(34,81,197,0.16) 0%,transparent 70%);
}
.hero h1{
    font-size:clamp(24px,4.5vw,56px);
    font-weight:800;
    color:#fff;
    line-height:1.1;
    letter-spacing:-1.5px;
    margin-bottom:clamp(8px,1vw,14px);
}
.hero h1 span{
    background:linear-gradient(120deg,#5b8def,#93c5fd);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.hero p{
    font-size:clamp(13px,1.1vw,17px);
    color:var(--c-muted);
    margin-bottom:clamp(20px,2.5vw,32px);
    line-height:1.6;
}

/* ══════════════════════════════════════════════
   SELECTBOX
══════════════════════════════════════════════ */
div[data-testid="stSelectbox"] label{display:none !important;}
div[data-testid="stSelectbox"]>div>div{
    background:#0d1228 !important;
    border:1.5px solid #1e2d50 !important;
    border-radius:var(--radius-btn) !important;
    color:var(--c-text) !important;
    font-family:'Outfit',sans-serif !important;
    font-size:clamp(13px,1.2vw,16px) !important;
    min-height:52px !important;
    transition:border-color var(--transition),box-shadow var(--transition) !important;
}
div[data-testid="stSelectbox"]>div>div:focus-within{
    border-color:#4477dd !important;
    box-shadow:0 0 0 3px rgba(68,119,221,0.18) !important;
}

/* ══════════════════════════════════════════════
   BUTTONS — shared base
══════════════════════════════════════════════ */
div.stButton>button{
    font-family:'Outfit',sans-serif !important;
    transition:all var(--transition) !important;
    outline:none !important;
    cursor:pointer !important;
}
div.stButton>button:focus{outline:none !important;box-shadow:none !important;}

/* Find Similar Movies */
.btn-find div.stButton>button{
    background:linear-gradient(135deg,#2251c5,#3a6ee8) !important;
    color:#fff !important;
    border:none !important;
    border-radius:var(--radius-btn) !important;
    font-size:clamp(13px,1.2vw,16px) !important;
    font-weight:700 !important;
    padding:clamp(12px,1.2vw,16px) 0 !important;
    width:100% !important;
    box-shadow:0 4px 24px rgba(34,81,197,0.50) !important;
    letter-spacing:0.4px !important;
}
.btn-find div.stButton>button:hover{
    background:linear-gradient(135deg,#1a3fa8,#2d5bc8) !important;
    transform:translateY(-2px) !important;
    box-shadow:0 8px 28px rgba(34,81,197,0.65) !important;
}

/* View Details */
.vd-btn-wrap{margin-top:6px;}
.vd-btn-wrap div.stButton>button{
    background:#0f1626 !important;
    color:#7eb8ff !important;
    border:1px solid #1e356e !important;
    border-radius:0 0 var(--radius-card) var(--radius-card) !important;
    font-size:clamp(9px,0.82vw,12px) !important;
    font-weight:600 !important;
    padding:clamp(7px,0.7vw,10px) 0 !important;
    width:100% !important;
    letter-spacing:0.5px !important;
    transition:background var(--transition),color var(--transition),border-color var(--transition) !important;
}
.vd-btn-wrap div.stButton>button:hover{
    background:#172040 !important;
    color:#bfdbfe !important;
    border-color:#4477dd !important;
    transform:none !important;
}

/* Show More */
.btn-more-wrap{
    margin:clamp(24px,3vw,40px) auto 0;
    max-width:260px;
}
.btn-more-wrap div.stButton>button{
    background:transparent !important;
    color:#7eb8ff !important;
    border:1.5px solid #2251c5 !important;
    border-radius:var(--radius-btn) !important;
    font-size:clamp(12px,1.1vw,15px) !important;
    font-weight:600 !important;
    padding:clamp(11px,1.1vw,14px) 0 !important;
    width:100% !important;
    letter-spacing:0.4px !important;
}
.btn-more-wrap div.stButton>button:hover{
    background:rgba(34,81,197,0.15) !important;
    border-color:#5b8def !important;
    color:#bfdbfe !important;
    transform:translateY(-2px) !important;
    box-shadow:0 4px 20px rgba(34,81,197,0.25) !important;
}

/* Back */
.btn-back-wrap{margin-bottom:28px;}
.btn-back-wrap div.stButton>button{
    background:#0d1228 !important;
    color:#8aaac8 !important;
    border:1px solid #1e2d50 !important;
    border-radius:8px !important;
    font-size:clamp(11px,1vw,14px) !important;
    font-weight:500 !important;
    padding:10px 24px !important;
    width:auto !important;
}
.btn-back-wrap div.stButton>button:hover{
    background:#111a35 !important;
    color:#d0e4ff !important;
    border-color:#2d4a80 !important;
    transform:none !important;
}

/* ══════════════════════════════════════════════
   SECTION HEADER
══════════════════════════════════════════════ */
.sec-wrap{
    padding:clamp(20px,2.5vw,36px) var(--page-pad-x) clamp(14px,1.8vw,24px);
}
.sec-label{
    font-size:clamp(9px,0.72vw,11px);
    letter-spacing:3.5px;
    text-transform:uppercase;
    color:var(--c-dim);
    margin-bottom:6px;
    font-weight:600;
}
.sec-title{
    font-size:clamp(18px,2vw,28px);
    font-weight:700;
    color:var(--c-text);
    line-height:1.2;
}
.sec-title em{font-style:normal;color:var(--c-accent);}
.hdivider{
    border:none;
    border-top:1px solid #0e1528;
    margin:0 var(--page-pad-x);
}

/* ══════════════════════════════════════════════
   CARD GRID
══════════════════════════════════════════════ */
.cards-outer{
    padding:0 var(--page-pad-x) clamp(8px,1vw,16px);
    box-sizing:border-box;
    width:100%;
    overflow:visible;
}
.cards-outer [data-testid="stHorizontalBlock"]{
    gap:var(--gap-card) !important;
    align-items:stretch !important;
    flex-wrap:nowrap !important;
    width:100% !important;
}
.cards-outer [data-testid="stColumn"]{
    padding:0 !important;
    min-width:0 !important;
    flex:1 1 0 !important;
    max-width:none !important;
}
.card-row-spacer{height:var(--gap-row);}

/* ══════════════════════════════════════════════
   MOVIE CARD
══════════════════════════════════════════════ */
.mcard-wrap{
    position:relative;
    z-index:1;
    transition:z-index 0s 0.3s;
}
.mcard-wrap:hover{z-index:200;transition:z-index 0s 0s;}

.mcard{
    border-radius:var(--radius-card);
    overflow:hidden;
    background:var(--c-surface);
    border:1px solid var(--c-border);
    cursor:pointer;
    transition:
        transform 0.28s cubic-bezier(0.34,1.3,0.64,1),
        box-shadow 0.28s ease,
        border-color 0.22s ease,
        border-radius 0.28s ease;
}
.mcard-wrap:hover .mcard{
    transform:scale(1.06) translateY(-6px);
    box-shadow:0 28px 60px rgba(0,0,0,0.88),0 0 0 1px rgba(34,81,197,0.3);
    border-color:var(--c-border-hi);
    border-radius:var(--radius-card) var(--radius-card) 0 0;
}

.mcard-img{
    position:relative;
    width:100%;
    aspect-ratio:2/3;
    overflow:hidden;
    max-height:280px;
}
.mcard-img img{
    width:100%;height:100%;
    object-fit:cover;display:block;
    transition:filter 0.28s ease,transform 0.32s ease;
}
.mcard-wrap:hover .mcard-img img{
    filter:brightness(0.45);
    transform:scale(1.04);
}

.mcard-overlay{
    position:absolute;inset:0;
    background:linear-gradient(
        0deg,
        rgba(8,8,14,0.97) 0%,
        rgba(8,8,14,0.55) 32%,
        transparent 62%
    );
    display:flex;flex-direction:column;justify-content:flex-end;
    padding:clamp(8px,0.8vw,12px);
}
.mcard-title{
    font-size:clamp(10px,0.95vw,14px);
    font-weight:700;
    color:#fff;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
    line-height:1.3;
    margin-bottom:2px;
}
.mcard-rating{
    color:var(--c-accent2);
    font-size:clamp(8px,0.75vw,11px);
    margin-top:2px;
    font-weight:600;
    letter-spacing:0.3px;
}
.mcard-genres{margin-top:5px;display:flex;flex-wrap:wrap;gap:4px;}
.mcard-tag{
    background:rgba(34,81,197,0.5);
    color:#c8dcff;
    border:1px solid rgba(91,141,239,0.35);
    border-radius:4px;
    padding:2px 6px;
    font-size:clamp(7px,0.62vw,10px);
    font-weight:600;
    letter-spacing:0.2px;
}

/* ══════════════════════════════════════════════
   HOVER POPUP
══════════════════════════════════════════════ */
.mcard-popup{
    position:absolute;top:100%;left:50%;
    transform:translateX(-50%) scaleX(1.06);
    transform-origin:top center;
    width:100%;
    background:#111827;
    border:1px solid var(--c-border-hi);border-top:none;
    border-radius:0 0 var(--radius-card) var(--radius-card);
    box-shadow:0 24px 52px rgba(0,0,0,0.95);
    padding:12px 14px;
    opacity:0;pointer-events:none;
    transition:opacity 0.2s ease 0.06s;
    z-index:201;
}
.mcard-wrap:hover .mcard-popup{opacity:1;pointer-events:auto;}
.pop-title{
    font-size:clamp(10px,1vw,13px);font-weight:700;
    color:#e8f0ff;margin-bottom:4px;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}
.pop-meta{font-size:clamp(8px,0.72vw,10px);color:#4a6a8a;margin-bottom:6px;line-height:1.5;}
.pop-plot{
    font-size:clamp(8px,0.72vw,10px);color:#7a9abf;
    line-height:1.6;font-weight:300;
    display:-webkit-box;-webkit-line-clamp:3;
    -webkit-box-orient:vertical;overflow:hidden;
}

/* ══════════════════════════════════════════════
   SPINNER
══════════════════════════════════════════════ */
div[data-testid="stSpinner"]{
    position:fixed !important;top:50% !important;left:50% !important;
    transform:translate(-50%,-50%) !important;z-index:9999 !important;
    display:flex !important;flex-direction:column !important;
    align-items:center !important;gap:14px !important;
    background:rgba(8,8,14,0.96) !important;
    padding:32px 56px !important;
    border-radius:16px !important;
    border:1px solid #1e2d50 !important;
    backdrop-filter:blur(18px) !important;
    box-shadow:0 24px 64px rgba(0,0,0,0.7) !important;
}
div[data-testid="stSpinner"] p{
    color:#7a9abf !important;font-size:14px !important;
    font-family:'Outfit',sans-serif !important;font-weight:500 !important;margin:0 !important;
}

/* ══════════════════════════════════════════════
   DETAIL PAGE
══════════════════════════════════════════════ */
.det-wrap{
    padding:clamp(20px,3.5vw,52px) var(--page-pad-x) clamp(32px,4vw,64px);
}
.det-h1{
    font-size:clamp(24px,4.5vw,52px);
    font-weight:800;color:#fff;
    letter-spacing:-0.8px;margin-bottom:8px;line-height:1.05;
}
.det-meta{
    color:#3d5070;font-size:clamp(12px,1.05vw,16px);
    margin-bottom:14px;font-weight:500;line-height:1.6;
}
.det-tag{
    display:inline-block;
    background:rgba(34,81,197,0.16);
    color:#93c5fd;
    border:1px solid rgba(91,141,239,0.28);
    border-radius:6px;
    padding:4px 12px;
    font-size:clamp(10px,0.9vw,13px);
    margin:3px;font-weight:600;
}
.det-row{margin-bottom:10px;line-height:1.65;}
.det-lbl{color:#4477dd;font-weight:700;font-size:clamp(11px,1vw,14px);}
.det-val{color:#7a96b8;font-size:clamp(11px,1vw,14px);}
.det-plot{
    font-size:clamp(13px,1.15vw,17px);
    color:#6a88a8;line-height:1.9;
    margin-top:18px;font-weight:300;
    padding-left:18px;border-left:3px solid #2251c5;
}

/* ══════════════════════════════════════════════
   RESPONSIVE — 1200px
══════════════════════════════════════════════ */
@media(max-width:1200px){
    :root{
        --page-pad-x:clamp(20px,4vw,72px);
        --gap-card:clamp(10px,1.1vw,16px);
    }
}

/* ══════════════════════════════════════════════
   RESPONSIVE — 992px  (tablet landscape)
══════════════════════════════════════════════ */
@media(max-width:992px){
    :root{
        --page-pad-x:var(--page-pad-x-md);
        --gap-card:12px;
    }
    .mcard-popup{display:none !important;}
    .mcard-img{max-height:230px;}
    .sec-title{font-size:clamp(16px,2.2vw,22px);}
}

/* ══════════════════════════════════════════════
   RESPONSIVE — 768px  (tablet portrait)
══════════════════════════════════════════════ */
@media(max-width:768px){
    :root{
        --page-pad-x:20px;
        --gap-card:10px;
        --gap-row:20px;
    }
    .cards-outer [data-testid="stHorizontalBlock"]{
        flex-wrap:wrap !important;
    }
    .cards-outer [data-testid="stColumn"]{
        flex:1 1 calc(33.33% - 8px) !important;
        max-width:calc(33.33% - 8px) !important;
    }
    .mcard-img{max-height:220px !important;}
    .navbar{padding:0 20px;}
    .hero{padding:clamp(24px,4vw,48px) 20px clamp(16px,2.5vw,28px);}
    .sec-wrap{padding-left:20px !important;padding-right:20px !important;}
    .hdivider{margin-left:20px !important;margin-right:20px !important;}
    .det-wrap{padding:20px 20px 40px !important;}
}

/* ══════════════════════════════════════════════
   RESPONSIVE — 576px  (mobile)
══════════════════════════════════════════════ */
@media(max-width:576px){
    :root{
        --page-pad-x:14px;
        --gap-card:8px;
        --gap-row:16px;
    }
    .cards-outer [data-testid="stColumn"]{
        flex:1 1 calc(50% - 4px) !important;
        max-width:calc(50% - 4px) !important;
    }
    .mcard-img{max-height:190px !important;}
    .mcard-title{white-space:normal;font-size:10px;}
    .hero h1{letter-spacing:-0.5px;font-size:clamp(20px,7vw,32px);}
    .hero p{font-size:13px;}
    .nav-tagline{display:none;}
    .sec-title{font-size:clamp(15px,4.5vw,20px);}
    .vd-btn-wrap div.stButton>button{font-size:10px !important;padding:6px 0 !important;}
    .det-wrap{padding:14px 14px 32px !important;}
    .btn-more-wrap{max-width:90%;}
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATA & API
# ─────────────────────────────────────────────
@st.cache_resource
def load_data():
    movies     = pickle.load(open("movies.pkl",     "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity

movies, similarity = load_data()
OMDB_KEY = "9b5e7a03"


def fetch_movie_data(title):
    import re
    title = str(title)
    r = {
        "poster": None, "rating": "N/A", "genres": [],
        "plot": "No description available.", "year": "N/A",
        "director": "N/A", "cast": "N/A", "runtime": "N/A",
        "language": "N/A", "awards": "N/A", "country": "N/A", "box_office": "N/A"
    }
    for suffix in [" film", ""]:
        try:
            d = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/"
                f"{requests.utils.quote(title+suffix)}", timeout=3).json()
            if not r["poster"]:
                t = d.get("thumbnail", {}).get("source")
                if t: r["poster"] = t
            if r["plot"] == "No description available.":
                ext = d.get("extract", "")
                if ext and len(ext) > 20:
                    r["plot"] = ext[:300] + ("..." if len(ext) > 300 else "")
            if r["year"] == "N/A":
                yr = re.search(r"\b(19|20)\d{2}\b", d.get("description", ""))
                if yr: r["year"] = yr.group()
            if r["poster"] and r["plot"] != "No description available.": break
        except: pass
    try:
        d = requests.get(
            f"https://www.omdbapi.com/?t={requests.utils.quote(title)}"
            f"&plot=short&apikey={OMDB_KEY}", timeout=3).json()
        if d.get("Response") == "True":
            p = d.get("Poster")
            if p and p != "N/A": r["poster"] = p
            for k, v in [("rating","imdbRating"),("year","Year"),
                         ("director","Director"),("cast","Actors"),
                         ("runtime","Runtime"),("language","Language"),
                         ("awards","Awards"),("country","Country"),
                         ("box_office","BoxOffice")]:
                val = d.get(v, "N/A")
                if val and val != "N/A": r[k] = val
            plot = d.get("Plot", "")
            if plot and plot != "N/A": r["plot"] = plot
            g = d.get("Genre", "")
            if g and g != "N/A": r["genres"] = [x.strip() for x in g.split(",")]
    except: pass
    if not r["poster"]:
        r["poster"] = (f"https://placehold.co/300x450/0d1020/2251c5?text="
                       f"{requests.utils.quote(title)}")
    return r


@st.cache_data(show_spinner=False)
def fetch_movie_data_cached(title: str):
    return fetch_movie_data(title)


def fetch_parallel(titles):
    out = [None] * len(titles)
    with ThreadPoolExecutor(max_workers=30) as ex:
        fmap = {ex.submit(fetch_movie_data, t): i for i, t in enumerate(titles)}
        for f in as_completed(fmap): out[fmap[f]] = f.result()
    return out


@st.cache_data(show_spinner=False)
def recommend(movie, num=30):
    idx    = movies[movies["title"] == movie].index[0]
    top    = sorted(enumerate(similarity[idx]), reverse=True,
                    key=lambda x: x[1])[1:num+1]
    titles = [movies.iloc[i].title for i, _ in top]
    # If fewer than requested, pad with popular movies from the dataset
    if len(titles) < num:
        all_titles = movies["title"].tolist()
        extras = [t for t in all_titles if t != movie and t not in titles]
        titles = titles + extras[:num - len(titles)]
    return titles, fetch_parallel(titles)


# ─────────────────────────────────────────────
#  NAVBAR
# ─────────────────────────────────────────────
NAVBAR = """<div class="navbar">
  <div class="nav-logo">Movie Recommendation System</div>
  <div class="nav-tagline">Discover · Explore · Watch</div>
</div>"""


# ─────────────────────────────────────────────
#  DETAIL PAGE
# ─────────────────────────────────────────────
def detail_page():
    st.markdown(NAVBAR, unsafe_allow_html=True)
    title = st.session_state.selected_detail
    data  = fetch_movie_data_cached(title)

    st.markdown('<div class="det-wrap">', unsafe_allow_html=True)

    # Back button
    st.markdown('<div class="btn-back-wrap" style="margin-bottom:20px">', unsafe_allow_html=True)
    if st.button("← Back to Results", key="back_btn"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Movie info layout
    col_img, col_info = st.columns([1, 2.4], gap="large")

    with col_img:
        st.image(data["poster"], use_container_width=True)

    with col_info:
        st.markdown(f"<div class='det-h1'>{title}</div>", unsafe_allow_html=True)

        # Year · Runtime · Rating
        meta_parts = []
        if data["year"]    != "N/A": meta_parts.append(data["year"])
        if data["runtime"] != "N/A": meta_parts.append(data["runtime"])
        if data["rating"]  != "N/A": meta_parts.append(f"⭐ {data['rating']} IMDb")
        if meta_parts:
            st.markdown(f"<div class='det-meta'>{' &nbsp;·&nbsp; '.join(meta_parts)}</div>",
                        unsafe_allow_html=True)

        # Genre tags
        if data["genres"]:
            tags = "".join([f"<span class='det-tag'>{g}</span>" for g in data["genres"]])
            st.markdown(f"<div style='margin-bottom:14px'>{tags}</div>",
                        unsafe_allow_html=True)

        # Info rows
        for lbl, val in [
            ("Director", data["director"]),
            ("Cast",     data["cast"]),
            ("Language", data["language"]),
            ("Country",  data["country"]),
            ("Box Office", data["box_office"]),
            ("Awards",   data["awards"]),
        ]:
            if val != "N/A":
                st.markdown(
                    f"<div class='det-row'>"
                    f"<span class='det-lbl'>{lbl}:&nbsp;</span>"
                    f"<span class='det-val'>{val}</span></div>",
                    unsafe_allow_html=True)

        # Plot
        st.markdown(f"<div class='det-plot'>{data['plot']}</div>",
                    unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HOME PAGE
# ─────────────────────────────────────────────
def home_page():
    st.markdown(NAVBAR, unsafe_allow_html=True)

    # ── Hero section ──
    st.markdown("""
    <div class="hero">
      <h1>Find Your Next <span>Favourite Film</span></h1>
      <p>Pick a movie you love — we'll find what to watch next</p>
    </div>""", unsafe_allow_html=True)

    # ── Search row ──
    _, sc, _ = st.columns([0.05, 0.9, 0.05])
    with sc:
        selected = st.selectbox("", movies["title"].values,
                                label_visibility="collapsed")

    _, bc, _ = st.columns([0.3, 0.4, 0.3])
    with bc:
        st.markdown('<div class="btn-find">', unsafe_allow_html=True)
        find_clicked = st.button("🎬  Find Similar Movies",
                                 use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if find_clicked:
        st.session_state.recommend_movie = selected
        st.session_state.show_count      = 5
        st.session_state.results         = None

    if "recommend_movie" not in st.session_state:
        return

    # ── Load recommendations ──
    if st.session_state.get("results") is None:
        with st.spinner("Finding movies for you..."):
            names, all_data = recommend(st.session_state.recommend_movie, 30)
        st.session_state.results = (names, all_data)

    names, all_data = st.session_state.results
    show_count = st.session_state.get("show_count", 5)
    vnames     = names[:show_count]
    vdata      = all_data[:show_count]

    # ── Section header ──
    st.markdown('<div class="hdivider"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sec-wrap">
      <div class="sec-label">Recommendations</div>
      <div class="sec-title">Because you liked &nbsp;<em>{st.session_state.recommend_movie}</em></div>
    </div>""", unsafe_allow_html=True)

    # ── Cards + View Details buttons ──────────────────────────────────
    # Render in rows of 5. Each card has a unique key using its global index.
    # ─────────────────────────────────────────────────────────────────
    COLS_PER_ROW = 5
    st.markdown('<div class="cards-outer">', unsafe_allow_html=True)

    for row_start in range(0, len(vnames), COLS_PER_ROW):
        row_titles = vnames[row_start:row_start + COLS_PER_ROW]
        row_data   = vdata[row_start:row_start + COLS_PER_ROW]
        cols = st.columns(COLS_PER_ROW, gap="small")

        for col_idx, (col, title, data) in enumerate(zip(cols, row_titles, row_data)):
            global_idx = row_start + col_idx
            with col:
                safe = (title.replace("&","&amp;").replace('"',"&quot;")
                             .replace("'","&#39;").replace("<","&lt;").replace(">","&gt;"))
                rs   = f"⭐ {data['rating']}" if data["rating"] != "N/A" else ""
                yr   = data["year"]            if data["year"]   != "N/A" else ""
                rt_  = data["runtime"]         if data["runtime"]!= "N/A" else ""
                gt   = "".join([f"<span class='mcard-tag'>{g}</span>"
                                for g in data["genres"][:2]])
                ps   = (data["plot"][:130]+"...") if len(data["plot"])>130 else data["plot"]
                meta = " · ".join(filter(None, [yr, rt_, rs]))

                # Poster card (HTML — hover animation via CSS)
                st.markdown(f"""
<div class="mcard-wrap">
  <div class="mcard">
    <div class="mcard-img">
      <img src="{data['poster']}" alt="{safe}" loading="lazy">
      <div class="mcard-overlay">
        <div class="mcard-title">{safe}</div>
        <div class="mcard-rating">{rs}</div>
        <div class="mcard-genres">{gt}</div>
      </div>
    </div>
  </div>
  <div class="mcard-popup">
    <div class="pop-title">{safe}</div>
    <div class="pop-meta">{meta}</div>
    <div class="pop-plot">{ps}</div>
  </div>
</div>""", unsafe_allow_html=True)

                # View Details button — unique key by global index
                st.markdown('<div class="vd-btn-wrap">', unsafe_allow_html=True)
                if st.button("▶  View Details",
                             key=f"vd_{global_idx}_{show_count}",
                             use_container_width=True):
                    st.session_state.selected_detail = title
                    st.session_state.page = "detail"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # Spacer between rows (not after last row)
        if row_start + COLS_PER_ROW < len(vnames):
            st.markdown('<div class="card-row-spacer"></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # /cards-outer

    # ── Show More ──
    if show_count < len(names):
        st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
        _, mc, _ = st.columns([0.35, 0.3, 0.35])
        with mc:
            st.markdown('<div class="btn-more-wrap">', unsafe_allow_html=True)
            if st.button("Show More", key="show_more", use_container_width=True):
                st.session_state.show_count = min(show_count + 5, len(names))
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="height:32px"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "detail":
    detail_page()
else:
    home_page()