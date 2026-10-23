"""Class 7 | Soumya AI Vision | AI Interview Coach
Run: pip install -r requirements.txt
     streamlit run streamlit_app_groq_openai.py
Set GROQ_API_KEY / OPENAI_API_KEY in .env, your environment, or Streamlit
secrets; never hardcode a key.
"""
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

load_dotenv(override=True)  # .env wins over any stale key in the environment

st.set_page_config(page_title="AI Interview Coach | Soumya AI Vision", page_icon="🎯", layout="centered")
st.title("🎯 AI Interview Coach")
st.caption("A hands-on LangChain Prompt Templates project | Soumya AI Vision")

with st.sidebar:
    st.header("Interview settings")
    role = st.selectbox("Role", ["GenAI Engineer", "Python Developer", "Data Scientist", "Data Engineer"])
    experience = st.selectbox("Experience", ["Fresher", "0–2 years", "2–4 years", "5+ years"])
    difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
    interview_type = st.selectbox("Interview type", ["Technical + Coding", "Technical only", "Scenario-based"])
    question_limit = st.slider("Number of questions", 2, 8, 4)
    provider = st.selectbox("LLM provider", ["Groq (free-tier available)", "OpenAI"])
    # Groq retires models periodically; check https://console.groq.com/docs/models for current ids.
    default_model = "openai/gpt-oss-20b" if provider.startswith("Groq") else "gpt-4o-mini"
    model_name = st.text_input("Model", value=default_model, key=f"model_{provider}")
    st.caption("Groq offers a limited free tier. Availability and rate limits may change.")
    if st.button("Start / Restart Interview", use_container_width=True):
        st.session_state.messages = []
        st.session_state.question_count = 0
        st.session_state.started = True
        st.session_state.finished = False
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "started" not in st.session_state:
    st.session_state.started = False
if "finished" not in st.session_state:
    st.session_state.finished = False

# Prompts define how the model should behave, not whether its output is guaranteed.
SYSTEM = """You are a helpful and professional technical interviewer.
Role: {role}. Experience: {experience}. Difficulty: {difficulty}.
Interview type: {interview_type}. Total questions: {question_limit}.
Ask one concise question at a time, appropriate to the role and difficulty.
After a candidate answer, give brief actionable feedback, a better-answer tip,
and then ask exactly one next question, unless the interview is complete.
Keep the tone supportive, factually cautious, and technically accurate.
Do not claim to have evaluated an answer you have not seen.
Do not invent personal candidate details."""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{request}"),
])

config = (role, experience, difficulty, interview_type, question_limit, provider, model_name)
if "config" in st.session_state and st.session_state.config != config:
    st.info("Settings changed. Click Start / Restart Interview to apply them to a new interview.")
else:
    st.session_state.config = config

key_name = "GROQ_API_KEY" if provider.startswith("Groq") else "OPENAI_API_KEY"
api_key = os.getenv(key_name)
if not api_key:
    try:
        api_key = st.secrets.get(key_name)
    except (FileNotFoundError, KeyError):
        pass

if not api_key:
    st.warning(f"Set {key_name} as an environment variable or Streamlit secret to use {provider}. Never paste keys into source code.")

for msg in st.session_state.messages:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content)

@st.cache_resource(show_spinner=False)
def build_model(provider_name: str, name: str, key: str):
    if provider_name.startswith("Groq"):
        return ChatGroq(model=name, api_key=key, temperature=0.3)
    return ChatOpenAI(model=name, api_key=key, temperature=0.3)

def ask_model(request: str):
    chain = prompt | build_model(provider, model_name, api_key)
    return chain.invoke({"role": role, "experience": experience,
                         "difficulty": difficulty, "interview_type": interview_type,
                         "question_limit": question_limit,
                         "history": st.session_state.messages,
                         "request": request}).content

if st.session_state.started and not st.session_state.messages and api_key:
    with st.spinner("Preparing your first question..."):
        try:
            reply = ask_model("Begin the interview. Ask question 1 only. Do not give the answer.")
            st.session_state.messages.append(AIMessage(content=reply))
            st.session_state.question_count = 1
            st.rerun()
        except Exception as exc:
            st.error(f"Unable to start interview: {type(exc).__name__}. Check API key, model and connection.")
            st.exception(exc)

if st.session_state.started and st.session_state.question_count >= question_limit:
    st.caption("Final question reached. Submit your last answer to receive the final feedback.")

answer = st.chat_input("Type your interview answer...", disabled=(not st.session_state.started or st.session_state.finished or not api_key or not st.session_state.messages))
if answer and answer.strip():
    st.session_state.messages.append(HumanMessage(content=answer.strip()))
    with st.spinner("Reviewing your answer..."):
        try:
            if st.session_state.question_count >= question_limit:
                reply = ask_model("Provide brief feedback on the candidate's latest answer, then a concise interview summary with 3 improvement suggestions. Do NOT ask another question.")
                st.session_state.finished = True
            else:
                reply = ask_model("Give brief feedback on the latest answer, then ask the next question only.")
                st.session_state.question_count += 1
            st.session_state.messages.append(AIMessage(content=reply))
            st.rerun()
        except Exception as exc:
            st.session_state.messages.pop()  # avoid duplicate answer after model failure
            st.error(f"Request failed: {type(exc).__name__}. Retry after checking your configuration.")
            st.exception(exc)
if st.session_state.finished:
    st.success("Interview complete. Restart to practice a new interview.")
