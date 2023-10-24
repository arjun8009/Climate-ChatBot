import streamlit as st
import pandas as pd
import sqlite3
con = sqlite3.connect('data/feedback.db')

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
                col1, col2 = st.columns([1,1])
                if col2.checkbox('Wrong Answer? Click here', key=user_msg+response_msg + 'wrong'):
                    # Uncheck the checkbox with key=response_msg so that the sources are not displayed.                    
                    feedback = st.text_area("Please write a detailed feedback:")
                    if st.button("Submit", key=user_msg + response_msg):
                        if len(feedback) < 10:
                            st.error("Please write a detailed feedback to help us improve the bot.")
                            st.stop()
                        # Save the feedback to the database along with the source_history. for the user_msg.
                        tmp_dict = {'question': user_msg, 'response': response_msg, 'df_results': df_results.to_csv(), 'feedback': feedback}
                        df = pd.DataFrame(tmp_dict, index=[0])
                        df.to_sql('feedback', con, if_exists='append', index=False)
                        st.success("Sorry about that. I will try to do better next time. Thank you for your feedback!")
                    st.stop()                
                if col1.checkbox("Click here to view sources", key=user_msg + response_msg):
                    st.markdown("#### Here are the sources I have read to answer your question:")
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
        st.info(f"###### **File**: {row['file_name']}, Paragraph number: {row['chunk_number']}, Relevance: {round(row.get('relatednesses', 0) * 100, 2)} %")
        st.write(row.get('strings', ''))
        st.markdown("-----")
