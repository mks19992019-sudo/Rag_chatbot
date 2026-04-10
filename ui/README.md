# UI

This folder contains a standalone chat UI for the FastAPI app in `main.py`.

## Run it

1. Start the backend from the project root:

```bash
uvicorn main:app --reload
```

2. Start the UI server from the project root:

```bash
python ui/server.py
```

3. Open this in your browser:

```text
http://127.0.0.1:3000
```

## Notes

- The UI server proxies requests to `http://127.0.0.1:8000/chat` by default.
- You can change that with the `BACKEND_URL` environment variable if needed.
