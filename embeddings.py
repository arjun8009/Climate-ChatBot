import openai
import pandas as pd
from scipy import spatial  # for calculating vector similarities for search
import streamlit as st
# search function
def get_excerpts_from_database(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 5
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
        
    # models
    EMBEDDING_MODEL = "text-embedding-ada-002"
    
    query_embedding_response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response["data"][0]["embedding"]
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embeddings"]), row["chunk_number"], row["file_name"])
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses, chunk_numbers, file_names = zip(*strings_and_relatednesses)
    # convert into a dataframe
    df_results = pd.DataFrame({"strings": strings, "relatednesses": relatednesses, "chunk_number": chunk_numbers, "file_name": file_names})

    # sort the dataframe by relatedness (highest to lowest) and return the top_n
    df_results = df_results.sort_values(by=['relatednesses'], ascending=False).head(top_n)

    return df_results