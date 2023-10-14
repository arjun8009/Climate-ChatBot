import time
import openai
import streamlit as st
import os
import json

def get_llm_output(messages, model='gpt-3.5-turbo', max_tokens=500, temperature=0):

    '''
    Get the response from the Language Learning Model (LLM) for the given messages. We are using ChatGPT model for this.

    Parameters:
    -----------
    messages: list
        A list of dictionaries containing the role and content of each message in the conversation. comes from the chat_history in the session state.
    model: str
        The name of the model to use. The default is 'gpt-3.5-turbo'.
    max_tokens: int
        The maximum number of tokens to generate. The default is 500.
    temperature: float
        What sampling temperature to use. Higher values mean the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer. The default is 0.
    
    Returns:
    --------
    response_message: str
        The response message from the LLM.
    '''

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=max_tokens,
    )
    response_message = response["choices"][0]["message"]["content"]
    return response_message

def get_or_set_openai_api_key():
    '''
    This function will check if the openai api key is set in the secrets.json file. If not, it will ask the user to enter the api key.
    '''
    import json
    if not os.path.exists("secrets.json"):
        ph1 = st.empty()
        ph2 = st.empty()
        ph3 = st.empty()
        api_key = ph1.text_input("Please enter your OpenAI API key")
        ph2.error("No secrets.json found. Please add your OpenAI API key.")
        if ph3.button("Save"):
            with open("secrets.json", 'w') as outfile:
                json.dump({"openai_api_key": api_key}, outfile) 
            ph1.empty()
            ph2.empty()
            ph3.empty()
            with st.spinner('Saving...'):
                time.sleep(3)
                st.success("Saved!")

            st.experimental_rerun()
        else:
            st.stop()
    else:
        with open("secrets.json") as f:
            secrets = json.load(f)

    st.session_state.openai_api_key = secrets['openai_api_key']

    openai.api_key = st.session_state.openai_api_key
    return None
