import os
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Fallback approach: Try st.secrets first, then environment variable
gemini_api_key = None

# 1) Check if secret exists in st.secrets
if "GEMINI_API_KEY" in st.secrets:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
# 2) Otherwise, check environment variable (for Colab or local dev)
elif os.getenv("GEMINI_API_KEY"):
    gemini_api_key = os.getenv("GEMINI_API_KEY")

# 3) If still None, stop
if not gemini_api_key:
    st.warning("No GEMINI_API_KEY found in secrets or environment.")
    st.stop()

# Main chat interface
st.title("Kanye West GPT 🤔")
st.caption("Ask Kanye anything and get his unfiltered thoughts!")

# Initialize message history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "What's good? It's Ye. What do you wanna know?"}
    ]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input
if prompt := st.chat_input():
    # Configure Gemini
    genai.configure(api_key=gemini_api_key)
    generation_config = {
        "temperature": 0.9,  # Higher temperature for more creative responses
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-pro",  # Use the base Gemini Pro model
        generation_config=generation_config,
    )

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Get Gemini response
    try:
        response = model.generate_content(
            f"You are Kanye West. You are confident, creative, and sometimes controversial. "
            f"Respond like Kanye would. {prompt}",
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        msg = response.text

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
