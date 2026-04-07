from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime
import sqlite3, io, csv, os, httpx, asyncio, base64, json, hashlib, secrets

app = FastAPI(title="Sistema de Gastos - Pertrak", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH       = "gastos.db"
BOT_TOKEN     = "8632601955:AAH3u0UXOcSRh8mLgfxdaGwNviIfQOAsASo"
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "")
TELEGRAM_API  = f"https://api.telegram.org/bot{BOT_TOKEN}"

CATEGORIAS = [
    "Refrigerio", "Viáticos", "Transporte", "Combustible",
    "Alojamiento", "Papelería", "Herramientas", "Telefonía",
    "Representación", "Otros"
]

METODOS_PAGO = [
    "Efectivo", "Tarjeta de crédito", "Tarjeta de débito",
    "Transferencia", "Otros"
]

security = HTTPBearer(auto_error=False)

# ─────────────────────────────────────────
# Base de datos
# ─────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            nombre     TEXT NOT NULL,
            rol        TEXT DEFAULT 'empleado',
            activo     INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token      TEXT PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuarios(id),
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS empleados (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE,
            nombre      TEXT NOT NULL,
            email       TEXT,
            activo      INTEGER DEFAULT 1,
            created_at  TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS gastos (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id   INTEGER REFERENCES empleados(id),
            usuario_id    INTEGER REFERENCES usuarios(id),
            fecha         TEXT NOT NULL,
            monto         REAL NOT NULL,
            moneda        TEXT DEFAULT 'ARS',
            categoria     TEXT NOT NULL,
            metodo_pago   TEXT DEFAULT 'Efectivo',
            descripcion   TEXT,
            nro_tarjeta   TEXT,
            estado        TEXT DEFAULT 'pendiente',
            created_at    TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS bot_states (
            chat_id    TEXT PRIMARY KEY,
            step       TEXT,
            data       TEXT,
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        );
    """)
    # Crear usuario admin por defecto si no existe
    admin = conn.execute("SELECT id FROM usuarios WHERE username='admin'").fetchone()
    if not admin:
        conn.execute(
            "INSERT INTO usuarios (username,password,nombre,rol) VALUES (?,?,?,?)",
            ("admin", hash_password("admin123"), "Administrador", "admin")
        )
        conn.commit()
    conn.close()

init_db()

# ─────────────────────────────────────────
# Auth
# ─────────────────────────────────────────
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(401, "No autenticado")
    token = credentials.credentials
    conn = get_db()
    row = conn.execute(
        "SELECT u.* FROM sessions s JOIN usuarios u ON s.usuario_id=u.id WHERE s.token=? AND u.activo=1",
        (token,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(401, "Token inválido o expirado")
    return dict(row)

def require_admin(user=Depends(get_current_user)):
    if user["rol"] != "admin":
        raise HTTPException(403, "Se requiere rol administrador")
    return user

# ─────────────────────────────────────────
# Estado del bot en DB
# ─────────────────────────────────────────
def get_state(chat_id: str) -> dict:
    conn = get_db()
    row = conn.execute("SELECT step, data FROM bot_states WHERE chat_id=?", (chat_id,)).fetchone()
    conn.close()
    if not row or not row["step"]:
        return {}
    return {"step": row["step"], "data": json.loads(row["data"] or "{}")}

def set_state(chat_id: str, step: str, data: dict):
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO bot_states (chat_id,step,data,updated_at) VALUES (?,?,?,datetime('now','localtime'))",
        (chat_id, step, json.dumps(data))
    )
    conn.commit()
    conn.close()

def clear_state(chat_id: str):
    conn = get_db()
    conn.execute("DELETE FROM bot_states WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class UsuarioCreate(BaseModel):
    username: str
    password: str
    nombre: str
    rol: str = "empleado"

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[str] = None
    activo: Optional[int] = None

class EmpleadoCreate(BaseModel):
    telegram_id: Optional[str] = None
    nombre: str
    email: Optional[str] = None

class GastoCreate(BaseModel):
    empleado_id: Optional[int] = None
    fecha: str
    monto: float
    moneda: str = "ARS"
    categoria: str
    metodo_pago: str = "Efectivo"
    descripcion: Optional[str] = None
    nro_tarjeta: Optional[str] = None

    @validator('empleado_id', pre=True)
    def empty_empleado_id_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v

class GastoUpdate(BaseModel):
    empleado_id: Optional[int] = None
    fecha: Optional[str] = None
    monto: Optional[float] = None
    moneda: Optional[str] = None
    categoria: Optional[str] = None
    metodo_pago: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None

    @validator('empleado_id', pre=True)
    def empty_empleado_id_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v

# ─────────────────────────────────────────
# AUTH ENDPOINTS
# ─────────────────────────────────────────
@app.post("/auth/login", tags=["Auth"])
def login(req: LoginRequest):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM usuarios WHERE username=? AND password=? AND activo=1",
        (req.username, hash_password(req.password))
    ).fetchone()
    if not user:
        conn.close()
        raise HTTPException(401, "Usuario o contraseña incorrectos")
    token = secrets.token_hex(32)
    conn.execute("INSERT INTO sessions (token, usuario_id) VALUES (?,?)", (token, user["id"]))
    conn.commit()
    conn.close()
    return {"token": token, "nombre": user["nombre"], "rol": user["rol"], "username": user["username"]}

@app.post("/auth/logout", tags=["Auth"])
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials:
        conn = get_db()
        conn.execute("DELETE FROM sessions WHERE token=?", (credentials.credentials,))
        conn.commit()
        conn.close()
    return {"mensaje": "Sesión cerrada"}

@app.get("/auth/me", tags=["Auth"])
def me(user=Depends(get_current_user)):
    return {"id": user["id"], "username": user["username"], "nombre": user["nombre"], "rol": user["rol"]}

# ─────────────────────────────────────────
# USUARIOS (solo admin)
# ─────────────────────────────────────────
@app.post("/usuarios", tags=["Usuarios"])
def crear_usuario(u: UsuarioCreate, admin=Depends(require_admin)):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO usuarios (username,password,nombre,rol) VALUES (?,?,?,?)",
            (u.username, hash_password(u.password), u.nombre, u.rol)
        )
        conn.commit()
        row = conn.execute("SELECT id,username,nombre,rol,activo FROM usuarios WHERE username=?", (u.username,)).fetchone()
        return dict(row)
    except sqlite3.IntegrityError:
        raise HTTPException(400, f"El usuario '{u.username}' ya existe")
    finally:
        conn.close()

@app.get("/usuarios", tags=["Usuarios"])
def listar_usuarios(admin=Depends(require_admin)):
    conn = get_db()
    rows = conn.execute("SELECT id,username,nombre,rol,activo,created_at FROM usuarios ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.put("/usuarios/{uid}", tags=["Usuarios"])
def actualizar_usuario(uid: int, u: UsuarioUpdate, admin=Depends(require_admin)):
    conn = get_db()
    data = u.dict(exclude_none=True)
    if "password" in data:
        data["password"] = hash_password(data["password"])
    if data:
        sets = ", ".join(f"{k}=?" for k in data)
        conn.execute(f"UPDATE usuarios SET {sets} WHERE id=?", list(data.values())+[uid])
        conn.commit()
    row = conn.execute("SELECT id,username,nombre,rol,activo FROM usuarios WHERE id=?", (uid,)).fetchone()
    conn.close()
    return dict(row)

@app.delete("/usuarios/{uid}", tags=["Usuarios"])
def eliminar_usuario(uid: int, admin=Depends(require_admin)):
    conn = get_db()
    conn.execute("UPDATE usuarios SET activo=0 WHERE id=?", (uid,))
    conn.commit()
    conn.close()
    return {"mensaje": "Usuario desactivado"}

# ─────────────────────────────────────────
# EMPLEADOS
# ─────────────────────────────────────────
@app.post("/empleados", tags=["Empleados"])
def crear_empleado(e: EmpleadoCreate, user=Depends(get_current_user)):
    conn = get_db()
    try:
        conn.execute("INSERT INTO empleados (telegram_id,nombre,email) VALUES (?,?,?)",
                     (e.telegram_id, e.nombre, e.email))
        conn.commit()
        row = conn.execute("SELECT * FROM empleados WHERE nombre=? ORDER BY id DESC LIMIT 1", (e.nombre,)).fetchone()
        return dict(row)
    except sqlite3.IntegrityError:
        raise HTTPException(400, "Ya existe un empleado con ese Telegram ID")
    finally:
        conn.close()

@app.get("/empleados", tags=["Empleados"])
def listar_empleados(user=Depends(get_current_user)):
    conn = get_db()
    rows = conn.execute("SELECT * FROM empleados WHERE activo=1 ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.delete("/empleados/{eid}", tags=["Empleados"])
def eliminar_empleado(eid: int, admin=Depends(require_admin)):
    conn = get_db()
    conn.execute("UPDATE empleados SET activo=0 WHERE id=?", (eid,))
    conn.commit()
    conn.close()
    return {"mensaje": "Empleado desactivado"}

# ─────────────────────────────────────────
# GASTOS
# ─────────────────────────────────────────
@app.post("/gastos", tags=["Gastos"])
def crear_gasto(g: GastoCreate, user=Depends(get_current_user)):
    if g.categoria not in CATEGORIAS:
        raise HTTPException(400, "Categoría inválida.")
    if g.metodo_pago not in METODOS_PAGO:
        raise HTTPException(400, "Método de pago inválido.")
    conn = get_db()
    conn.execute(
        "INSERT INTO gastos (empleado_id,usuario_id,fecha,monto,moneda,categoria,metodo_pago,descripcion,nro_tarjeta) VALUES (?,?,?,?,?,?,?,?,?)",
        (g.empleado_id, user["id"], g.fecha, g.monto, g.moneda, g.categoria, g.metodo_pago, g.descripcion, g.nro_tarjeta)
    )
    conn.commit()
    row = conn.execute(
        """SELECT g.*, 
           COALESCE(e.nombre, u.nombre) AS empleado 
           FROM gastos g 
           LEFT JOIN empleados e ON g.empleado_id=e.id 
           LEFT JOIN usuarios u ON g.usuario_id=u.id
           ORDER BY g.id DESC LIMIT 1"""
    ).fetchone()
    conn.close()
    return dict(row)

@app.get("/gastos", tags=["Gastos"])
def listar_gastos(
    empleado_id: Optional[int] = None,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    categoria: Optional[str] = None,
    metodo_pago: Optional[str] = None,
    moneda: Optional[str] = None,
    estado: Optional[str] = None,
    user=Depends(get_current_user)
):
    conn = get_db()
    sql = """SELECT g.*, COALESCE(e.nombre, u.nombre) AS empleado
             FROM gastos g
             LEFT JOIN empleados e ON g.empleado_id=e.id
             LEFT JOIN usuarios u ON g.usuario_id=u.id
             WHERE 1=1"""
    params = []
    # Empleados solo ven sus propios gastos
    if user["rol"] == "empleado":
        sql += " AND g.usuario_id=?"; params.append(user["id"])
    if empleado_id: sql += " AND g.empleado_id=?"; params.append(empleado_id)
    if desde:       sql += " AND g.fecha>=?";       params.append(desde)
    if hasta:       sql += " AND g.fecha<=?";       params.append(hasta)
    if categoria:   sql += " AND g.categoria=?";    params.append(categoria)
    if metodo_pago: sql += " AND g.metodo_pago=?";  params.append(metodo_pago)
    if moneda:      sql += " AND g.moneda=?";       params.append(moneda)
    if estado:      sql += " AND g.estado=?";       params.append(estado)
    sql += " ORDER BY g.fecha DESC, g.id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.put("/gastos/{gid}", tags=["Gastos"])
def actualizar_gasto(gid: int, g: GastoUpdate, user=Depends(get_current_user)):
    conn = get_db()
    row = conn.execute("SELECT * FROM gastos WHERE id=?", (gid,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Gasto no encontrado")
    # Empleados solo pueden editar sus propios gastos pendientes
    if user["rol"] == "empleado":
        if row["usuario_id"] != user["id"]:
            conn.close()
            raise HTTPException(403, "No podés editar gastos de otros")
        if row["estado"] != "pendiente":
            conn.close()
            raise HTTPException(403, "Solo podés editar gastos pendientes")
    data = g.dict(exclude_none=True)
    if data:
        sets = ", ".join(f"{k}=?" for k in data)
        conn.execute(f"UPDATE gastos SET {sets} WHERE id=?", list(data.values())+[gid])
        conn.commit()
    row = conn.execute(
        "SELECT g.*, COALESCE(e.nombre,u.nombre) AS empleado FROM gastos g LEFT JOIN empleados e ON g.empleado_id=e.id LEFT JOIN usuarios u ON g.usuario_id=u.id WHERE g.id=?",
        (gid,)
    ).fetchone()
    conn.close()
    return dict(row)

@app.delete("/gastos/{gid}", tags=["Gastos"])
def eliminar_gasto(gid: int, admin=Depends(require_admin)):
    conn = get_db()
    conn.execute("DELETE FROM gastos WHERE id=?", (gid,))
    conn.commit()
    conn.close()
    return {"mensaje": "Gasto eliminado"}

# ─────────────────────────────────────────
# REPORTES
# ─────────────────────────────────────────
@app.get("/resumen", tags=["Reportes"])
def resumen(desde: Optional[str] = None, hasta: Optional[str] = None, user=Depends(get_current_user)):
    conn = get_db()
    params = []
    where = "WHERE 1=1"
    if user["rol"] == "empleado":
        where += " AND usuario_id=?"; params.append(user["id"])
    if desde: where += " AND fecha>=?"; params.append(desde)
    if hasta: where += " AND fecha<=?"; params.append(hasta)
    total_ars = conn.execute(f"SELECT COALESCE(SUM(monto),0) FROM gastos {where} AND moneda='ARS'", params).fetchone()[0]
    total_usd = conn.execute(f"SELECT COALESCE(SUM(monto),0) FROM gastos {where} AND moneda='USD'", params).fetchone()[0]
    por_cat   = conn.execute(f"SELECT categoria,moneda,SUM(monto) as total,COUNT(*) as qty FROM gastos {where} GROUP BY categoria,moneda ORDER BY total DESC", params).fetchall()
    por_metodo = conn.execute(f"SELECT metodo_pago,SUM(monto) as total,COUNT(*) as qty FROM gastos {where} AND moneda='ARS' GROUP BY metodo_pago ORDER BY total DESC", params).fetchall()
    por_emp   = conn.execute(f"SELECT COALESCE(e.nombre,u.nombre) as nombre,g.moneda,SUM(g.monto) as total,COUNT(*) as qty FROM gastos g LEFT JOIN empleados e ON g.empleado_id=e.id LEFT JOIN usuarios u ON g.usuario_id=u.id {where.replace('WHERE','WHERE g.')} GROUP BY nombre,g.moneda ORDER BY total DESC", params).fetchall()
    por_mes   = conn.execute(f"SELECT substr(fecha,1,7) as mes,moneda,SUM(monto) as total FROM gastos {where} GROUP BY mes,moneda ORDER BY mes DESC", params).fetchall()
    conn.close()
    return {
        "total_ars": round(total_ars, 2),
        "total_usd": round(total_usd, 2),
        "por_categoria": [dict(r) for r in por_cat],
        "por_metodo_pago": [dict(r) for r in por_metodo],
        "por_empleado":  [dict(r) for r in por_emp],
        "por_mes":       [dict(r) for r in por_mes],
    }

@app.get("/exportar/excel", tags=["Reportes"])
def exportar_excel(desde: Optional[str] = None, hasta: Optional[str] = None, user=Depends(get_current_user)):
    conn = get_db()
    sql = """SELECT g.fecha, COALESCE(e.nombre,u.nombre) as empleado, g.categoria, g.metodo_pago,
             g.descripcion, g.monto, g.moneda, g.estado, g.created_at
             FROM gastos g LEFT JOIN empleados e ON g.empleado_id=e.id LEFT JOIN usuarios u ON g.usuario_id=u.id
             WHERE 1=1"""
    params = []
    if user["rol"] == "empleado":
        sql += " AND g.usuario_id=?"; params.append(user["id"])
    if desde: sql += " AND g.fecha>=?"; params.append(desde)
    if hasta: sql += " AND g.fecha<=?"; params.append(hasta)
    sql += " ORDER BY g.fecha DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fecha","Empleado","Categoría","Método de Pago","Descripción","Monto","Moneda","Estado","Registrado"])
    for r in rows:
        writer.writerow(list(r))
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=gastos_{date.today()}.csv"}
    )

@app.get("/categorias", tags=["Config"])
def get_categorias():
    return CATEGORIAS

@app.get("/metodos-pago", tags=["Config"])
def get_metodos_pago():
    return METODOS_PAGO

# ─────────────────────────────────────────
# CLAUDE VISION
# ─────────────────────────────────────────
async def analizar_ticket(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    if len(image_bytes) > 1_000_000:
        image_bytes = image_bytes[:1_000_000]
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    payload = {
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 512,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                {"type": "text", "text": (
                    "Analizá este ticket/comprobante de pago y extraé los siguientes datos en formato JSON estricto:\n"
                    "{\n"
                    '  "monto": <número con decimales, solo el total final>,\n'
                    '  "moneda": <"ARS" o "USD">,\n'
                    '  "fecha": <"YYYY-MM-DD" — la fecha de emisión del ticket/comprobante, NO la fecha de inicio de actividades del comercio — usá el año 2026 si no se ve claramente>,\n'
                    '  "descripcion": <descripción breve del comercio, máximo 60 caracteres>,\n'
                    '  "metodo_pago": <"Efectivo", "Tarjeta de crédito", "Tarjeta de débito", "Transferencia" o "Otros">\n'
                    "}\n"
                    "Si no podés leer algún campo, ponelo como null. Respondé SOLO el JSON."
                )}
            ]
        }]
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json=payload
        )
        if not r.is_success:
            raise Exception(f"API error {r.status_code}: {r.text}")
        text = r.json()["content"][0]["text"].strip()
        text = text.replace("```json","").replace("```","").strip()
        return json.loads(text)

# ─────────────────────────────────────────
# TELEGRAM BOT
# ─────────────────────────────────────────
async def send_msg(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API}/sendMessage", json=payload)

def make_keyboard(options, columns=2):
    keyboard = []
    for i in range(0, len(options), columns):
        keyboard.append([{"text": o} for o in options[i:i+columns]])
    return {"keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}

def remove_keyboard():
    return {"remove_keyboard": True}

async def get_file_bytes(file_id: str) -> tuple:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{TELEGRAM_API}/getFile?file_id={file_id}")
        file_path = r.json()["result"]["file_path"]
        mime = "image/png" if file_path.endswith(".png") else "image/jpeg"
        file_r = await client.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}")
        return file_r.content, mime

async def process_update(update: dict):
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return
    chat_id   = str(msg["chat"]["id"])
    text      = msg.get("text","").strip()
    photo     = msg.get("photo")
    document  = msg.get("document")
    from_user = msg.get("from", {})
    tg_name   = (from_user.get("first_name","") + " " + from_user.get("last_name","")).strip()

    conn = get_db()
    emp = conn.execute("SELECT * FROM empleados WHERE telegram_id=?", (chat_id,)).fetchone()
    if not emp:
        conn.execute("INSERT OR IGNORE INTO empleados (telegram_id,nombre) VALUES (?,?)",
                     (chat_id, tg_name or f"Usuario {chat_id}"))
        conn.commit()
        emp = conn.execute("SELECT * FROM empleados WHERE telegram_id=?", (chat_id,)).fetchone()
    emp = dict(emp)
    conn.close()

    state = get_state(chat_id)

    if text in ("/start", "/ayuda", "/help"):
        clear_state(chat_id)
        await send_msg(chat_id,
            f"👋 Hola <b>{emp['nombre']}</b>!\n\n"
            "📸 <b>Mandá una foto del ticket</b> → registro automático\n"
            "💸 /nuevo → Cargar manualmente\n"
            "📋 /misgastos → Ver tus gastos\n"
            "❓ /ayuda → Esta ayuda",
            make_keyboard(["/nuevo", "/misgastos"])
        )
        return

    if text == "/misgastos":
        conn = get_db()
        rows = conn.execute(
            "SELECT fecha,categoria,metodo_pago,monto,moneda,descripcion FROM gastos WHERE empleado_id=? ORDER BY fecha DESC LIMIT 20",
            (emp["id"],)
        ).fetchall()
        conn.close()
        if not rows:
            await send_msg(chat_id, "📭 No tenés gastos registrados todavía.")
        else:
            total_ars = sum(r["monto"] for r in rows if r["moneda"]=="ARS")
            total_usd = sum(r["monto"] for r in rows if r["moneda"]=="USD")
            lines = ["📋 <b>Tus últimos gastos:</b>\n"]
            for r in rows:
                mp = f" [{r['metodo_pago']}]" if r["metodo_pago"] else ""
                lines.append(f"• {r['fecha']} | {r['categoria']}{mp} | <b>{r['moneda']} ${r['monto']:,.2f}</b>{' — '+r['descripcion'] if r['descripcion'] else ''}")
            lines.append(f"\n💰 <b>Total ARS: ${total_ars:,.2f}</b>")
            if total_usd:
                lines.append(f"💵 <b>Total USD: ${total_usd:,.2f}</b>")
            await send_msg(chat_id, "\n".join(lines))
        return

    # FOTO
    if photo or (document and document.get("mime_type","").startswith("image/")):
        await send_msg(chat_id, "🔍 Analizando tu ticket con IA, un momento…", remove_keyboard())
        try:
            file_id = photo[-1]["file_id"] if photo else document["file_id"]
            img_bytes, mime = await get_file_bytes(file_id)
            datos = await analizar_ticket(img_bytes, mime)
            monto = datos.get("monto")
            moneda = datos.get("moneda") or "ARS"
            fecha = datos.get("fecha") or date.today().isoformat()
            descripcion = datos.get("descripcion") or ""
            metodo_pago = datos.get("metodo_pago") or "Efectivo"
            if metodo_pago not in METODOS_PAGO:
                metodo_pago = "Efectivo"
            if not monto:
                await send_msg(chat_id, "⚠️ No pude leer el monto. Intentá de nuevo o usá /nuevo.")
                return
            set_state(chat_id, "categoria_ticket", {
                "empleado_id": emp["id"], "fecha": fecha, "monto": monto,
                "moneda": moneda, "descripcion": descripcion, "metodo_pago": metodo_pago
            })
            await send_msg(chat_id,
                f"✅ <b>Ticket leído:</b>\n\n"
                f"📅 {fecha} | 💰 {moneda} ${monto:,.2f}\n"
                f"💳 Método: <b>{metodo_pago}</b>\n"
                f"📝 {descripcion or '—'}\n\n"
                "¿En qué categoría lo registramos?",
                make_keyboard(CATEGORIAS, 2)
            )
        except Exception as ex:
            await send_msg(chat_id, f"⚠️ No pude procesar la imagen: {str(ex)}\nUsá /nuevo para cargarlo manualmente.")
        return

    if state.get("step") == "categoria_ticket":
        cat_match = next((c for c in CATEGORIAS if c.lower() == text.lower() or c in text or text in c), None)
        if not cat_match:
            await send_msg(chat_id, "⚠️ Elegí una categoría.", make_keyboard(CATEGORIAS, 2))
            return
        d = state["data"]
        d["categoria"] = cat_match
        set_state(chat_id, "moneda_ticket", d)
        await send_msg(chat_id,
            f"🗂 <b>Categoría:</b> {cat_match}\n\n"
            f"💱 <b>Moneda actual:</b> {d['moneda']}\n"
            f"¿Es correcta? Elegí la moneda:",
            make_keyboard(["ARS 🇦🇷", "USD 🇺🇸"], 2)
        )
        return

    if text == "/nuevo":
        set_state(chat_id, "fecha", {"empleado_id": emp["id"]})
        await send_msg(chat_id, "📅 <b>Paso 1/6</b> — Fecha del gasto (YYYY-MM-DD o <b>hoy</b>):", remove_keyboard())
        return

    if state.get("step") == "moneda_ticket":
        moneda = "ARS" if "ARS" in text else "USD" if "USD" in text else None
        if not moneda:
            await send_msg(chat_id, "⚠️ Elegí ARS o USD.", make_keyboard(["ARS 🇦🇷", "USD 🇺🇸"], 2))
            return
        d = state["data"]
        d["moneda"] = moneda
        set_state(chat_id, "metodo_pago_ticket", d)
        await send_msg(chat_id,
            f"💱 <b>Moneda:</b> {moneda}\n\n"
            f"💳 <b>Método actual:</b> {d['metodo_pago']}\n"
            f"¿Es correcto? Elegí el método de pago:",
            make_keyboard(METODOS_PAGO, 2)
        )
        return

    if state.get("step") == "metodo_pago_ticket":
        mp_match = next((m for m in METODOS_PAGO if m.lower() == text.lower() or m in text or text in m), None)
        if not mp_match:
            await send_msg(chat_id, "⚠️ Elegí un método de pago.", make_keyboard(METODOS_PAGO, 2))
            return
        try:
            d = state["data"]
            monto = float(d["monto"])
            conn = get_db()
            conn.execute(
                "INSERT INTO gastos (empleado_id,fecha,monto,moneda,categoria,metodo_pago,descripcion) VALUES (?,?,?,?,?,?,?)",
                (d["empleado_id"], d["fecha"], monto, d["moneda"], d["categoria"], mp_match, d.get("descripcion"))
            )
            conn.commit()
            conn.close()
            clear_state(chat_id)
            await send_msg(chat_id,
                f"🎉 <b>Gasto registrado:</b>\n"
                f"📅 {d['fecha']} | 🗂 {d['categoria']}\n"
                f"💰 {d['moneda']} ${monto:,.2f} | 💳 {mp_match}\n"
                f"📝 {d.get('descripcion') or '—'}\n\n¿Tenés otro ticket?",
                make_keyboard(["/nuevo", "/misgastos"])
            )
        except Exception as ex:
            clear_state(chat_id)
            await send_msg(chat_id,
                f"⚠️ Error al registrar: {str(ex)}\nUsá /nuevo para intentar de nuevo.",
                make_keyboard(["/nuevo", "/misgastos"])
            )
        return

    if state.get("step") == "fecha":
        fecha = date.today().isoformat() if text.lower() == "hoy" else text
        try: datetime.strptime(fecha, "%Y-%m-%d")
        except:
            await send_msg(chat_id, "⚠️ Formato incorrecto. Usá YYYY-MM-DD o <b>hoy</b>.")
            return
        d = state["data"]; d["fecha"] = fecha
        set_state(chat_id, "categoria", d)
        await send_msg(chat_id, "🗂 <b>Paso 2/6</b> — Categoría:", make_keyboard(CATEGORIAS, 2))
        return

    if state.get("step") == "categoria":
        # Buscar coincidencia flexible (ignora mayúsculas/tildes parciales)
        cat_match = next((c for c in CATEGORIAS if c.lower() == text.lower() or c in text or text in c), None)
        if not cat_match:
            await send_msg(chat_id, "⚠️ Elegí una categoría de la lista.", make_keyboard(CATEGORIAS, 2))
            return
        d = state["data"]; d["categoria"] = cat_match
        set_state(chat_id, "metodo_pago", d)
        await send_msg(chat_id, "💳 <b>Paso 3/6</b> — Método de pago:", make_keyboard(METODOS_PAGO, 2))
        return

    if state.get("step") == "metodo_pago":
        mp_match = next((m for m in METODOS_PAGO if m.lower() == text.lower() or m in text or text in m), None)
        if not mp_match:
            await send_msg(chat_id, "⚠️ Elegí un método de pago.", make_keyboard(METODOS_PAGO, 2))
            return
        d = state["data"]; d["metodo_pago"] = mp_match
        set_state(chat_id, "moneda", d)
        await send_msg(chat_id, "💱 <b>Paso 4/6</b> — Moneda:", make_keyboard(["ARS 🇦🇷", "USD 🇺🇸"], 2))
        return

    if state.get("step") == "moneda":
        moneda = "ARS" if "ARS" in text else "USD" if "USD" in text else None
        if not moneda:
            await send_msg(chat_id, "⚠️ Elegí ARS o USD.", make_keyboard(["ARS 🇦🇷", "USD 🇺🇸"], 2))
            return
        d = state["data"]; d["moneda"] = moneda
        set_state(chat_id, "monto", d)
        await send_msg(chat_id, f"💰 <b>Paso 5/6</b> — Monto en {moneda}:", remove_keyboard())
        return

    if state.get("step") == "monto":
        try: monto = float(text.replace(",",".").replace("$","").strip())
        except:
            await send_msg(chat_id, "⚠️ Ingresá solo el número, ej: <b>1500.50</b>")
            return
        d = state["data"]; d["monto"] = monto
        set_state(chat_id, "descripcion", d)
        await send_msg(chat_id, "📝 <b>Paso 6/6</b> — Descripción (o <b>-</b> para omitir):", remove_keyboard())
        return

    if state.get("step") == "descripcion":
        desc = None if text == "-" else text
        d = state["data"]
        conn = get_db()
        conn.execute(
            "INSERT INTO gastos (empleado_id,fecha,monto,moneda,categoria,metodo_pago,descripcion) VALUES (?,?,?,?,?,?,?)",
            (d["empleado_id"], d["fecha"], d["monto"], d["moneda"], d["categoria"], d.get("metodo_pago","Efectivo"), desc)
        )
        conn.commit()
        conn.close()
        clear_state(chat_id)
        await send_msg(chat_id,
            f"✅ <b>Gasto registrado:</b>\n"
            f"📅 {d['fecha']} | 🗂 {d['categoria']}\n"
            f"💰 {d['moneda']} ${d['monto']:,.2f} | 💳 {d.get('metodo_pago','Efectivo')}\n"
            f"📝 {desc or '—'}\n\n¿Registrar otro?",
            make_keyboard(["/nuevo", "/misgastos"])
        )
        return

    await send_msg(chat_id, "🤖 Mandá una foto del ticket o usá los comandos:", make_keyboard(["/nuevo", "/misgastos"]))

@app.post("/webhook", tags=["Telegram"])
async def webhook(update: dict):
    asyncio.create_task(process_update(update))
    return {"ok": True}

@app.get("/setup-webhook", tags=["Telegram"])
async def setup_webhook(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{TELEGRAM_API}/setWebhook", json={"url": f"{url}/webhook"})
        return r.json()
