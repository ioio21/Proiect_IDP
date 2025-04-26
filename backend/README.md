
# Backend

### Pasi instalare

1. Creare mediu de lucru
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instalare biblioteci
```bash
pip3 install -r backend/requirements.txt
```

### Rulare

#### Autentificare si autorizare
Din rootul proiectului:
```bash
uvicorn backend.src.auth:app --reload
```

Inregistrare utilizator:
```bash
curl -X 'POST' 'http://127.0.0.1:8000/register/' -H 'Content-Type: application/json' -d '{"username": "test", "password": "test"}'
```

Logare:
```bash
curl -X 'POST' 'http://127.0.0.1:8000/login/' -H 'Content-Type: application/json' -d '{"username": "test", "password": "test"}'
```

Accesare cai:
```bash
curl -X 'GET' 'http://127.0.0.1:8000/admin/'      -H 'Authorization: Bearer <token>'
```

### Mod de lucru
Lintare:
```
ruff check backend/
```
```
ruff check --fix
```

#### Autentificare si autorizare
Toate caile creeate sunt ca default publice. Daca se doreste ca userul sa fie autentificat cand acceseaza ruta se va adauga decoratorul `authenticate_user`.

Exemplu:
```python3
@app.get("/protected/")
@authenticate_user
async def protected_route(request: Request):
    user = request.state.user
    return {"message": f"Hello, {user['username']}. You have access to this protected route."}
```

Daca se doreste ca o cale sa fie disponibila doar unor utilizatori cu anumite roluri se va adauga in plus si decoratorul `authorize_roles`.

Exemplu:
```python3
@app.get("/admin/")
@authenticate_user
@authorize_roles("admin", "superadmin")
async def admin_route(request: Request):
    return {"message": "Hello, admin. You have access to this admin route."}
```

Acest serviciu are nevoie de urmatoarele chei. `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.