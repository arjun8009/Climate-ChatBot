import streamlit as st
import pandas as pd

@st.cache_data
def load_embeddings_df():
    '''
    Load the dataframe with the embeddings from the parquet file.
    '''

    df = pd.read_parquet('data/text_with_embeddings.parquet')
    return df

def display_messages_and_sources(source_history):
    '''
    Display the messages and sources in the chat history. 

    Parameters:
    -----------
    source_history: list
        A list of dictionaries containing the question, response and df_results for each question asked by the user. 

    Returns:
    --------
    None

    '''
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

                # Display the sources, this checkox should be visible only when the bot has responded.
                if st.checkbox('Click to see sources', key=response_msg):
                    display_sources(response_msg, df_results)

def display_sources(response_msg, df_results):
    '''
    Display the sources for the response message.

    Parameters:
    -----------
    response_msg: str
        The response message from the bot.
    df_results: pd.DataFrame
        The dataframe containing the relevant excerpts from the database, sorted by relatedness, file_name and chunk_number.

    Returns:
    --------
    None
    '''
    
    for index, row in df_results.iterrows():
        st.write(f"Source: {row['file_name']}, Chunk number: {row['chunk_number']}, Similarity: {round(row.get('relatednesses', 0) * 100, 2)} %")
        st.write(row.get('strings', ''))
        st.write("-----")
