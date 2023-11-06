import os
import openai
import streamlit as st
import requests
from langchain.llms import OpenLM
from langchain.chains import LLMChain


openai_api_key = st.secrets["openai_api_key"]

# Correct way to pass the api_key in the newer versions of LangChain
llm = OpenLM(
    model="text-davinci-003",
    model_kwargs={
        "api_key": st.secrets["openai_api_key"]  # Pass api_key within model_kwargs
    },
)


def generate_response(prompt):
    headers = {
        "Authorization": f'Bearer {st.secrets["openai_api_key"]}',
        "Content-Type": "application/json",
    }

    data = {"prompt": prompt, "max_tokens": 150, "model": "text-davinci-003"}

    try:
        response = requests.post(
            "https://api.openai.com/v1/completions", headers=headers, json=data
        )
        response.raise_for_status()  # This will raise an exception for HTTP error codes
        response_data = response.json()
        # st.write(response_data)  # Log the full response data
        return response_data["choices"][0]["text"].strip()
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")  # HTTP error
    except Exception as err:
        st.error(f"Other error occurred: {err}")  # Other errors
    return "I'm not sure how to respond to that."


# Streamlit app setup
st.title("Hotel Finder Chat")
st.write(
    "Welcome to the Hotel Finder. Ask me anything about hotels, and I'll try to help!"
)

# Session state to keep track of conversation
if "conversation" not in st.session_state:
    st.session_state["conversation"] = []

# Text input for user message
user_message = st.text_input("Your question:")

# When the user sends a message, add it to the conversation and generate a response
if st.button("Send"):
    if user_message:
        # Append user message to conversation
        st.session_state["conversation"].append(
            {"role": "user", "content": user_message}
        )

        # Generate a response using the generate_response function
        response = generate_response(user_message)

        # Append the AI response to the conversation
        st.session_state["conversation"].append({"role": "system", "content": response})

        # Clear the input box after sending the message
        user_message = ""
    else:
        st.warning("Please enter a message.")

# Display the conversation
for index, message in enumerate(st.session_state["conversation"]):
    role = message["role"]
    content = message["content"]
    key = f"{role}_{index}"  # This creates a unique key for each widget
    if role == "user":
        st.text_area("You", value=content, height=75, key=key)
    else:
        st.text_area("Travel Agent", value=content, height=75, key=key)
