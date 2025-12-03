import streamlit as st
import requests
import json
import random

# --- Configurações Iniciais ---
st.set_page_config(
    page_title="TAM IA",
    page_icon="✨",
    layout="wide"
)

# Constantes dos Webhooks
WEBHOOK_AVALIATIVO = st.secrets["webhook_avaliativo"]
WEBHOOK_CNAB = st.secrets["webhook_cnab"]

# --- Função de Envio para Webhook ---
def enviar_para_webhook(prompt_usuario, historico, webhook_url):
    """
    Envia a mensagem para o webhook configurado.
    """
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "message": prompt_usuario,
        "history": historico
    }

    try:
        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        dados = response.json()
        
        if isinstance(dados, list) and len(dados) > 0:
            item = dados[0]
            if isinstance(item, dict):
                return item.get("output", str(item))
            return str(item)
            
        elif isinstance(dados, dict):
            return dados.get("output", dados.get("response", dados.get("text", str(dados))))
            
        return str(dados)
        
    except requests.exceptions.RequestException as e:
        return f"❌ Erro inesperado, abra um ticket em #suporte_enablement"
    except json.JSONDecodeError:
        return f"❌ Erro inesperado, abra um ticket em #suporte_enablement"
    except Exception as e:
        return f"❌ Erro inesperado, abra um ticket em #suporte_enablement"

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn.siga.activesoft.com.br/siga-producao/logo_brand_activesoft_completa.png", width=800)
    st.markdown("<div style='text-align: center; color: grey; font-size: 12px;'> ⚡ Powered by <b>Enablement team</b></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.title("Assistentes Disponíveis")
    st.caption("Escolha o agente especializado na aba principal.")
    
    st.markdown("### 🤖 Agentes:")
    st.markdown("**📊 Sistema Avaliativo** - Fórmulas pedagógicas")
    st.markdown("**🏦 CNAB Bancário** - Processamento de arquivos bancários")
    
    st.markdown("---")
    
    st.markdown("### Suporte")
    st.markdown("Encontrou um erro ou a fórmula não funcionou?")
    st.link_button("🎫 Abrir Ticket Enablement", "https://arco.enterprise.slack.com/archives/C081H84965V", help="Fale com o time de suporte.")

# --- Título Principal ---
st.title("✨ TAM IA - Assistentes Especializados")

# --- Criação das Abas ---
tab1, tab2 = st.tabs(["📊 Sistema Avaliativo", "🏦 CNAB Bancário"])

# ============================================================================
# ABA 1: SISTEMA AVALIATIVO
# ============================================================================
with tab1:
    st.header("Gerador de Fórmulas Avaliativas")
    
    with st.container():
        st.markdown("""
        Este assistente traduz regras de negócio pedagógicas para a sintaxe de fórmulas do **Activesoft**.
        
        **Como usar:**
        1. Descreva a regra de cálculo (ex: média ponderada, recuperação, faltas).
        2. O assistente gerará a fórmula pronta para copiar e colar.
        """)
    
    # Expanders com informações específicas
    with st.expander("🧠 Base de Conhecimento - Sistema Avaliativo"):
        st.info("Eu conheço a sintaxe oficial do Activesoft (variáveis, funções e regras de arredondamento).")

    with st.expander("📚 Dicionário de Variáveis"):
        st.markdown("""
        **Notas:**
        * `[NF01]`: Nota da Fase 01 (ex: 1º Bimestre)
        * `[NC01]`: Nota de Composição 01 (ex: Prova)
        
        **Faltas:**
        * `[FF01]`: Faltas da Fase 01
        * `[QF01]`: Qtde. Faltas (Total)
        * `[AD01]`: Aulas Dadas
        
        **Outros:**
        * `[MEDIA]`: Média calculada
        * `[SIGLADISCIPLINA]`: Sigla da matéria atual
        """)

    with st.expander("➗ Funções Principais"):
        st.markdown("""
        * **Condicional:** `IF(condição, verdadeiro, falso)`
        * **Comparação:** `MAIOR(v1, v2)` ou `MENOR(v1, v2)`
        * **Média Inteligente:** `MEDIA_NOTAS_INFORMADAS(...)`
        * **Arredondamento:** `ARREDONDAR05(valor)`, `TRUNC(valor)`, etc.
        """)

    with st.expander("💡 Exemplos de Prompts"):
        st.markdown("**Copie e adapte:**")
        
        st.markdown("🔹 *Média Simples*")
        st.code("Crie uma fórmula de Média Anual somando [NF01], [NF02], [NF03] e dividindo por 3.")
        
        st.markdown("🔹 *Recuperação*")
        st.code("Se a [NF04] for >= 7, mantém ela. Senão, faz a média entre [NF04] e a Recuperação [NF05].")
        
        st.markdown("🔹 *Arredondamento*")
        st.code("Arredonde a média final para 0.5 (ex: 7.2 vira 7.5) usando as regras do Activesoft.")
    
    # Gerenciamento do Estado - Avaliativo
    if "messages_avaliativo" not in st.session_state:
        st.session_state.messages_avaliativo = []
        st.session_state.messages_avaliativo.append({
            "role": "assistant", 
            "content": "Olá! Estou pronto para ajudar com fórmulas avaliativas. Qual é a regra de negócio que você precisa?"
        })
    
    # Renderização do Chat - Avaliativo
    for message in st.session_state.messages_avaliativo:
        avatar = "🧑‍💻" if message["role"] == "user" else "📊"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
    
    # Input do Usuário - Avaliativo
    if prompt_avaliativo := st.chat_input("Ex: Média Aritmética das fases [NF01], [NF02] e [NF03]...", key="input_avaliativo"):
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt_avaliativo)
        st.session_state.messages_avaliativo.append({"role": "user", "content": prompt_avaliativo})
        
        with st.chat_message("assistant", avatar="📊"):
            with st.spinner("Processando..."):
                resposta_api = enviar_para_webhook(prompt_avaliativo, st.session_state.messages_avaliativo, WEBHOOK_AVALIATIVO)
                st.markdown(resposta_api)
        
        st.session_state.messages_avaliativo.append({"role": "assistant", "content": resposta_api})
    
    # Botão de limpar - Avaliativo
    if st.button("🗑️ Limpar Conversa - Avaliativo", key="clear_avaliativo"):
        st.session_state.messages_avaliativo = []
        st.rerun()

