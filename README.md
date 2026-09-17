# Veridian IT Copilot

A lightweight Streamlit prototype for AIONOS Assignment 2 (Internal IT Support Agent).

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Included capabilities

- Policy-grounded routing using the supplied Veridian knowledge base
- Risk, priority, status and approval-route signals
- Clarification handling for vague requests
- Ticket preview and JSON export (not a real submission)
- Operations overview for all 15 requests
- Evaluation Lab for the supplied request set
- Searchable Policy Explorer

## Important limitations

- This is a transparent prototype, not a production ITSM integration.
- It does not send emails, create real tickets, grant access or contact Security/Finance.
- Classification is lightweight keyword/rule based; an LLM/RAG integration can be added later if credentials and an approved provider are available.
- Only the supplied Veridian data should be used during the assignment demo.
