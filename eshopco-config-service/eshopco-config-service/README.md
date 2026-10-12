# eShopCo Effective Config API

FastAPI service for merging configuration in this order: hardcoded defaults, `config.<APP_ENV>.yaml`, `.env`, OS `APP_*` variables, then repeated `?set=key=value` query parameters. `NUM_WORKERS` aliases to `workers`; `api_key` is always masked.

## Run locally

```bash
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

Test:

```text
http://127.0.0.1:8000/effective-config?set=port=9000&set=debug=true&set=workers=2
```

## Deploy on Render

1. Push these files to a GitHub repository.
2. In Render, create **New + → Blueprint** and select the repository containing `render.yaml`.
3. Deploy the service. Render will provide a public URL such as `https://<service-name>.onrender.com`.
4. Submit `https://<service-name>.onrender.com/effective-config` as the endpoint URL.

Do not submit the example URL; use the actual URL Render assigns.
