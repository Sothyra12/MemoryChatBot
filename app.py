"""
Author: Sothyra Chan
Last Modified by: Sothyra Chan
Date Last Modified: 2024-08-02
Program Description: This module handles user input and interaction with the ChatGPT API during entire conversation sessions.
Revision History:
  - 2024-07-30: Added initial setup for ChatGPT API integration.
  - 2024-07-31: Implemented memory-based conversation tracking.
  - 2024-08-1: Enhanced error handling for API initialization and updated the code due to some deprecated version.
  - 2024-08-1: Set up a virtual environment, and completed the projected.
Source: This implementation is based on the YouTube tutorial "AI Memory ChatBot with Conversational Memory | ChatGPT API and LangChain" by Caffeine and Code.
Author: Avratanu Biswas
URL: https://www.youtube.com/watch?v=cHjlperESbg&t=898s
"""


# Import necessary libraries
import os
import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain_community.chat_models import ChatOpenAI

# Initialize session state
if "generated" not in st.session_state:
    st.session_state["generated"] = []  # Model's output
if "past_conversation" not in st.session_state:
    st.session_state["past_conversation"] = []  # User's input history
if "input" not in st.session_state:
    st.session_state["input"] = ""  # Current user input
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []  # Saved conversation sessions

def get_text():
    """
    Get user input text.

    Returns:
        str: User input text
    """
    input_text = st.text_input(
        "You: ",
        st.session_state["input"],
        key="input",
        placeholder="AI assistant here! Type and ask me anything...",
        label_visibility='hidden'
    )
    return input_text

def new_chat():
    """
    Clears session state and commences a new chat session.
    """
    save = []
    # Save the current conversation to stored sessions
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        save.append("User: " + st.session_state["past_conversation"][i])
        # Access the response from the generated dictionary
        bot_response = st.session_state["generated"][i].get("response", "")
        save.append("Bot: " + bot_response)
    st.session_state["stored_session"].append(save)
    # Reset session states
    st.session_state["generated"] = []
    st.session_state["past_conversation"] = []
    st.session_state["input"] = ""
    # Reinitialize the entity memory to clear it
    st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=10)

# Set the title of the app
st.title("MemoryBot AI Assistant")

# Get API key from user input
api_key = st.sidebar.text_input("Please Enter Your API-Key here: ", type="password")
MODEL = st.sidebar.selectbox(label='Model', options=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"])

if api_key:
    try:
        # Set the environment variable
        os.environ["OPENAI_API_KEY"] = api_key

        # Create ChatOpenAI instance
        llm = ChatOpenAI(
            temperature=0,
            model_name=MODEL,
        )

        # Create a conversation memory
        if 'entity_memory' not in st.session_state:
            st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=10)

        # Create a conversation chain
        Conversation = ConversationChain(
            llm=llm,
            prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
            memory=st.session_state.entity_memory,
        )

    except Exception as e:
        st.error(f"Failed to initialize OpenAI: {e}")  # Error handling for API initialization
else:
    st.error("No API found! Please enter your OpenAI API-Key to continue.")

# Create a button to start a new chat session
st.sidebar.button("New Chat", on_click=new_chat, type='primary')

# Get user input
user_input = get_text()

# Generate output using ConversationChain instance and the user input, and add the input to the conversation history
if user_input:
    output = Conversation.invoke(input=user_input)

    st.session_state.past_conversation.append(user_input)
    st.session_state.generated.append(output)

with st.expander("Conversation"):
    # Display the conversation history
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        st.info(st.session_state["past_conversation"][i])
        # Access the response from the generated dictionary
        bot_response = st.session_state["generated"][i].get("response", "")
        st.success(bot_response, icon="🤖")