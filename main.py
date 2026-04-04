from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import sqlite3, io, csv, os, httpx, asyncio, base64

app = FastAPI(title="Sistema de Gastos - Pertrak", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH      = "gastos.db"
BOT_TOKEN    = "8632601955:AAH3u0UXOcSRh8mLgfxdaGwNviIfQOAsASo"
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

CATEGORIAS = [
    "Refrigerio", "Viáticos", "Transporte", "Combustible",
    "Alojamiento", "Papelería", "Herramientas", "Telefonía",
    "Representación", "Otros"
]

# ─────────────────────────────────────────
# Base de datos
# ─────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS empleados (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE,
            nombre      TEXT NOT NULL,
            email       TEXT,
            activo      INTEGER DEFAULT 1,
            created_at  TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS gastos (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id  INTEGER REFERENCES empleados(id),
            fecha        TEXT NOT NULL,
            monto        REAL NOT NULL,
            moneda       TEXT DEFAULT 'ARS',
            categoria    TEXT NOT NULL,
            descripcion  TEXT,
            nro_tarjeta  TEXT,
            estado       TEXT DEFAULT 'pendiente',
            created_at   TEXT DEFAULT (datetime('now','localtime'))
        );
    """)
    conn.commit()
    conn.close()

init_db()

# ─────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────
class EmpleadoCreate(BaseModel):
    telegram_id: Optional[str] = None
    nombre: str
    email: Optional[str] = None

class GastoCreate(BaseModel):
    empleado_id: int
    fecha: str
    monto: float
    moneda: str = "ARS"
    categoria: str
    descripcion: Optional[str] = None
    nro_tarjeta: Optional[str] = None

class GastoUpdate(BaseModel):
    fecha: Optional[str] = None
    monto: Optional[float] = None
    moneda: Optional[str] = None
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None

# ─────────────────────────────────────────
# EMPLEADOS
# ─────────────────────────────────────────
@app.post("/empleados", tags=["Empleados"])
def crear_empleado(e: EmpleadoCreate):
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
def listar_empleados():
    conn = get_db()
    rows = conn.execute("SELECT * FROM empleados WHERE activo=1 ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.delete("/empleados/{eid}", tags=["Empleados"])
def eliminar_empleado(eid: int):
    conn = get_db()
    conn.execute("UPDATE empleados SET activo=0 WHERE id=?", (eid,))
    conn.commit()
    conn.close()
    return {"mensaje": "Empleado desactivado"}

# ─────────────────────────────────────────
# GASTOS
# ─────────────────────────────────────────
@app.post("/gastos", tags=["Gastos"])
def crear_gasto(g: GastoCreate):
    if g.categoria not in CATEGORIAS:
        raise HTTPException(400, f"Categoría inválida.")
    conn = get_db()
    emp = conn.execute("SELECT id FROM empleados WHERE id=?", (g.empleado_id,)).fetchone()
    if not emp:
        conn.close()
        raise HTTPException(404, "Empleado no encontrado")
    conn.execute(
        "INSERT INTO gastos (empleado_id,fecha,monto,moneda,categoria,descripcion,nro_tarjeta) VALUES (?,?,?,?,?,?,?)",
        (g.empleado_id, g.fecha, g.monto, g.moneda, g.categoria, g.descripcion, g.nro_tarjeta)
    )
    conn.commit()
    row = conn.execute(
        "SELECT g.*, e.nombre AS empleado FROM gastos g JOIN empleados e ON g.empleado_id=e.id ORDER BY g.id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return dict(row)

@app.get("/gastos", tags=["Gastos"])
def listar_gastos(
    empleado_id: Optional[int] = None,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    categoria: Optional[str] = None,
    moneda: Optional[str] = None,
    estado: Optional[str] = None
):
    conn = get_db()
    sql = "SELECT g.*, e.nombre AS empleado FROM gastos g JOIN empleados e ON g.empleado_id=e.id WHERE 1=1"
    params = []
    if empleado_id: sql += " AND g.empleado_id=?"; params.append(empleado_id)
    if desde:       sql += " AND g.fecha>=?";       params.append(desde)
    if hasta:       sql += " AND g.fecha<=?";       params.append(hasta)
    if categoria:   sql += " AND g.categoria=?";    params.append(categoria)
    if moneda:      sql += " AND g.moneda=?";       params.append(moneda)
    if estado:      sql += " AND g.estado=?";       params.append(estado)
    sql += " ORDER BY g.fecha DESC, g.id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.put("/gastos/{gid}", tags=["Gastos"])
def actualizar_gasto(gid: int, g: GastoUpdate):
    conn = get_db()
    row = conn.execute("SELECT * FROM gastos WHERE id=?", (gid,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Gasto no encontrado")
    data = g.dict(exclude_none=True)
    if data:
        sets = ", ".join(f"{k}=?" for k in data)
        conn.execute(f"UPDATE gastos SET {sets} WHERE id=?", list(data.values())+[gid])
        conn.commit()
    row = conn.execute(
        "SELECT g.*, e.nombre AS empleado FROM gastos g JOIN empleados e ON g.empleado_id=e.id WHERE g.id=?", (gid,)
    ).fetchone()
    conn.close()
    return dict(row)

@app.delete("/gastos/{gid}", tags=["Gastos"])
def eliminar_gasto(gid: int):
    conn = get_db()
    conn.execute("DELETE FROM gastos WHERE id=?", (gid,))
    conn.commit()
    conn.close()
    return {"mensaje": "Gasto eliminado"}

# ─────────────────────────────────────────
# REPORTES
# ─────────────────────────────────────────
@app.get("/resumen", tags=["Reportes"])
def resumen(desde: Optional[str] = None, hasta: Optional[str] = None):
    conn = get_db()
    params = []
    where = "WHERE 1=1"
    if desde: where += " AND fecha>=?"; params.append(desde)
    if hasta: where += " AND fecha<=?"; params.append(hasta)
    total_ars = conn.execute(f"SELECT COALESCE(SUM(monto),0) FROM gastos {where} AND moneda='ARS'", params).fetchone()[0]
    total_usd = conn.execute(f"SELECT COALESCE(SUM(monto),0) FROM gastos {where} AND moneda='USD'", params).fetchone()[0]
    por_cat   = conn.execute(f"SELECT categoria, moneda, SUM(monto) as total, COUNT(*) as qty FROM gastos {where} GROUP BY categoria, moneda ORDER BY total DESC", params).fetchall()
    por_emp   = conn.execute(f"SELECT e.nombre, g.moneda, SUM(g.monto) as total, COUNT(*) as qty FROM gastos g JOIN empleados e ON g.empleado_id=e.id {where.replace('WHERE','WHERE g.')} GROUP BY e.nombre, g.moneda ORDER BY total DESC", params).fetchall()
    por_mes   = conn.execute(f"SELECT substr(fecha,1,7) as mes, moneda, SUM(monto) as total FROM gastos {where} GROUP BY mes, moneda ORDER BY mes DESC", params).fetchall()
    conn.close()
    return {
        "total_ars": round(total_ars, 2),
        "total_usd": round(total_usd, 2),
        "por_categoria": [dict(r) for r in por_cat],
        "por_empleado":  [dict(r) for r in por_emp],
        "por_mes":       [dict(r) for r in por_mes],
    }

@app.get("/exportar/excel", tags=["Reportes"])
def exportar_excel(desde: Optional[str] = None, hasta: Optional[str] = None):
    conn = get_db()
    sql = "SELECT g.fecha, e.nombre, g.categoria, g.descripcion, g.monto, g.moneda, g.nro_tarjeta, g.estado, g.created_at FROM gastos g JOIN empleados e ON g.empleado_id=e.id WHERE 1=1"
    params = []
    if desde: sql += " AND g.fecha>=?"; params.append(desde)
    if hasta: sql += " AND g.fecha<=?"; params.append(hasta)
    sql += " ORDER BY g.fecha DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fecha","Empleado","Categoría","Descripción","Monto","Moneda","Nro Tarjeta","Estado","Registrado"])
    for r in rows:
        writer.writerow(list(r))
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=gastos_{date.today()}.csv"}
    )

@app.get("/categorias", tags=["Gastos"])
def get_categorias():
    return CATEGORIAS

# ─────────────────────────────────────────
# CLAUDE VISION — leer ticket desde imagen
# ─────────────────────────────────────────
async def analizar_ticket(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """Envía la imagen a Claude y extrae monto, fecha, descripción y moneda."""
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    payload = {
        "model": "claude-sonnet-4-5-20251015",
        "max_tokens": 512,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": mime_type, "data": image_b64}
                },
                {
                    "type": "text",
                    "text": (
                        "Analizá este ticket/comprobante de pago y extraé los siguientes datos en formato JSON estricto, sin texto adicional:\n"
                        "{\n"
                        '  "monto": <número con decimales, solo el total final>,\n'
                        '  "moneda": <"ARS" o "USD">,\n'
                        '  "fecha": <"YYYY-MM-DD" o null si no se ve>,\n'
                        '  "descripcion": <descripción breve del comercio o producto, máximo 60 caracteres>\n'
                        "}\n"
                        "Si no podés leer algún campo, ponelo como null. Respondé SOLO el JSON."
                    )
                }
            ]
        }]
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json=payload
        )
        r.raise_for_status()
        text = r.json()["content"][0]["text"].strip()
        # limpiar posibles backticks
        text = text.replace("```json","").replace("```","").strip()
        import json
        return json.loads(text)

# ─────────────────────────────────────────
# TELEGRAM BOT
# ─────────────────────────────────────────
user_state = {}

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

async def get_file_bytes(file_id: str) -> tuple[bytes, str]:
    """Descarga un archivo de Telegram y devuelve sus bytes y mime_type."""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{TELEGRAM_API}/getFile?file_id={file_id}")
        file_path = r.json()["result"]["file_path"]
        ext = file_path.split(".")[-1].lower()
        mime = "image/jpeg" if ext in ("jpg","jpeg") else "image/png" if ext == "png" else "image/jpeg"
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

    # Auto-registrar empleado
    conn = get_db()
    emp = conn.execute("SELECT * FROM empleados WHERE telegram_id=?", (chat_id,)).fetchone()
    if not emp:
        conn.execute("INSERT OR IGNORE INTO empleados (telegram_id,nombre) VALUES (?,?)",
                     (chat_id, tg_name or f"Usuario {chat_id}"))
        conn.commit()
        emp = conn.execute("SELECT * FROM empleados WHERE telegram_id=?", (chat_id,)).fetchone()
    emp = dict(emp)
    conn.close()

    state = user_state.get(chat_id, {})

    # ── /start o /ayuda ──
    if text in ("/start", "/ayuda", "/help"):
        user_state[chat_id] = {}
        await send_msg(chat_id,
            f"👋 Hola <b>{emp['nombre']}</b>!\n\n"
            "Soy el bot de gastos de <b>Pertrak</b>. Podés:\n\n"
            "📸 <b>Mandar una foto del ticket</b> → lo registro automáticamente\n"
            "💸 /nuevo → Cargar un gasto manualmente\n"
            "📋 /misgastos → Ver tus gastos del mes\n"
            "❓ /ayuda → Ver esta ayuda",
            make_keyboard(["/nuevo", "/misgastos"])
        )
        return

    # ── /misgastos ──
    if text == "/misgastos":
        conn = get_db()
        mes  = date.today().strftime("%Y-%m")
        rows = conn.execute(
            "SELECT fecha,categoria,monto,moneda,descripcion FROM gastos WHERE empleado_id=? AND substr(fecha,1,7)=? ORDER BY fecha DESC",
            (emp["id"], mes)
        ).fetchall()
        conn.close()
        if not rows:
            await send_msg(chat_id, "📭 No tenés gastos registrados este mes.")
        else:
            total_ars = sum(r["monto"] for r in rows if r["moneda"]=="ARS")
            total_usd = sum(r["monto"] for r in rows if r["moneda"]=="USD")
            lines = [f"📋 <b>Tus gastos de {mes}:</b>\n"]
            for r in rows:
                lines.append(f"• {r['fecha']} | {r['categoria']} | <b>{r['moneda']} ${r['monto']:,.2f}</b>{' — '+r['descripcion'] if r['descripcion'] else ''}")
            lines.append(f"\n💰 <b>Total ARS: ${total_ars:,.2f}</b>")
            if total_usd:
                lines.append(f"💵 <b>Total USD: ${total_usd:,.2f}</b>")
            await send_msg(chat_id, "\n".join(lines))
        return

    # ── FOTO DE TICKET → Claude Vision ──
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

            if not monto:
                await send_msg(chat_id,
                    "⚠️ No pude leer el monto del ticket. "
                    "Intentá con mejor iluminación o usá /nuevo para cargarlo manualmente."
                )
                return

            # Guardar datos extraídos y pedir solo la categoría
            user_state[chat_id] = {
                "step": "categoria_ticket",
                "data": {
                    "empleado_id": emp["id"],
                    "fecha": fecha,
                    "monto": monto,
                    "moneda": moneda,
                    "descripcion": descripcion
                }
            }

            await send_msg(chat_id,
                f"✅ <b>Ticket leído correctamente:</b>\n\n"
                f"📅 Fecha: <b>{fecha}</b>\n"
                f"💰 Monto: <b>{moneda} ${monto:,.2f}</b>\n"
                f"📝 Descripción: <b>{descripcion or '—'}</b>\n\n"
                "¿En qué categoría lo registramos?",
                make_keyboard(CATEGORIAS, 2)
            )
        except Exception as ex:
            await send_msg(chat_id,
                f"⚠️ No pude procesar la imagen: {str(ex)}\n"
                "Podés intentar de nuevo o usar /nuevo para cargarlo manualmente."
            )
        return

    # ── Categoría después de foto ──
    if state.get("step") == "categoria_ticket":
        if text not in CATEGORIAS:
            await send_msg(chat_id, "⚠️ Elegí una categoría de la lista.", make_keyboard(CATEGORIAS, 2))
            return
        d = state["data"]
        d["categoria"] = text
        conn = get_db()
        conn.execute(
            "INSERT INTO gastos (empleado_id,fecha,monto,moneda,categoria,descripcion) VALUES (?,?,?,?,?,?)",
            (d["empleado_id"], d["fecha"], d["monto"], d["moneda"], d["categoria"], d.get("descripcion"))
        )
        conn.commit()
        conn.close()
        user_state[chat_id] = {}
        await send_msg(chat_id,
            f"🎉 <b>Gasto registrado desde ticket:</b>\n\n"
            f"📅 {d['fecha']} | 🗂 {d['categoria']}\n"
            f"💰 {d['moneda']} ${d['monto']:,.2f}\n"
            f"📝 {d.get('descripcion') or '—'}\n\n"
            "¿Tenés otro ticket?",
            make_keyboard(["/nuevo", "/misgastos"])
        )
        return

    # ── /nuevo — flujo manual ──
    if text == "/nuevo":
        user_state[chat_id] = {"step": "fecha", "data": {"empleado_id": emp["id"]}}
        await send_msg(chat_id,
            "📅 <b>Paso 1/5</b> — ¿Cuál es la fecha del gasto?\n"
            "Escribí la fecha en formato <b>YYYY-MM-DD</b> o enviá <b>hoy</b>.",
            remove_keyboard()
        )
        return

    if state.get("step") == "fecha":
        fecha = date.today().isoformat() if text.lower() == "hoy" else text
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except:
            await send_msg(chat_id, "⚠️ Formato incorrecto. Usá YYYY-MM-DD o escribí <b>hoy</b>.")
            return
        user_state[chat_id]["data"]["fecha"] = fecha
        user_state[chat_id]["step"] = "categoria"
        await send_msg(chat_id, "🗂 <b>Paso 2/5</b> — ¿Cuál es la categoría?", make_keyboard(CATEGORIAS, 2))
        return

    if state.get("step") == "categoria":
        if text not in CATEGORIAS:
            await send_msg(chat_id, "⚠️ Elegí una categoría de la lista.", make_keyboard(CATEGORIAS, 2))
            return
        user_state[chat_id]["data"]["categoria"] = text
        user_state[chat_id]["step"] = "moneda"
        await send_msg(chat_id, "💱 <b>Paso 3/5</b> — ¿En qué moneda?", make_keyboard(["ARS 🇦🇷", "USD 🇺🇸"], 2))
        return

    if state.get("step") == "moneda":
        moneda = "ARS" if "ARS" in text else "USD" if "USD" in text else None
        if not moneda:
            await send_msg(chat_id, "⚠️ Elegí ARS o USD.", make_keyboard(["ARS 🇦🇷", "USD 🇺🇸"], 2))
            return
        user_state[chat_id]["data"]["moneda"] = moneda
        user_state[chat_id]["step"] = "monto"
        await send_msg(chat_id, f"💰 <b>Paso 4/5</b> — ¿Cuánto fue el monto en {moneda}?", remove_keyboard())
        return

    if state.get("step") == "monto":
        try:
            monto = float(text.replace(",",".").replace("$","").strip())
        except:
            await send_msg(chat_id, "⚠️ Ingresá solo el número, ej: <b>1500.50</b>")
            return
        user_state[chat_id]["data"]["monto"] = monto
        user_state[chat_id]["step"] = "descripcion"
        await send_msg(chat_id, "📝 <b>Paso 5/5</b> — Descripción breve (o <b>-</b> para omitir):", remove_keyboard())
        return

    if state.get("step") == "descripcion":
        desc = None if text == "-" else text
        d = user_state[chat_id]["data"]
        d["descripcion"] = desc
        conn = get_db()
        conn.execute(
            "INSERT INTO gastos (empleado_id,fecha,monto,moneda,categoria,descripcion) VALUES (?,?,?,?,?,?)",
            (d["empleado_id"], d["fecha"], d["monto"], d["moneda"], d["categoria"], desc)
        )
        conn.commit()
        conn.close()
        user_state[chat_id] = {}
        await send_msg(chat_id,
            f"✅ <b>Gasto registrado:</b>\n\n"
            f"📅 {d['fecha']} | 🗂 {d['categoria']}\n"
            f"💰 {d['moneda']} ${d['monto']:,.2f}\n"
            f"📝 {desc or '—'}\n\n"
            "¿Querés registrar otro?",
            make_keyboard(["/nuevo", "/misgastos"])
        )
        return

    # Mensaje no reconocido
    await send_msg(chat_id,
        "🤖 Podés <b>mandar una foto del ticket</b> para registrarlo automáticamente, "
        "o usá los comandos:",
        make_keyboard(["/nuevo", "/misgastos"])
    )

@app.post("/webhook", tags=["Telegram"])
async def webhook(update: dict):
    asyncio.create_task(process_update(update))
    return {"ok": True}

@app.get("/setup-webhook", tags=["Telegram"])
async def setup_webhook(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{TELEGRAM_API}/setWebhook", json={"url": f"{url}/webhook"})
        return r.json()
