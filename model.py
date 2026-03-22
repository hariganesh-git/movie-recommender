import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("netflix.csv")
df.head()

df.drop("Unnamed: 0",axis=1,inplace=True)

df.info()

df["content"] = (df["genre"] + " " + df["description"] + " " + df["director"] + " " + df["cast"])

tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(df["content"])

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

pickle.dump(df, open("movies.pkl", "wb"))
pickle.dump(cosine_sim, open("cosine_sim.pkl", "wb"))

print("✅ Model built and saved!")