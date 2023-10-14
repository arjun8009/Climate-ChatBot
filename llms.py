import time
import openai
import streamlit as st
import os
import json

def get_llm_output(messages, model='gpt-3.5-turbo', max_tokens=500, temperature=0):

    # messages = [
    # {"role": "system", "content": "You answer questions about the 2022 Winter Olympics."},
    # {"role": "user", "content": message},
    # ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=max_tokens,
    )
    response_message = response["choices"][0]["message"]["content"]
    return response_message

def get_or_set_openai_api_key():
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
