from getpass import getpass
from pinecone import Pinecone # type: ignore
from openai import OpenAI  # type: ignore
import os 
import streamlit as st # type: ignore
from streamlit_msal  import Msal # type: ignore
import uuid
import json
import msal # type: ignore
import requests # type: ignore

CLIENT_ID = 'c5f2b8b6-0ec9-4164-9959-e8f4207f564f'
CLIENT_SECRET = '0wt8Q~mLMGHALHzuYe9HBqLHv4TY1GPvgPkxyaYF'
AUTHORITY = 'https://login.microsoftonline.com/4258257d-d3fc-442c-9839-27f31a89da9e'
REDIRECT_URI = 'https://hackathon-abxxapphuu2swgej8u79mcn.streamlit.app'
SCOPE=['User.Read']
grant_type='authorization_code' 
api_key = 'pcsk_74GfB8_DQpW4kMPCFPPbPFGBJUcmwXBNbFUp6neyQ8Hqkf9cDsuW2VgYdwKHZmWQcDYxn6'
pc = Pinecone(api_key=api_key)
name = 'Verdentra-assisstant'




def get_msal_app():
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )

def get_auth_url():
    session_state = str(uuid.uuid4())
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        scopes=SCOPE,
        state=session_state,
        redirect_uri=REDIRECT_URI,
        grant_type=grant_type
    )
    return auth_url

def get_token_from_code(auth_code):
    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        auth_code,
        scopes=SCOPE,
        redirect_uri=REDIRECT_URI
    )
    return result


def get_chatbot_response(userinput):
    msgs = [
        {
            "role": "user",
            "content": user_input
        }
    ] 
    resp = oai_client.chat.completions.create(
        model="gpt-4o",
        messages=msgs
    ) 
    return resp.choices[0].message.content

query_params = st.query_params

if "code" in query_params and "token_result" not in st.session_state:
    auth_code = query_params["code"]
    token_result = get_token_from_code(auth_code)
    st.session_state["token_result"] = token_result
else:
    token_result = st.session_state.get("token_result")


if token_result and "access_token" in token_result:
    st.success("✅ Login successful!")
    access_token = token_result["access_token"]

    user_data = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    instructions_updated = f"""You are Maryam, a helpful HR assistant at Verdentra, headquartered in Colombo, Sri Lanka. Your primary role is to assist employees with their queries while maintaining strict confidentiality and professionalism. The current user is {user_data}. You must address {user_data['givenName']} queries while ensuring that no personal identifiable information (PII) of other employees is disclosed. If {user_data['givenName']} requests details about another employee’s objectives, data, or personal information, respond with: "I’m sorry, but I can’t provide details about other employees."

    The company's leadership consists of Harsha Liyanage (CEO), Anuradha Weeraman (CTO), Mahesh Wanigasooriya (COO - Asia), Marian Rupasinghe (COO), and Ravin Wijesinghe (Head of Engineering). Only Maryam (yourself) and Mahesh Wanigasooriya are authorized to access information about other employees. If {user_data['givenName']} requests information you are unsure about, direct him to Mahesh@verdentra.com for further details. Never reveal PII of other employees under any circumstances.

    All responses must be formatted in Markdown and maintain a clear, professional tone in American English. If an employee requests details about non-compliance due to "no-shows," cross-reference the Reservation Dump, which lists employees who booked office seats, with the Cleaned_Modified_Access_Record_Retrieval, which logs office entries and exits. If an employee booked a seat but has no corresponding entry in the access logs, they are classified as a "no-show" and considered non-compliant for that day.

    If a request violates company policies (such as requesting PII of other employees), politely decline to provide the data. Additionally, never include references when sharing information about employees. If necessary, direct the user to Mahesh Wanigasooriya for further assistance.
    """
    
    if name not in [a.name for a in pc.assistant.list_assistants()]:
        assistant = pc.assistant.create_assistant(
            assistant_name=name,
            instructions=instructions_updated,
            timeout=30
        )
    else:
        assistant = pc.assistant.Assistant(assistant_name=name)


    url = f"{assistant.host}/chat/{assistant.name}"
    oai_client = OpenAI(api_key=api_key, base_url=url)
    assistant = pc.assistant.update_assistant(
        assistant_name=name, 
        instructions=instructions_updated,
    )

    st.title(f"Welcome {user_data['givenName']} to Verdentra HR Assistance")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []


    st.markdown("""
        <style>
        .chat-history { max-height: 400px; overflow-y: auto; }
        .chat-bubble { padding: 10px; border-radius: 10px; margin: 5px; display: inline-block; max-width: 70%; color: black; }
        .user-bubble { background-color: #DCF8C6; align-self: flex-end; }
        .assistant-bubble { background-color: #E6E6E6; align-self: flex-start; }
        .avatar { width: 40px; height: 40px; border-radius: 50%; display: inline-block; vertical-align: middle; margin-right: 10px; }
        .user-avatar { background-image: url('W/"1c425770520f3a3c27b1f295f042dc89a4cc6d338133b5b67b9259b517399da6"'); }
        .assistant-avatar { background-image: url('data:image/png;base64,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'); }
        .chat-container { display: flex; align-items: center; margin-bottom: 10px; }
        .user-container { justify-content: flex-end; }
        .assistant-container { justify-content: flex-start; }
        </style>
    """, unsafe_allow_html=True)

 
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    for chat in st.session_state['chat_history']:
        if chat['role'] == 'user':
            st.markdown(f'<div class="chat-container user-container"><div class="avatar user-avatar"></div><div class="chat-bubble user-bubble">{chat["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-container assistant-container"><div class="avatar assistant-avatar"></div><div class="chat-bubble assistant-bubble">{chat["content"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    user_input = st.chat_input("Enter your message:")
    if user_input:
        
        msgs = [
            {
                "role": "user",
                "content": user_input
            }
        ] 
        st.session_state['chat_history'].append({"role": "user", "content": user_input})
        resp = oai_client.chat.completions.create(
            model="gpt-4o",
            messages=msgs,
            max_tokens=50
        ) 
        # resp = assistant.chat(messages=msgs)
        response = resp.choices[0].message.content  
        
        st.session_state['chat_history'].append({"role": "assistant", "content": response})
        st.rerun()
else:
    auth_url = get_auth_url()
    st.markdown(f"### [🔐 Click here to login with Microsoft]({auth_url})")

























# citation = f"[{resp.citations[0].references[0].pages}]({resp.citations[0].references[0].file.signed_url})"

# content = str(resp.message.content)

# for citation in reversed(resp.citations):
#     # build markdown citation
#     pages = str(citation.references[0].pages)
#     url = citation.references[0].file.signed_url
#     markdown_citation = f" [{pages}]({url})"
#     # insert citation
#     pos = citation.position
#     content = content[:pos] + markdown_citation + content[pos:]

# print(resp.choices[0].message.content)




# print(assistant)

# response = assistant.upload_file(
#     file_path=r"C:\Users\NishanthanJanarthana\Downloads\Verdentra Time Reporting Policy - V 1.2.pdf",
#     metadata={"company": "verdentra", "document_type": "pdf"},
#     timeout=None
# )




# resp = assistant.chat(messages=msgs)


# print(resp,citation)