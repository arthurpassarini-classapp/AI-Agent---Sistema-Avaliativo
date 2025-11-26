import streamlit as st
import requests
import json

# --- Configurações Iniciais ---
st.set_page_config(
    page_title="Migrador - Gerador de Fórmulas",
    page_icon="✨",
    layout="wide" # Layout wide para melhor visualização de fórmulas complexas
)

# Constante do Webhook - INSIRA SUA URL AQUI
WEBHOOK_URL = st.secrets["webhook_url"]


# --- Barra Lateral (UX e Controles) ---
with st.sidebar:
    st.title("ⓘ Info")
    st.caption("Gere fórmulas para o sistema avaliativo de forma automatizada.")
    
    st.markdown("---")
    
    # Botão de Limpar com confirmação visual melhorada
    if st.button("🗑️ Limpar Conversa", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("Made with ❤️ by **Enablement**")

# --- Interface Principal ---
st.title("֎ Gerador de Fórmulas Avaliativas")
st.markdown("""
Bem-vindo ao assistente do Migrador. Descreva a lógica da avaliação e eu gerarei a fórmula correspondente.
""")

# --- Lógica de Comunicação com Webhook ---
def enviar_para_webhook(prompt_usuario, historico):
    """
    Envia a mensagem para o webhook configurado.
    Adapte o payload (json) conforme o que sua API espera receber.
    """
    if WEBHOOK_URL == "[INSIRA O WEBHOOK AQUI]":
        return "⚠️ Erro: A URL do Webhook ainda não foi configurada no código."

    headers = {"Content-Type": "application/json"}
    
    # Estrutura do JSON enviada para o seu endpoint
    payload = {
        "message": prompt_usuario,
        "history": historico # Envia contexto anterior se necessário
    }

    try:
        response = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Levanta erro para status 4xx/5xx
        
        # Tratamento da resposta baseada no formato fornecido: [{"output": "..."}]
        dados = response.json()
        
        # Caso 1: A resposta é uma lista (formato esperado)
        if isinstance(dados, list) and len(dados) > 0:
            item = dados[0]
            if isinstance(item, dict):
                return item.get("output", str(item))
            return str(item)
            
        # Caso 2: A resposta é um dicionário único (fallback)
        elif isinstance(dados, dict):
            return dados.get("output", dados.get("response", dados.get("text", str(dados))))
            
        return str(dados)
        
    except requests.exceptions.RequestException as e:
        return f"❌ Erro de conexão com o Webhook: {str(e)}"
    except json.JSONDecodeError:
        return f"❌ Erro: A resposta do servidor não é um JSON válido. Resposta crua: {response.text}"
    except Exception as e:
        return f"❌ Erro inesperado ao processar resposta: {str(e)}"

# --- Gerenciamento do Estado (Histórico) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensagem de boas-vindas inicial da IA (opcional)
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Olá! Estou pronto. Qual é a regra de negócio para a fórmula de hoje?"
    })

# --- Renderização do Chat ---
for message in st.session_state.messages:
    # Diferencia ícones para UX
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- Input do Usuário ---
if prompt := st.chat_input("Ex: Se nota > 8 e presença > 90%, então Aprovado..."):
    
    # 1. Exibir mensagem do usuário
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Processar resposta via Webhook
    with st.chat_message("assistant", avatar="🤖"):
        # UX: Spinner enquanto aguarda o servidor
        with st.spinner("Aguarde..."):
            resposta_api = enviar_para_webhook(prompt, st.session_state.messages)
            
            st.markdown(resposta_api)
            
            # Se for uma fórmula matemática, o Streamlit renderiza LaTeX bem com st.latex()
            # Se sua API retornar algo entre $$, o markdown já trata isso.
    
    # 3. Salvar resposta no histórico
    st.session_state.messages.append({"role": "assistant", "content": resposta_api})