# ============================================================================
# ABA 2: CNAB BANCÁRIO
# ============================================================================
with tab2:
    st.header("Assistente CNAB Bancário")
    
    with st.container():
        st.markdown("""
        **Como usar:**
        1. Envie qual banco deseja saber o CNAB Activesoft, WPensar e se o cliente precisa migrar.
        2. O assistente fornecerá orientações.
        """)
    
    # Gerenciamento do Estado - CNAB
    if "messages_cnab" not in st.session_state:
        st.session_state.messages_cnab = []
        st.session_state.messages_cnab.append({
            "role": "assistant", 
            "content": "Olá! Estou pronto para ajudar com arquivos CNAB. Qual é sua dúvida sobre processamento bancário?"
        })
    
    # Renderização do Chat - CNAB
    for message in st.session_state.messages_cnab:
        avatar = "🧑‍💻" if message["role"] == "user" else "🏦"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
    
    # Input do Usuário - CNAB
    if prompt_cnab := st.chat_input("Ex: Como validar um arquivo CNAB 240 do Itaú?", key="input_cnab"):
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt_cnab)
        st.session_state.messages_cnab.append({"role": "user", "content": prompt_cnab})
        
        with st.chat_message("assistant", avatar="🏦"):
            with st.spinner("Processando..."):
                resposta_api = enviar_para_webhook(prompt_cnab, st.session_state.messages_cnab, WEBHOOK_CNAB)
                st.markdown(resposta_api)
        
        st.session_state.messages_cnab.append({"role": "assistant", "content": resposta_api})
    
    # Botão de limpar - CNAB
    if st.button("🗑️ Limpar Conversa - CNAB", key="clear_cnab"):
        st.session_state.messages_cnab = []
        st.rerun()
