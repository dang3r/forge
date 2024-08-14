from openai import OpenAI
import pathlib
import pandas as pd

client = OpenAI()


def get_embedding(text, model="text-embedding-3-small"):
    text = text.lower()
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def cosine_similarity(v1, v2):
    num = sum([i1*i2 for i1,i2 in  zip(v1,v2)])
    denom = sum(i**2 for i in v1)**0.5 + sum(i**2 for i in v2)**0.5
    return num / denom




if not pathlib.Path("embeddings.csv").exists():
    df = pd.read_csv("wordlist-eng.txt")
    df["embeddings"] = df["word"].apply(lambda x: get_embedding(x))
    df.to_csv("embeddings.csv")

    ``
