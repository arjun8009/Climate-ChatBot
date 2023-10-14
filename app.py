import streamlit as st
import pandas as pd
from scipy import spatial  # for calculating vector similarities for search
import os
import time
st.set_page_config(layout="wide")

from embeddings import get_excerpts_from_database
from llms import get_llm_output, get_or_set_openai_api_key
from prompts import system_instruction, user_prompt
from utils import display_messages_and_sources, display_sources, load_embeddings_df

st.subheader("Tipping Points Bot", divider='rainbow')

# This function will check if the openai api key is set in the secrets.json file. If not, it will ask the user to enter the api key.
get_or_set_openai_api_key()

# Load the dataframe with the embeddings from the parquet file.
df = load_embeddings_df()

chat_container = st.container()
query = st.chat_input("Ask a question here:")

i = 0
if query:
    df_results = get_excerpts_from_database(query, df, top_n=5) # top_n is the number of excerpts to return from the database for the given query.
    
    excerpts = df_results['strings'].tolist()
    user_prompt = user_prompt.replace("<EXCERPTS>", "\n".join(excerpts))
    user_prompt = user_prompt.replace("<QUESTION>", query)
    
    st.session_state.query = query
    
    # Initialize chat history if it doesn't exist and add system_instruction to it. 
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat_history.append({"role": "system", "content": system_instruction})
    
    # Add user_prompt to chat history and later replace it with query
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    with st.spinner('Thinking...'):
        response = get_llm_output(st.session_state.chat_history, max_tokens=500, temperature=0, model='gpt-3.5-turbo')
    
    # delete user message from the chat history where the role is user, and replace it with the query.
    # This step is needed to avoid the excerpts to be shown in the chat history which takes up a lot of context length.
    for i in range(len(st.session_state.chat_history) - 1, -1, -1):
        if st.session_state.chat_history[i]['role'] == 'user':
            st.session_state.chat_history[i]['content'] = query
            break

    # Add the response from the bot to the chat history.
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Add the query, response and df_results to the source_history.
    if 'source_history' not in st.session_state:
        st.session_state.source_history = []
    st.session_state.source_history.append({'question':query,'response': response, 'df_results': df_results})

with chat_container:
    source_history = st.session_state.get('source_history', [])
    if source_history:
        display_messages_and_sources(source_history)
    else:
        with st.chat_message('assistant'):
            st.markdown("Hi! I'm the TP-Bot. I can answer questions about tipping points. Ask me a question to get started.")
            pass