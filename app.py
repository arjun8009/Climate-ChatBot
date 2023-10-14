import streamlit as st
import pandas as pd
from scipy import spatial  # for calculating vector similarities for search
import os
import time
st.set_page_config(layout="wide")

from embeddings import get_excerpts_from_database
from llms import get_llm_output, get_or_set_openai_api_key
from prompts import system_instruction, user_prompt

st.subheader("Tipping Points Bot", divider='rainbow')

get_or_set_openai_api_key()

if st.sidebar.checkbox('Show session state'):
    st.sidebar.write(st.session_state)

@st.cache_data
def load_embeddings_df():
    df = pd.read_parquet('/Users/ranu/Downloads/tipping_points_docs/text_with_embeddings.parquet')
    return df

def display_messages_and_sources(source_history):
    for item in source_history:
        user_msg = item.get('question', None)
        response_msg = item.get('response', None)
        df_results = item.get('df_results', None)

        if user_msg:
            with st.chat_message('user'):
                st.markdown(user_msg)

        if response_msg:
            with st.chat_message('assistant'):
                st.markdown(response_msg)

                if st.checkbox('Click to see sources', key=response_msg):
                    display_sources(response_msg, df_results)

def display_sources(response_msg, df_results):
    for index, row in df_results.iterrows():
        st.write(f"Source: {row['file_name']}, Chunk number: {row['chunk_number']}, Similarity: {round(row.get('relatednesses', 0) * 100, 2)} %")
        st.write(row.get('strings', ''))
        st.write("-----")


df = load_embeddings_df()

chat_container = st.container()
query = st.chat_input("Ask a question here:")

i = 0
if query:
    df_results = get_excerpts_from_database(query, df, top_n=5)
    excerpts = df_results['strings'].tolist()

    user_prompt = user_prompt.replace("<EXCERPTS>", "\n".join(excerpts))
    user_prompt = user_prompt.replace("<QUESTION>", query)
    st.session_state.query = query
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

    
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
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