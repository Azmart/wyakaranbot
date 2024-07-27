import openai
import streamlit as st
import time
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Set page configuration
st.set_page_config(page_title="मेरो व्याकरण गुरू।", page_icon=":speech_balloon:")

# Load secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

hide_github_icon = """
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, .viewerBadge_text__1JaDK{ display: none; } #MainMenu{ visibility: hidden; } footer { visibility: hidden; } header { visibility: hidden; } 
    """
st.markdown(hide_github_icon, unsafe_allow_html=True)

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
#GithubIcon {visibility:hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Authentication setup
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Check authentication status
name, authentication_status, username = authenticator.login('main')

if authentication_status:
    st.sidebar.title(f"स्वागत छ {name}।")

    assistant_id = "asst_bEIdCP6R29CcAy2R4qxtBJpd"
    client = openai

    if "start_chat" not in st.session_state:
        st.session_state.start_chat = False
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

    if st.sidebar.button("च्याट बन्द गर्नुहोस्।"):
        st.session_state.messages = []  # Clear the chat history
        st.session_state.start_chat = False  # Reset the chat state
        st.session_state.thread_id = None
        
    

    st.title("मेरो व्याकरण गुरू।")
    st.write("नमस्कार🙏")

    if st.button("च्याट सुरु गर्नुहोस्"):
        st.session_state.start_chat = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    if st.session_state.start_chat:
        if "openai_model" not in st.session_state:
            st.session_state.openai_model = "gpt-3.5-turbo-0125"
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input(""):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=prompt
            )

            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
                instructions="You are a Nepali language assistant with extensive knowledge of nepali language grammar. Your primary goal is to assist users with grammar and spelling in the Nepali language. You must perform the following tasks: 1. Only communicate in Nepali. 2. Only respond to questions related to the Nepali language and grammar. 3. Check the user's text for grammar and spelling errors. 4. If requested by the user, suggest ways to make the text more formal, informal, or refined. 5. Check grammar and spelling in all literary works such as poems, stories, essays, etc. 6. Provide only the necessary suggestions and corrections. 7. Answer questions related to the use of grammar in a fun and interesting way. 8. Do not assist in writing essays or any other forms of literary works from scratch. 9. For any information you don't know, you are free to search internet for that."
            )

            while run.status != 'completed':
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # Process and display assistant messages
            assistant_messages_for_run = [
                message for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]
            for message in assistant_messages_for_run:
                st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
                with st.chat_message("assistant"):
                    st.markdown(message.content[0].text.value)

    else:
        st.write("सुचारु गर्न 'च्याट सुरु' बटन थिच्नुहोस्।")

elif authentication_status == False:
    st.error('युजरनेम/पासवर्ड गलत भयो।')

elif authentication_status == None:
    st.warning('युजरनेम तथा पासवर्ड प्रविष्ट गर्नुहोस्।')

# Allow the user to logout
authenticator.logout('Logout', 'sidebar')
