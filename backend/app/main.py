from fastapi import FastAPI
from app.api.routes import auth


app = FastAPI(title='CryptoDash.IO')
app.include_router(auth.router, prefix='/api')


@app.get('/health')
async def health():
    return {'status': 'ok'}

