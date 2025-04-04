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
import webbrowser
from datetime import date

CLIENT_ID = 'c5f2b8b6-0ec9-4164-9959-e8f4207f564f'
CLIENT_SECRET = '0wt8Q~mLMGHALHzuYe9HBqLHv4TY1GPvgPkxyaYF'
AUTHORITY = 'https://login.microsoftonline.com/4258257d-d3fc-442c-9839-27f31a89da9e'
REDIRECT_URI = 'https://hackathon-abxxapphuu2swgej8u79mcn.streamlit.app'
SCOPE=['User.Read']
grant_type='authorization_code' 
api_key = 'pcsk_74GfB8_DQpW4kMPCFPPbPFGBJUcmwXBNbFUp6neyQ8Hqkf9cDsuW2VgYdwKHZmWQcDYxn6'
pc = Pinecone(api_key=api_key)
name = 'Verdentra-assisstant'
today = date.today()

login = False
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

def trigger_trackly_api():
    api_url = "https://raid-api.verdentra.com/api/items"
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IkNOdjBPSTNSd3FsSEZFVm5hb01Bc2hDSDJYRSIsImtpZCI6IkNOdjBPSTNSd3FsSEZFVm5hb01Bc2hDSDJYRSJ9.eyJhdWQiOiJhcGk6Ly83NGY4MTk3Zi1hNjQ1LTQ5NGItYTQ4MC03YzBjNDdlYmIxZWQiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC80MjU4MjU3ZC1kM2ZjLTQ0MmMtOTgzOS0yN2YzMWE4OWRhOWUvIiwiaWF0IjoxNzQzNzkyMDc1LCJuYmYiOjE3NDM3OTIwNzUsImV4cCI6MTc0Mzc5Njk3OCwiYWNyIjoiMSIsImFpbyI6IkFYUUFpLzhaQUFBQWphdTdrU0ZMdzFISlQyQ3hlcXJSaFRpTVVra0JqTEJ0QTErV1FVbUJuTGljSmVrYk1US1BGSEZmdlBPL2V6SUVGQmhQQnJqR0lQU0l1SWVlbUpLS2p5UlhBZ1dtaWVjMGdhYkgxNitLL1IwQkdnVlhoekZsaUdTTU8rbndkbUdXSWc2UXh0VUFQQjRJRWV4c2UzaFNRdz09IiwiYW1yIjpbInB3ZCIsInJzYSIsIm1mYSJdLCJhcHBpZCI6ImNiNzZmYWFiLTYzZWUtNDhlMS1hZjRjLTBjMDlhMGI3YWQyMiIsImFwcGlkYWNyIjoiMCIsImRldmljZWlkIjoiMTJkNGY2N2QtNTYxNi00ODJlLTk2ZGQtNzgyMjU5MTFjNjI1IiwiZmFtaWx5X25hbWUiOiJKYW5hcnRoYW5hcmFqYWgiLCJnaXZlbl9uYW1lIjoiTmlzaGFudGhhbiIsImlwYWRkciI6IjExMi4xMzQuMTY5LjIyMSIsIm5hbWUiOiJOaXNoYW50aGFuIEphbmFydGhhbmFyYWphaCIsIm9pZCI6IjZlOWMxYjgyLWU4MjctNDc3ZC1hOGUwLWU5OTBiNWI5Y2VkZiIsInJoIjoiMS5BWHdBZlNWWVF2elRMRVNZT1NmekdvbmFubjhaLUhSRnBrdEpwSUI4REVmcnNlMjdBUE44QUEuIiwic2NwIjoiYWNjZXNzX2FzX3VzZXIiLCJzaWQiOiI0NzlhNzI1Ni0xMmM4LTQyOTEtOTFlZi04YzAwZmMxODQ1MmIiLCJzdWIiOiJreG9vZzBPSFlMV3lBMHdfb0ZGQi1QZGxFR1Z5M0hxYXNEdEZMZC12My13IiwidGlkIjoiNDI1ODI1N2QtZDNmYy00NDJjLTk4MzktMjdmMzFhODlkYTllIiwidW5pcXVlX25hbWUiOiJuaXNoYW50aGFuakB2ZXJkZW50cmEuY29tIiwidXBuIjoibmlzaGFudGhhbmpAdmVyZGVudHJhLmNvbSIsInV0aSI6ImlfcTNneTRhSkVpNTdUamdVYmtqQUEiLCJ2ZXIiOiIxLjAifQ.GMRHeVh46WiYXPI5VYDsBqjJj3Qn4NH0pMIdykmohXRz3vCGfHHAbfFjEq3ubOXmvHFbJVjCEej7nbi43eesXqiiwblrWVxP3xnvNC84IDuj_gh9zE4wlY0RzPJTmjXlJMV-ZLofcUjz-JlAPLstpG8FWFMDWsPDQLE_jhMpvoS6Y2gkzOFk29wTEd7gRut30PkoE2VNhi-EPD2sAU3Kr2ywxyWpkgtIri6UsQvi4tGJhFFDEXyxf1j6gJhkJ2tR1AkLNOs1JvvPHOKFr52EBAnYkH_fMbLcbYrqAMUirX1JNRyGf22CJqJwCPiMN2F2QZOwP33Qb8bpu6HkhBcmOA'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "Title": "NishyHack",
        "targetDate": "Wed Apr 30 2025",
        "itemTypeId": 2,
        "ItemType": "Action Item",
        "itemStatusId": 1,
        "ItemStatus": "Open",
        "containerId": 39,
        "Container": "Global",
        "ownerId": 13,
        "Owner": "Assigned To Me"
    }
    
    response = requests.post(api_url, json=data, headers=headers)
    return response.json()

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
    login = True
    st.success("✅ Login successful!")
    access_token = token_result["access_token"]

    user_data = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()
    api_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IkNOdjBPSTNSd3FsSEZFVm5hb01Bc2hDSDJYRSIsImtpZCI6IkNOdjBPSTNSd3FsSEZFVm5hb01Bc2hDSDJYRSJ9.eyJhdWQiOiJhcGk6Ly83NGY4MTk3Zi1hNjQ1LTQ5NGItYTQ4MC03YzBjNDdlYmIxZWQiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC80MjU4MjU3ZC1kM2ZjLTQ0MmMtOTgzOS0yN2YzMWE4OWRhOWUvIiwiaWF0IjoxNzQzNzkyMDc1LCJuYmYiOjE3NDM3OTIwNzUsImV4cCI6MTc0Mzc5Njk3OCwiYWNyIjoiMSIsImFpbyI6IkFYUUFpLzhaQUFBQWphdTdrU0ZMdzFISlQyQ3hlcXJSaFRpTVVra0JqTEJ0QTErV1FVbUJuTGljSmVrYk1US1BGSEZmdlBPL2V6SUVGQmhQQnJqR0lQU0l1SWVlbUpLS2p5UlhBZ1dtaWVjMGdhYkgxNitLL1IwQkdnVlhoekZsaUdTTU8rbndkbUdXSWc2UXh0VUFQQjRJRWV4c2UzaFNRdz09IiwiYW1yIjpbInB3ZCIsInJzYSIsIm1mYSJdLCJhcHBpZCI6ImNiNzZmYWFiLTYzZWUtNDhlMS1hZjRjLTBjMDlhMGI3YWQyMiIsImFwcGlkYWNyIjoiMCIsImRldmljZWlkIjoiMTJkNGY2N2QtNTYxNi00ODJlLTk2ZGQtNzgyMjU5MTFjNjI1IiwiZmFtaWx5X25hbWUiOiJKYW5hcnRoYW5hcmFqYWgiLCJnaXZlbl9uYW1lIjoiTmlzaGFudGhhbiIsImlwYWRkciI6IjExMi4xMzQuMTY5LjIyMSIsIm5hbWUiOiJOaXNoYW50aGFuIEphbmFydGhhbmFyYWphaCIsIm9pZCI6IjZlOWMxYjgyLWU4MjctNDc3ZC1hOGUwLWU5OTBiNWI5Y2VkZiIsInJoIjoiMS5BWHdBZlNWWVF2elRMRVNZT1NmekdvbmFubjhaLUhSRnBrdEpwSUI4REVmcnNlMjdBUE44QUEuIiwic2NwIjoiYWNjZXNzX2FzX3VzZXIiLCJzaWQiOiI0NzlhNzI1Ni0xMmM4LTQyOTEtOTFlZi04YzAwZmMxODQ1MmIiLCJzdWIiOiJreG9vZzBPSFlMV3lBMHdfb0ZGQi1QZGxFR1Z5M0hxYXNEdEZMZC12My13IiwidGlkIjoiNDI1ODI1N2QtZDNmYy00NDJjLTk4MzktMjdmMzFhODlkYTllIiwidW5pcXVlX25hbWUiOiJuaXNoYW50aGFuakB2ZXJkZW50cmEuY29tIiwidXBuIjoibmlzaGFudGhhbmpAdmVyZGVudHJhLmNvbSIsInV0aSI6ImlfcTNneTRhSkVpNTdUamdVYmtqQUEiLCJ2ZXIiOiIxLjAifQ.GMRHeVh46WiYXPI5VYDsBqjJj3Qn4NH0pMIdykmohXRz3vCGfHHAbfFjEq3ubOXmvHFbJVjCEej7nbi43eesXqiiwblrWVxP3xnvNC84IDuj_gh9zE4wlY0RzPJTmjXlJMV-ZLofcUjz-JlAPLstpG8FWFMDWsPDQLE_jhMpvoS6Y2gkzOFk29wTEd7gRut30PkoE2VNhi-EPD2sAU3Kr2ywxyWpkgtIri6UsQvi4tGJhFFDEXyxf1j6gJhkJ2tR1AkLNOs1JvvPHOKFr52EBAnYkH_fMbLcbYrqAMUirX1JNRyGf22CJqJwCPiMN2F2QZOwP33Qb8bpu6HkhBcmOA'
    api_base_url = "https://raid-api.verdentra.com/api"  # Replace with your actual API base URL
    instructions_updated = f"""You are VERA, an Assisstant for Verdentra, you going to help with Company operations. Your primary role is to assist employees with their queries while maintaining strict confidentiality and professionalism and bit of fun. The current user is {user_data}.
    You must address {user_data['givenName']} queries while ensuring that no personal identifiable information (PII) of other employees is disclosed. If current user is Mariyam or Mahesh, you can give other employee’s objectives, data, or personal information but
    If current user is not Mariyam or Mahesh and  requests details about another employee’s objectives, personal information, respond with: "I’m sorry, but I can’t provide details about other employees and dont give files link as reference
    Dont add References in your response
    The company's leadership consists of Harsha Liyanage (CEO), Anuradha Weeraman (CTO), Mahesh Wanigasooriya (COO - Asia), Marian Rupasinghe (COO), and Ravin Wijesinghe (Head of Engineering). Only Maryam (yourself) and Mahesh Wanigasooriya are authorized to access information about other employees. If {user_data['givenName']} requests information you are unsure about, direct him to Mahesh@verdentra.com for further details. Never reveal PII of other employees under any circumstances.
    Today is {today}. If there is list in your answer please provide summary in the start and give the list
    All responses must be formatted in Markdown and maintain a clear, professional tone in American English. If an employee requests details about non-compliance due to "no-shows," cross-reference the Reservation Dump, which lists employees who booked office seats, with the Cleaned_Modified_Access_Record_Retrieval, which logs office entries and exits. If an employee booked a seat but has no corresponding entry in the access logs, they are classified as a "no-show" and considered non-compliant for that day.
    All the files that you have access is about Verdentra company that your in
    If a request violates company policies (such as requesting PII of other employees), politely decline to provide the data. Additionally, never include references when sharing information about employees. If necessary, direct the user to Mahesh Wanigasooriya for further assistance.
    If user ask you to add any items to add in trackly you need to trigger api from trackly create or add to trackly api and we cant add subtasks in Trackly, everything is tasks
        
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

    st.title(f"Welcome {user_data['givenName']} to VERA")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []


    # st.markdown("""
    #     <style>
    #     .chat-history { max-height: 400px; overflow-y: auto; }
    #     .chat-bubble { padding: 10px; border-radius: 10px; margin: 5px; display: inline-block; max-width: 90%; color: black; }
    #     .user-bubble { background-color: #DCF8C6; align-self: flex-end; }
    #     .assistant-bubble { background-color: #E6E6E6; align-self: flex-start; }
    #     .avatar { width: 40px; height: 40px; border-radius: 50%; display: inline-block; vertical-align: middle; margin-right: 10px; }
    #     .user-avatar { background-image: https://www.verdentra.com/wp-content/uploads/2024/07/Mahesh_c2a.jpg }
    #     .chat-container { display: flex; align-items: center; margin-bottom: 10px; }
    #     .user-container { justify-content: flex-end; }
    #     .assistant-container { justify-content: flex-start; }
    #     </style>
    # """, unsafe_allow_html=True)

    
    st.markdown("""
        <style>
            /* Scrollable chat history */
            .chat-history {
                max-height: 400px;
                min-width: 760px;
                overflow-y: auto;            
                animation: fadeIn 0.5s ease-in-out;            
            }

            /* Chat bubbles */
            .chat-bubble {
                padding: 12px 16px;
                border-radius: 18px;
                margin: 8px;
                display: inline-block;
                max-width: 85%;
                font-size: 14px;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                animation: slideUp 0.3s ease;
                transition: background 0.3s ease;
                line-height: 1.5;
            }

            .user-bubble {
                background-color: #d9fdd3;
                align-self: flex-end;
                color: #000;
                border: 1px solid #c3e6cb;
            }

            .assistant-bubble {
                background-color: #e0e0e0;
                align-self: flex-start;
                color: #333;
                border: 1px solid #d6d6d6;
            }

            /* Chat containers */
            .chat-container {
                display: flex;
                align-items: flex-end;
                margin-bottom: 10px;
                animation: fadeIn 0.5s ease-in-out;
            }

            .user-container {
                justify-content: flex-start;
                flex-direction: row-reverse;
            }

            .assistant-container {
                justify-content: flex-start;
                flex-direction: row;
            }

            /* Avatar */
            .avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background-size: cover;
                background-position: center;
                margin: 0 10px;
                flex-shrink: 0;
                box-shadow: 0 0 4px rgba(0,0,0,0.15);
            }

            .user-avatar {
               background-image: url('https://th.bing.com/th/id/OIP.glBtzqX5lElEUPAhQpTXqwHaF7?w=209&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7');
            }
            .assistant-avatar{
                background-image: url('https://www.verdentra.com/wp-content/uploads/2023/10/custom.svg');
            }

            @keyframes fadeIn {
                0% { opacity: 0; transform: translateY(10px); }
                100% { opacity: 1; transform: translateY(0); }
            }

            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }

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
        st.session_state['chat_history'].append({"role": "user", "content": user_input})
        
        msgs = [
            {
                "role": "user",
                "content": user_input
            }
        ] 
  
            
        
        
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

    st.markdown(f"### [ Click here to login with Microsoft]({auth_url})")

























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