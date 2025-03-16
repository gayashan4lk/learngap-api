# LearnGAP API

## Run

execute this command in the root directory after creating a vertual environment and installing dependencies.

```bash
uvicorn app.main:app --reload
```

if you run below command weired import errors will happen!!

```bash
uv run fastapi dev
```

[read more](https://stackoverflow.com/questions/60819376/fastapi-throws-an-error-error-loading-asgi-app-could-not-import-module-api)

## Important commands

### update requirements.txt file using uv

```bash
uv export --output-file requirements.txt
```

## Readings

### Resource 01

[Building Smarter APIs: A Guide to Integrating CrewAI with FastAPI](https://halilural5.medium.com/building-smarter-apis-a-guide-to-integrating-crewai-with-fastapi-e0f4b69cbb34)

[github repository for above article](https://github.com/halilural/multi-model-ai-agents/tree/master/crewai/url_insight_api)

https://freedium.cfd/https://halilural5.medium.com/building-smarter-apis-a-guide-to-integrating-crewai-with-fastapi-e0f4b69cbb34

### Resource 02

[Github repository](https://github.com/MuhammadAinurR/crewai-playground/blob/main/src/main.py)

### Resource 03

[Generated v0 ui](https://v0.dev/chat/personal-ai-tutor-app-DExqm8QELbZ?b=b_usC3PVgo619&p=0)
