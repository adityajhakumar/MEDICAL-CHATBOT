import streamlit as st
import requests

# Define API key and endpoint
api_key = '546a6970e213017a1ad6bcaab76e66c4'
default_model = 'gpt-3.5-turbo'
api_url = 'http://195.179.229.119/gpt/api.php'

# Streamlit interface setup
st.set_page_config(page_title="Medical Assistant Chat", page_icon="💬", layout="wide")
st.title("💬 Medical Assistant Chat")
st.markdown("""
    **Welcome to your Personal Medical Assistant.**
    I am here to help answer any health-related questions you may have, provide information about medical conditions, and guide you to the right resources. 
    How can I assist you today? Feel free to ask me anything!
""", unsafe_allow_html=True)

# Styling
st.markdown("""
    <style>
    .css-1d391kg {
        background-color: #f2f8fb;
    }
    .streamlit-expanderHeader {
        font-size: 20px;
    }
    .chat-bubble-user {
        background-color: #e1f7e1;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .chat-bubble-assistant {
        background-color: #d4f1f4;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .assistant-response {
        font-size: 16px;
        line-height: 1.6;
    }
    .assistant-heading {
        font-weight: bold;
        font-size: 18px;
        color: #00796b;
    }
    </style>
""", unsafe_allow_html=True)

# Define a session state for storing chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the previous chat history (if any)
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-assistant"><b>Assistant:</b> {message["content"]}</div>', unsafe_allow_html=True)

# Input box for user to send message
user_input = st.text_input("Ask me anything (e.g., symptoms, medical conditions, treatments):", "")

if user_input:
    # Add user's message to the chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Define the prompt for the API based on all prior messages (for continuous conversation)
    conversation_history = "\n".join([message["content"] for message in st.session_state.messages])

    # Choose the model (you can add other options here)
    model = default_model

    # Make the API request
    try:
        response = requests.get(
            api_url,
            params={
                "prompt": conversation_history,
                "api_key": api_key,
                "model": model
            }
        )
        response.raise_for_status()  # Check for HTTP errors

        # Get the response from the API using the 'content' field
        data = response.json()
        chat_gpt_response = data.get("content", "Sorry, I couldn't generate a response.")

        # Format the response for medical-related queries
        # Ensure bold, bullet points, and headings are correctly formatted
        formatted_response = chat_gpt_response

        # Replace **bold** with Markdown or HTML tags
        formatted_response = formatted_response.replace("**", "<b>").replace("**", "</b>", 1)

        # Ensure markdown and bullet points are parsed as well
        formatted_response = formatted_response.replace("1.", "<ul><li>").replace("2.", "<ul><li>")
        formatted_response = formatted_response.replace("\n", "</li><li>").replace("</ul><li>", "</li></ul>")

        # Format sections like headings using HTML tags
        formatted_response = f"<div class='assistant-response'>{formatted_response}</div>"

        # Add assistant's response to the chat history
        st.session_state.messages.append({"role": "assistant", "content": formatted_response})

        # Display the assistant's response
        st.markdown(formatted_response, unsafe_allow_html=True)

    except requests.RequestException as e:
        # Display any errors in case of a failed request
        st.error(f"Error: {e}")
