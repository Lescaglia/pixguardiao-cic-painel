import streamlit as st
import requests
import pandas as pd
from google.cloud import firestore

# --- CONFIGURAÇÃO ---
API_URL = "https://pix-guardiao-analisar-api-wafno7njtq-rj.a.run.app"

# --- CONEXÃO COM O BANCO DE DADOS ---
db = firestore.Client(project="pixguardiao-app")

# --- INTERFACE ---
st.set_page_config(layout="wide", page_title="CIC - PixGuardiao")
st.title("🛡️ Central de Inteligência Conectada (CIC)")
st.markdown("Esta interface chama a API real e lê o log de auditoria do Firestore.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Simular Nova Transação")
    id_transacao_input = st.text_input("ID da Transação para Análise:", "teste-transacao-cic-01")

    if st.button("Analisar com a API Real", type="primary"):
        with st.spinner("Chamando a API do PixGuardiao..."):
            try:
                payload = {"data": {"id_transacao": id_transacao_input}}
                response = requests.post(API_URL, json=payload)
                response.raise_for_status()
                st.success("API respondeu com sucesso!")
                st.json(response.json())
            except requests.exceptions.RequestException as e:
                st.error(f"Erro ao chamar a API: {e}")
                st.json(e.response.json() if e.response else "Nenhuma resposta do servidor.")

with col2:
    st.subheader("Log de Auditoria (Lido do Firestore)")
    
    if st.button("Atualizar Log"):
        pass
        
    try:
        with st.spinner("Lendo os últimos registros do Firestore..."):
            docs = db.collection('auditorias').order_by('timestamp_utc', direction=firestore.Query.DESCENDING).limit(5).stream()
            log_data = [doc.to_dict() for doc in docs]
            
            if log_data:
                df = pd.DataFrame(log_data)
                st.dataframe(df)
            else:
                st.write("Nenhum registro de auditoria encontrado.")
    except Exception as e:
        st.error(f"Erro ao ler o Firestore: {e}")
        
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8081))
    os.system(f"streamlit run painel_cic.py --server.port={port} --server.headless=true --server.enableCORS=false")