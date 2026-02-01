import streamlit as st
import ollama
import os
from summarize import get_system_stats, list_files, summarize_directory, read_specific_file, triage_emails

st.set_page_config(page_title="AI Agent OS Supervisor", page_icon="🤖", layout="wide")

st.title("🤖 Agent")
st.markdown("Interface de supervision et d'analyse de documents (PDF, Word, Texte)")

with st.sidebar:
    st.header("Système")
    if st.button("Actualiser les stats"):
        stats = get_system_stats()
        st.write(stats)
    
    st.divider()
    st.info("Agents disponibles : Supervisor, Summarizer, Email Triage (Study)")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": (
                "Tu es un superviseur d'OS. "
                "Si l'utilisateur mentionne 'mails', 'messages', 'emails' ou 'courriels', "
                "tu dois EXCLUSIVEMENT utiliser l'outil 'triage_emails'. "
                "N'essaie jamais d'utiliser 'list_files' ou 'summarize_directory' pour les emails."
            )
        }
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Comment puis-je vous aider avec vos fichiers ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("L'agent réfléchit..."):
            available_tools = [get_system_stats, list_files, summarize_directory, read_specific_file, triage_emails]
            
            response = ollama.chat(
                model="llama3.2", 
                messages=st.session_state.messages, 
                tools=available_tools
            )

            if response.get('message', {}).get('tool_calls'):
                st.session_state.messages.append(response['message'])
                
                for tool in response['message']['tool_calls']:
                    name = tool['function']['name']
                    args = tool['function']['arguments']
                    
                    if name == "get_system_stats": result = get_system_stats()
                    elif name == "list_files": result = list_files(**args)
                    elif name == "summarize_directory": result = summarize_directory(**args)
                    elif name == "read_specific_file": result = read_specific_file(**args)
                    elif name == "triage_emails": result = triage_emails(**args)
                    else: result = f"Outil '{name}' inconnu."
                    
                    st.session_state.messages.append({'role': 'tool', 'content': result})
                
                final_res = ollama.chat(model="llama3.2", messages=st.session_state.messages)
                full_response = final_res['message']['content']
            else:
                full_response = response['message']['content']
            
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})