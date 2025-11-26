import streamlit as st
import requests
import json
import random

# --- Configurações Iniciais ---
st.set_page_config(
    page_title="TAM IA",
    page_icon="✨",
    layout="wide" # Layout wide para melhor visualização de fórmulas complexas
)

# Constante do Webhook - INSIRA SUA URL AQUI
WEBHOOK_URL = st.secrets["webhook_url"]

with st.sidebar:
    st.image("	https://cdn.siga.activesoft.com.br/siga-producao/logo_brand_activesoft_completa.png", width=800) # Opcional: ícone/logo
    st.markdown("<div style='text-align: center; color: grey; font-size: 12px;'> ⚡ Powered by <b>Enablement team</b></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.title("Assistente de Fórmulas")
    st.caption("Gere lógicas para o Activesoft de forma automatizada.")
    
    # --- Seção 1: O que a ferramenta sabe? (Cheat Sheet) ---
    st.markdown("### 🧠 Base de Conhecimento")
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
    
    st.markdown("---")
    
    # --- Controles da Sessão ---
    if st.button("🗑️ Limpar Conversa", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("### Suporte")
    st.markdown("Encontrou um erro ou a fórmula não funcionou?")
    st.link_button("🎫 Abrir Ticket Enablement", "https://arco.enterprise.slack.com/archives/C081H84965V", help="Fale com o time de suporte.")



# --- Interface Principal ---
st.title("֎ Gerador de Fórmulas Avaliativas")
with st.container():
    st.markdown("""
    Este assistente traduz regras de negócio pedagógicas para a sintaxe de fórmulas do **Activesoft**.
    
    **Como usar:**
    1. Descreva a regra de cálculo (ex: média ponderada, recuperação, faltas).
    2. O assistente gerará a fórmula pronta para copiar e colar.
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
        
    # except requests.exceptions.RequestException as e:
    #     return f"❌ Erro de conexão com o Webhook: {str(e)}"
    # except json.JSONDecodeError:
    #     return f"❌ Erro: A resposta do servidor não é um JSON válido. Resposta crua: {response.text}"
    # except Exception as e:
    #     return f"❌ Erro inesperado ao processar resposta: {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"❌ Erro inesperado, abra um ticket em #suporte_enablement"
    except json.JSONDecodeError:
        return f"❌ Erro inesperado, abra um ticket em #suporte_enablement"
    except Exception as e:
        return f"❌ Erro inesperado, abra um ticket em #suporte_enablement"

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

# # --- Input do Usuário ---
# placeholders_dicas = [
#     "Ex: Média Aritmética das fases [NF01], [NF02] e [NF03]...",
#     "Ex: Se a nota [NF04] > 7, aprovado, senão vai para recuperação...",
#     "Ex: Fórmula para arredondar a nota final em 0.5...",
#     "Ex: Calcular faltas somando [FF01] + [FF02]...",
#     "Ex: Média Ponderada: NF01 (peso 1) e NF02 (peso 2)...",
#     "Ex: Reprovar se a frequência for menor que 75%..."
# ]

# placeholder_atual = random.choice(placeholders_dicas)

if prompt := st.chat_input("Ex: Média Aritmética das fases [NF01], [NF02] e [NF03]..."):
    
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
