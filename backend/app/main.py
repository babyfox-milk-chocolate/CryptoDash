from fastapi import FastAPI
from app.api.routes import auth, coins, watchlist
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title='CryptoDash.IO')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],   
    allow_headers=["*"],   
)

app.include_router(auth.router, prefix='/api')
app.include_router(coins.router, prefix='/api')
app.include_router(watchlist.router, prefix='/api')

@app.get('/health')
async def health():
    return {'status': 'ok'}

