# 🎯 AI Interview Coach

A simple Streamlit app that runs a mock technical interview using LangChain prompt templates.
It asks one question at a time, gives feedback on your answer, and ends with a summary.

**Class 7 | Soumya AI Vision** — LangChain Prompt Templates project.

## Features

- Pick role, experience, difficulty, interview type, and number of questions
- One question at a time, with feedback and a better-answer tip after each answer
- Final summary with 3 improvement suggestions
- Works with **Groq** (free tier available) or **OpenAI**

## Setup

1. Create a virtual environment and install the dependencies.

   On macOS, `pip` is often not on your PATH and the system Python is old, so
   use a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

   Or, if you have [uv](https://docs.astral.sh/uv/) installed (faster):

   ```bash
   uv venv --python 3.12
   uv pip install -r requirements.txt
   ```

2. Add your API key to `.env`:

   ```
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
   ```

   You only need the key for the provider you plan to use.
   - Groq key: https://console.groq.com/keys
   - OpenAI key: https://platform.openai.com/api-keys

3. Run the app:

   ```bash
   source .venv/bin/activate        # if not already active
   streamlit run streamlit_app_groq_openai.py
   ```

   It opens at http://localhost:8501

## How to use

1. Choose your settings in the sidebar.
2. Click **Start / Restart Interview**.
3. Type your answer in the chat box and press Enter.
4. Keep answering until the interview finishes, then restart to practise again.

## Default models

| Provider | Default model |
|---|---|
| Groq | `openai/gpt-oss-20b` |
| OpenAI | `gpt-4o-mini` |

You can type any other model name in the sidebar.

**Groq retires models.** If you see `NotFoundError: model_not_found`, the model
id no longer exists - it is not a key problem. Older versions of this tutorial
used `llama-3.1-8b-instant`, which has since been retired. List the ids your key
can currently use:

```bash
curl -s https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY" | python3 -m json.tool | grep '"id"'
```

## Notes

- `.env` is listed in `.gitignore` — never commit your keys.
- Deploying on Streamlit Cloud? Put the keys in **Settings → Secrets** instead of `.env`.
- Groq free-tier limits and model availability can change over time.
