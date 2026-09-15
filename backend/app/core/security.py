from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import bcrypt
from app.core.config import settings



def hash_password(password: str) -> str:
    pw = password.encode('utf-8')[:72]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    pw = plain.encode('utf-8')[:72]
    return bcrypt.checkpw(pw, hashed.encode('utf-8'))


''' JWT '''
ALGORITHM = 'HS256'


def _create_token(subject: str, expire_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        'sub': subject, # кого идентифицирует токен. Id юзера
        'exp': now + expire_delta, # время протухания. Jose сам проверяет это поле и отвергает просроченный токен
        'iat': now, # когда выпущен
        'type': token_type # кастомное поле, чтобы отличать access от refresh 
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: int) -> str:
    return _create_token(
        subject=str(user_id),
        expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type='access'
    )


def create_refresh_token(user_id: int) -> str:
    return _create_token(
        subject=str(user_id),
        expire_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )

def decode_token(token: str) -> dict | None:
    # проверяет подпись и срок, возвращает payload или None
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
