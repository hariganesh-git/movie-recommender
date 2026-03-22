import streamlit as st
import pandas as pd
import pickle
import difflib
import requests
import urllib.parse
import os
import gdown



url = "https://drive.google.com/uc?id=1iAMTPxBZ9aQuzXseuD0k2P4ymiq8V-LM"
output = "cosine_sim.pkl"

if not os.path.exists(output):
    gdown.download(url, output, quiet=False)

model = pickle.load(open('cosine_sim.pkl', 'rb'))

st.markdown("""
<style>

/* Entire app background */
html, body, [class*="css"]  {
    background-color: #000000 !important;
    color: white !important;
}

/* Main container */
[data-testid="stAppViewContainer"] {
    background-color: #000000 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #000000 !important;
}

/* Text input / selectbox */
div[data-baseweb="select"] > div {
    background-color: #1c1f26 !important;
    color: white !important;
}

/* Dropdown options */
ul {
    background-color: #1c1f26 !important;
    color: white !important;
}

/* Titles */
h1, h2, h3, h4, h5, h6, p {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* Selectbox main box (closed state) */
div[data-baseweb="select"] > div {
    background-color: white !important;
    color: black !important;
    border-radius: 8px !important;
}

/* Selected value text */
div[data-baseweb="select"] span {
    color: black !important;
}

/* Dropdown menu */
ul[role="listbox"] {
    background-color: white !important;
}

/* Each option */
li[role="option"] {
    background-color: white !important;
    color: black !important;
}

/* Hover effect */
li[role="option"]:hover {
    background-color: #f0f0f0 !important;
    color: black !important;
}

</style>
""", unsafe_allow_html=True)

# ------------------ CONFIG ------------------ #
st.set_page_config(page_title="Movie Recommender By Hari Ganesh", page_icon="🎬", layout="wide")



API_KEY = os.getenv("TMDB_API_KEY") or st.secrets.get("TMDB_API_KEY")

# ------------------ LOAD DATA ------------------ #
df = pickle.load(open("movies.pkl", "rb"))
cosine_sim = pickle.load(open("cosine_sim.pkl", "rb"))

df["title_lower"] = df["title"].str.lower()
indices = pd.Series(df.index, index=df["title_lower"]).drop_duplicates()

# ------------------ POSTER FUNCTION ------------------ #
@st.cache_data
def fetch_poster(movie_title):
    base_url = "https://api.themoviedb.org/3/search/movie"

    try:
        query = urllib.parse.quote(movie_title.split("(")[0])

        url = f"{base_url}?api_key={API_KEY}&query={query}"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("results") and len(data["results"]) > 0:
            for movie in data["results"]:
                if movie.get("poster_path"):
                    return "https://image.tmdb.org/t/p/w500" + movie["poster_path"]

    except Exception as e:
        print("Error:", e)

    # ✅ ALWAYS RETURN VALID IMAGE (IMPORTANT FIX)
    return "https://via.placeholder.com/300x450.png?text=No+Image"

# ------------------ RECOMMEND ------------------ #
def recommend(title, num_recommendations=3):
    title = title.lower()

    if title not in indices:
        matches = difflib.get_close_matches(title, indices.index, n=1, cutoff=0.6)
        if matches:
            return f"❌ Movie not found. Did you mean '{matches[0]}'?"
        return "❌ Movie not found in dataset"

    idx = indices[title]

    similarity_scores = list(enumerate(cosine_sim[idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    seen = set()
    filtered = []

    for i, _ in similarity_scores[1:]:
        movie_title = df.iloc[i]["title"]
        if movie_title not in seen:
            seen.add(movie_title)
            filtered.append(i)
        if len(filtered) == num_recommendations:
            break

    return df.iloc[filtered]

# ------------------ CSS ------------------ #
st.markdown("""
<style>
body {
    background-color: white;
}

/* Title */
.title {
    text-align: center;
    font-size: 55px;
    color: #E50914;
    font-weight: bold;
}

/* Selectbox styling */
div[data-baseweb="select"] > div {
    background-color: white !important;
    color: black !important;
    border-radius: 8px !important;
}

/* Movie card */
.movie-card {
    background-color: #1c1f26;
    padding: 8px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------ #
st.markdown('<div class="title">🎬 HG Movie Recommender</div>', unsafe_allow_html=True)

# ------------------ NETFLIX STYLE SEARCH ------------------ #
search = st.selectbox(
    "🔍 Search for a movie",
    [""] + sorted(df["title"].tolist()),
    index=0
)

# ------------------ SHOW RECOMMENDATIONS ------------------ #
if search:
    result = recommend(search)

    if isinstance(result, str):
        st.error(result)
    else:
        st.subheader("🎯 Top Picks For You")

        cols = st.columns(3)  # 🔥 more columns = smaller images

        for i, row in enumerate(result.itertuples()):
            with cols[i % 3]:

                poster = fetch_poster(row.title)

                st.image(poster, use_container_width=True)  
               

                st.markdown(f"""
<p style='text-align:center; font-weight:bold; font-size:14px; color:white;'>
{row.title}
</p>
""", unsafe_allow_html=True)
