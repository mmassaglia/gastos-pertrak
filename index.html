<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Gastos Pertrak</title>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap" rel="stylesheet"/>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{
      --bg:#0F1117;--surface:#1A1D27;--surface2:#22263A;--ink:#F0F2FF;
      --ink-soft:#8B90B0;--accent:#6C63FF;--accent2:#FF6B6B;--green:#4ECDC4;
      --gold:#FFD93D;--border:#2A2D40;--radius:12px;--shadow:0 4px 24px rgba(0,0,0,.4);
    }
    body{font-family:'Space Grotesk',sans-serif;background:var(--bg);color:var(--ink);min-height:100vh;}

    /* LOGIN */
    .login-wrap{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:1rem;
      background:radial-gradient(ellipse at 60% 40%,rgba(108,99,255,.15) 0%,transparent 60%);}
    .login-box{background:var(--surface);border:1px solid var(--border);border-radius:20px;
      padding:2.5rem;width:100%;max-width:400px;box-shadow:0 20px 60px rgba(0,0,0,.5);}
    .login-logo{font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;text-align:center;margin-bottom:.5rem;}
    .login-logo span{color:var(--accent);}
    .login-sub{text-align:center;color:var(--ink-soft);font-size:.85rem;margin-bottom:2rem;}
    .login-field{display:flex;flex-direction:column;gap:.35rem;margin-bottom:1rem;}
    .login-field label{font-size:.75rem;font-weight:600;color:var(--ink-soft);text-transform:uppercase;letter-spacing:.05em;}
    .login-field input{background:var(--surface2);border:1.5px solid var(--border);border-radius:8px;
      padding:.65rem .85rem;font-family:'Space Grotesk',sans-serif;font-size:.95rem;color:var(--ink);}
    .login-field input:focus{outline:none;border-color:var(--accent);}
    .login-err{background:rgba(255,107,107,.1);border:1px solid var(--accent2);border-radius:8px;
      padding:.6rem .85rem;font-size:.82rem;color:var(--accent2);margin-bottom:1rem;}
    .btn-login{width:100%;background:var(--accent);color:#fff;border:none;border-radius:10px;
      padding:.75rem;font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;cursor:pointer;
      transition:background .17s;margin-top:.5rem;}
    .btn-login:hover{background:#5a52d5;}
    .login-hint{text-align:center;font-size:.75rem;color:var(--ink-soft);margin-top:1rem;}

    /* HEADER */
    header{background:var(--surface);border-bottom:1px solid var(--border);padding:0 2rem;
      display:flex;align-items:center;justify-content:space-between;height:64px;position:sticky;top:0;z-index:100;}
    .logo{font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;}
    .logo span{color:var(--accent);}
    .header-right{display:flex;align-items:center;gap:1rem;}
    .user-chip{background:var(--surface2);border:1px solid var(--border);border-radius:20px;
      padding:.3rem .85rem;font-size:.8rem;display:flex;align-items:center;gap:.4rem;}
    .role-badge{font-size:.65rem;font-weight:700;padding:.15rem .45rem;border-radius:10px;text-transform:uppercase;}
    .role-admin{background:rgba(108,99,255,.2);color:var(--accent);}
    .role-empleado{background:rgba(78,205,196,.2);color:var(--green);}
    .nav-tabs{display:flex;gap:.25rem;}
    .nav-tab{background:transparent;border:none;color:var(--ink-soft);font-family:'Space Grotesk',sans-serif;
      font-size:.85rem;font-weight:500;padding:.45rem 1rem;border-radius:8px;cursor:pointer;transition:all .18s;}
    .nav-tab:hover{background:var(--surface2);color:var(--ink);}
    .nav-tab.active{background:var(--accent);color:#fff;}

    /* LAYOUT */
    .container{max-width:1100px;margin:0 auto;padding:2rem 1.5rem;}
    .page-title{font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;margin-bottom:1.5rem;}
    .page-title small{font-family:'Space Grotesk',sans-serif;font-size:.85rem;color:var(--ink-soft);font-weight:400;display:block;margin-top:.2rem;}
    .top-bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:.75rem;}

    /* STATS */
    .stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:2rem;}
    .stat{background:var(--surface);border-radius:var(--radius);padding:1.25rem;border:1px solid var(--border);}
    .stat-val{font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;margin-bottom:.25rem;}
    .stat-val.green{color:var(--green);}.stat-val.gold{color:var(--gold);}
    .stat-val.purple{color:var(--accent);}.stat-val.red{color:var(--accent2);}
    .stat-lbl{font-size:.75rem;color:var(--ink-soft);text-transform:uppercase;letter-spacing:.06em;font-weight:600;}

    /* FILTERS */
    .filters{display:flex;gap:.75rem;flex-wrap:wrap;margin-bottom:1.25rem;align-items:center;}
    .filters input,.filters select{background:var(--surface);border:1px solid var(--border);border-radius:8px;
      padding:.45rem .85rem;color:var(--ink);font-family:'Space Grotesk',sans-serif;font-size:.85rem;}
    .filters input:focus,.filters select:focus{outline:none;border-color:var(--accent);}

    /* TABLE */
    .table-wrap{background:var(--surface);border-radius:var(--radius);border:1px solid var(--border);overflow:hidden;}
    table{width:100%;border-collapse:collapse;}
    thead th{background:var(--surface2);padding:.75rem 1rem;text-align:left;font-size:.75rem;
      text-transform:uppercase;letter-spacing:.06em;color:var(--ink-soft);font-weight:600;}
    tbody tr{border-top:1px solid var(--border);transition:background .12s;}
    tbody tr:hover{background:var(--surface2);}
    tbody td{padding:.75rem 1rem;font-size:.85rem;}
    .badge{font-size:.7rem;font-weight:700;padding:.2rem .6rem;border-radius:20px;text-transform:uppercase;letter-spacing:.04em;}
    .badge-ars{background:rgba(78,205,196,.15);color:var(--green);}
    .badge-usd{background:rgba(255,217,61,.15);color:var(--gold);}
    .badge-pendiente{background:rgba(108,99,255,.15);color:var(--accent);}
    .badge-aprobado{background:rgba(78,205,196,.15);color:var(--green);}
    .badge-rechazado{background:rgba(255,107,107,.15);color:var(--accent2);}
    .badge-mp{background:rgba(255,255,255,.08);color:var(--ink-soft);}

    /* BTNS */
    .btn{display:inline-flex;align-items:center;gap:.4rem;padding:.5rem 1.1rem;border-radius:9px;border:none;
      font-family:'Space Grotesk',sans-serif;font-size:.85rem;font-weight:600;cursor:pointer;transition:all .17s;}
    .btn-primary{background:var(--accent);color:#fff;}.btn-primary:hover{background:#5a52d5;}
    .btn-ghost{background:transparent;border:1px solid var(--border);color:var(--ink);}
    .btn-ghost:hover{border-color:var(--accent);color:var(--accent);}
    .btn-green{background:var(--green);color:#000;}
    .btn-export{background:var(--gold);color:#000;}.btn-export:hover{opacity:.85;}
    .btn-sm{padding:.3rem .65rem;font-size:.75rem;}
    .btn-red{color:var(--accent2)!important;}

    /* MODAL */
    .overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);backdrop-filter:blur(4px);z-index:200;
      display:flex;align-items:center;justify-content:center;padding:1rem;}
    .modal{background:var(--surface);border-radius:18px;padding:2rem;width:100%;max-width:500px;
      border:1px solid var(--border);animation:popIn .2s ease;max-height:90vh;overflow-y:auto;}
    @keyframes popIn{from{transform:scale(.94);opacity:0}to{transform:scale(1);opacity:1}}
    .modal h2{font-family:'Syne',sans-serif;font-size:1.4rem;margin-bottom:1.25rem;}
    .form-grid{display:grid;grid-template-columns:1fr 1fr;gap:.75rem;}
    .form-grid .full{grid-column:1/-1;}
    .field{display:flex;flex-direction:column;gap:.3rem;}
    .field label{font-size:.75rem;font-weight:600;color:var(--ink-soft);text-transform:uppercase;letter-spacing:.05em;}
    .field input,.field select,.field textarea{background:var(--surface2);border:1px solid var(--border);
      border-radius:8px;padding:.55rem .75rem;font-family:'Space Grotesk',sans-serif;font-size:.9rem;color:var(--ink);}
    .field input:focus,.field select:focus{outline:none;border-color:var(--accent);}
    .modal-footer{display:flex;gap:.75rem;justify-content:flex-end;margin-top:1.5rem;}

    /* REPORTES */
    .report-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem;}
    .report-card{background:var(--surface);border-radius:var(--radius);padding:1.25rem;border:1px solid var(--border);}
    .report-card h3{font-size:.85rem;color:var(--ink-soft);text-transform:uppercase;letter-spacing:.06em;font-weight:600;margin-bottom:1rem;}
    .report-row{display:flex;justify-content:space-between;align-items:center;padding:.4rem 0;border-bottom:1px solid var(--border);font-size:.85rem;}
    .report-row:last-child{border:none;}
    .report-row strong{color:var(--green);font-weight:700;}

    /* USUARIOS */
    .usr-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1rem;}
    .usr-card{background:var(--surface);border-radius:var(--radius);padding:1.25rem;border:1px solid var(--border);}
    .usr-avatar{width:42px;height:42px;border-radius:50%;background:var(--accent);display:flex;align-items:center;
      justify-content:center;font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;margin-bottom:.75rem;}
    .usr-avatar.emp{background:var(--green);}

    .empty{text-align:center;padding:3rem;color:var(--ink-soft);}
    .empty .icon{font-size:2.5rem;margin-bottom:.75rem;}
    .spinner{border:3px solid var(--border);border-top-color:var(--accent);border-radius:50%;width:28px;height:28px;
      animation:spin .7s linear infinite;margin:3rem auto;}
    @keyframes spin{to{transform:rotate(360deg)}}
    .toast{position:fixed;bottom:1.5rem;right:1.5rem;background:var(--accent);color:#fff;padding:.75rem 1.25rem;
      border-radius:10px;font-size:.85rem;font-weight:600;z-index:300;animation:slideUp .25s ease;}
    @keyframes slideUp{from{transform:translateY(12px);opacity:0}to{transform:translateY(0);opacity:1}}

    @media(max-width:700px){
      .stats{grid-template-columns:1fr 1fr;}
      .report-grid{grid-template-columns:1fr;}
      .form-grid{grid-template-columns:1fr;}
      .nav-tabs{display:none;}
    }
  </style>
</head>
<body>
<div id="root"></div>
<script>
const API = 'https://gastos-pertrak-production.up.railway.app';
const {useState,useEffect,createElement:h} = React;

const CATS = ["Refrigerio","Viáticos","Transporte","Combustible","Alojamiento","Papelería","Herramientas","Telefonía","Representación","Otros"];
const METODOS = ["Efectivo","Tarjeta de crédito","Tarjeta de débito","Transferencia","Otros"];
const METODO_ICONS = {"Efectivo":"💵","Tarjeta de crédito":"💳","Tarjeta de débito":"💳","Transferencia":"🏦","Otros":"📋"};

const fmt = n => n ? new Intl.NumberFormat('es-AR',{minimumFractionDigits:2}).format(n) : '0,00';
const today = () => new Date().toISOString().slice(0,10);
const mesActual = () => { const d=new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-01`; };
const initials = n => n ? n.split(' ').map(p=>p[0]).join('').slice(0,2).toUpperCase() : '?';

function Toast({msg}){ return msg ? h('div',{className:'toast'},msg) : null; }

// ── AUTH helpers ──
function getToken(){ return localStorage.getItem('gp_token'); }
function getUser(){ try{ return JSON.parse(localStorage.getItem('gp_user')); }catch{ return null; } }
function authHeaders(){ return {'Content-Type':'application/json','Authorization':'Bearer '+getToken()}; }

// ── LOGIN ──
function Login({onLogin}){
  const [form,setForm] = useState({username:'',password:''});
  const [err,setErr] = useState('');
  const [loading,setLoading] = useState(false);
  const set = k => e => setForm(f=>({...f,[k]:e.target.value}));

  async function submit(e){
    e.preventDefault();
    setLoading(true); setErr('');
    try{
      const r = await fetch(`${API}/auth/login`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(form)});
      if(!r.ok){ setErr('Usuario o contraseña incorrectos'); return; }
      const data = await r.json();
      localStorage.setItem('gp_token', data.token);
      localStorage.setItem('gp_user', JSON.stringify({nombre:data.nombre,rol:data.rol,username:data.username}));
      onLogin(data);
    }catch{ setErr('Error de conexión'); }
    finally{ setLoading(false); }
  }

  return h('div',{className:'login-wrap'},
    h('div',{className:'login-box'},
      h('div',{className:'login-logo'},'💰 Gastos ',h('span',null,'Pertrak')),
      h('div',{className:'login-sub'},'Sistema de gestión de gastos'),
      err && h('div',{className:'login-err'},'⚠️ '+err),
      h('form',{onSubmit:submit},
        h('div',{className:'login-field'},h('label',null,'Usuario'),h('input',{value:form.username,onChange:set('username'),placeholder:'usuario',autoComplete:'username'})),
        h('div',{className:'login-field'},h('label',null,'Contraseña'),h('input',{type:'password',value:form.password,onChange:set('password'),placeholder:'••••••••',autoComplete:'current-password'})),
        h('button',{className:'btn-login',type:'submit',disabled:loading},loading?'Ingresando…':'Ingresar')
      ),
      h('div',{className:'login-hint'},'Usuario por defecto: admin / admin123')
    )
  );
}

// ── MODAL GASTO ──
function ModalGasto({empleados, gasto, onClose, onSaved, user}){
  const editing = !!gasto;
  const [form,setForm] = useState({
    empleado_id: gasto?.empleado_id||'',
    fecha: gasto?.fecha||today(),
    monto: gasto?.monto||'',
    moneda: gasto?.moneda||'ARS',
    categoria: gasto?.categoria||'',
    metodo_pago: gasto?.metodo_pago||'Efectivo',
    descripcion: gasto?.descripcion||'',
  });
  const [loading,setLoading] = useState(false);
  const set = k => e => setForm(f=>({...f,[k]:e.target.value}));

  async function submit(){
    if(!form.fecha||!form.monto||!form.categoria||!form.metodo_pago){ alert('Completá todos los campos obligatorios'); return; }
    setLoading(true);
    try{
      const url = editing ? `${API}/gastos/${gasto.id}` : `${API}/gastos`;
      const method = editing ? 'PUT' : 'POST';
      const body = {...form, monto:parseFloat(form.monto)};
      if(form.empleado_id) body.empleado_id = parseInt(form.empleado_id);
      const r = await fetch(url,{method,headers:authHeaders(),body:JSON.stringify(body)});
      if(!r.ok){ const e=await r.json(); throw new Error(e.detail||'Error'); }
      onSaved();
    }catch(e){ alert(e.message); }
    finally{ setLoading(false); }
  }

  return h('div',{className:'overlay',onClick:e=>e.target===e.currentTarget&&onClose()},
    h('div',{className:'modal'},
      h('h2',null,editing?'Editar gasto':'Nuevo gasto'),
      h('div',{className:'form-grid'},
        user.rol==='admin' && h('div',{className:'field full'},
          h('label',null,'Empleado (opcional)'),
          h('select',{value:form.empleado_id,onChange:set('empleado_id')},
            h('option',{value:''},'— Sin asignar —'),
            empleados.map(e=>h('option',{key:e.id,value:e.id},e.nombre))
          )
        ),
        h('div',{className:'field'},h('label',null,'Fecha'),h('input',{type:'date',value:form.fecha,onChange:set('fecha')})),
        h('div',{className:'field'},
          h('label',null,'Moneda'),
          h('select',{value:form.moneda,onChange:set('moneda')},
            h('option',{value:'ARS'},'🇦🇷 ARS'),
            h('option',{value:'USD'},'🇺🇸 USD')
          )
        ),
        h('div',{className:'field'},h('label',null,'Monto'),h('input',{type:'number',step:'0.01',placeholder:'0.00',value:form.monto,onChange:set('monto')})),
        h('div',{className:'field'},
          h('label',null,'Categoría'),
          h('select',{value:form.categoria,onChange:set('categoria')},
            h('option',{value:''},'— Categoría —'),
            CATS.map(c=>h('option',{key:c,value:c},c))
          )
        ),
        h('div',{className:'field'},
          h('label',null,'Método de pago'),
          h('select',{value:form.metodo_pago,onChange:set('metodo_pago')},
            METODOS.map(m=>h('option',{key:m,value:m},METODO_ICONS[m]+' '+m))
          )
        ),
        h('div',{className:'field full'},h('label',null,'Descripción'),h('input',{type:'text',placeholder:'Detalle del gasto…',value:form.descripcion,onChange:set('descripcion')}))
      ),
      h('div',{className:'modal-footer'},
        h('button',{className:'btn btn-ghost',onClick:onClose},'Cancelar'),
        h('button',{className:'btn btn-primary',onClick:submit,disabled:loading},loading?'Guardando…':editing?'Guardar':'Registrar gasto')
      )
    )
  );
}

// ── TAB GASTOS ──
function TabGastos({empleados, user}){
  const [gastos,setGastos] = useState([]);
  const [loading,setLoading] = useState(false);
  const [error,setError] = useState('');
  const [modal,setModal] = useState(null);
  const [toast,setToast] = useState('');
  const [filtros,setFiltros] = useState({desde:mesActual(),hasta:today(),categoria:'',moneda:'',metodo_pago:'',empleado_id:''});
  function showToast(m){ setToast(m); setTimeout(()=>setToast(''),2800); }
  const setF = k => e => setFiltros(f=>({...f,[k]:e.target.value}));

  async function cargar(){
    setLoading(true);
    setError('');
    const p = new URLSearchParams();
    Object.entries(filtros).forEach(([k,v])=>{ if(v) p.set(k,v); });
    try{ const r=await fetch(`${API}/gastos?${p}`,{headers:authHeaders()}); setGastos(await r.json()); }
    catch(e){ setError('Error al cargar gastos: '+e.message); setGastos([]); }
    finally{ setLoading(false); }
  }

  useEffect(()=>{ cargar(); },[filtros]);

  async function eliminar(id){
    if(!confirm('¿Eliminar este gasto?')) return;
    await fetch(`${API}/gastos/${id}`,{method:'DELETE',headers:authHeaders()});
    showToast('Gasto eliminado'); cargar();
  }

  async function cambiarEstado(id, estado){
    await fetch(`${API}/gastos/${id}`,{method:'PUT',headers:authHeaders(),body:JSON.stringify({estado})});
    showToast(`Marcado como ${estado}`); cargar();
  }

  function exportar(){
    const p = new URLSearchParams();
    if(filtros.desde) p.set('desde',filtros.desde);
    if(filtros.hasta) p.set('hasta',filtros.hasta);
    window.open(`${API}/exportar/excel?${p}&token=${getToken()}`,'_blank');
  }

  const totalARS = gastos.filter(g=>g.moneda==='ARS').reduce((s,g)=>s+g.monto,0);
  const totalUSD = gastos.filter(g=>g.moneda==='USD').reduce((s,g)=>s+g.monto,0);

  return h('div',null,
    h('div',{className:'top-bar'},
      h('div',{className:'page-title'},'Gastos',h('small',null,`${gastos.length} registros`)),
      h('div',{style:{display:'flex',gap:'.5rem'}},
        user.rol==='admin' && h('button',{className:'btn btn-export',onClick:exportar},'⬇ Exportar CSV'),
        h('button',{className:'btn btn-primary',onClick:()=>setModal('nuevo')},'＋ Nuevo gasto')
      )
    ),
    h('div',{className:'stats'},
      h('div',{className:'stat'},h('div',{className:'stat-val green'},'$'+fmt(totalARS)),h('div',{className:'stat-lbl'},'Total ARS')),
      h('div',{className:'stat'},h('div',{className:'stat-val gold'},'$'+fmt(totalUSD)),h('div',{className:'stat-lbl'},'Total USD')),
      h('div',{className:'stat'},h('div',{className:'stat-val purple'},gastos.length),h('div',{className:'stat-lbl'},'Registros')),
      h('div',{className:'stat'},h('div',{className:'stat-val red'},gastos.filter(g=>g.estado==='pendiente').length),h('div',{className:'stat-lbl'},'Pendientes'))
    ),
    h('div',{className:'filters'},
      h('div',null,h('input',{type:'date',value:filtros.desde,onChange:setF('desde')})),
      h('div',null,h('input',{type:'date',value:filtros.hasta,onChange:setF('hasta')})),
      h('select',{value:filtros.categoria,onChange:setF('categoria')},
        h('option',{value:''},'Todas las categorías'),
        CATS.map(c=>h('option',{key:c,value:c},c))
      ),
      h('select',{value:filtros.metodo_pago,onChange:setF('metodo_pago')},
        h('option',{value:''},'Todos los métodos'),
        METODOS.map(m=>h('option',{key:m,value:m},METODO_ICONS[m]+' '+m))
      ),
      h('select',{value:filtros.moneda,onChange:setF('moneda')},
        h('option',{value:''},'ARS + USD'),
        h('option',{value:'ARS'},'Solo ARS'),
        h('option',{value:'USD'},'Solo USD')
      ),
      user.rol==='admin' && h('select',{value:filtros.empleado_id,onChange:setF('empleado_id')},
        h('option',{value:''},'Todos los empleados'),
        empleados.map(e=>h('option',{key:e.id,value:e.id},e.nombre))
      )
    ),
    loading && h('div',{className:'spinner'}),
    error && h('div',{className:'empty'},h('div',{className:'icon'},'⚠️'),h('p',null,error),h('button',{className:'btn btn-primary',onClick:cargar},'Reintentar')),
    !loading && !error && gastos.length===0 && h('div',{className:'empty'},h('div',{className:'icon'},'💸'),h('p',null,'Sin gastos para los filtros seleccionados')),
    !loading && gastos.length>0 && h('div',{className:'table-wrap'},
      h('table',null,
        h('thead',null,h('tr',null,
          h('th',null,'Fecha'),h('th',null,'Empleado'),h('th',null,'Categoría'),
          h('th',null,'Método'),h('th',null,'Monto'),h('th',null,'Estado'),h('th',null,'Acciones')
        )),
        h('tbody',null,
          gastos.map(g=>h('tr',{key:g.id},
            h('td',null,g.fecha),
            h('td',null,g.empleado||'—'),
            h('td',null,g.categoria),
            h('td',null,h('span',{className:'badge badge-mp'},METODO_ICONS[g.metodo_pago]||'📋',' ',g.metodo_pago||'—')),
            h('td',null,h('span',{className:`badge badge-${g.moneda.toLowerCase()}`},g.moneda),' $'+fmt(g.monto)),
            h('td',null,h('span',{className:`badge badge-${g.estado}`},g.estado)),
            h('td',null,
              h('div',{style:{display:'flex',gap:'.35rem',flexWrap:'wrap'}},
                user.rol==='admin' && g.estado==='pendiente' && h('button',{className:'btn btn-green btn-sm',onClick:()=>cambiarEstado(g.id,'aprobado')},'✓'),
                user.rol==='admin' && g.estado==='pendiente' && h('button',{className:'btn btn-ghost btn-sm btn-red',onClick:()=>cambiarEstado(g.id,'rechazado')},'✕'),
                h('button',{className:'btn btn-ghost btn-sm',onClick:()=>setModal(g)},'✏'),
                user.rol==='admin' && h('button',{className:'btn btn-ghost btn-sm btn-red',onClick:()=>eliminar(g.id)},'🗑')
              )
            )
          ))
        )
      )
    ),
    modal && h(ModalGasto,{
      empleados, user,
      gasto: modal==='nuevo'?null:modal,
      onClose:()=>setModal(null),
      onSaved:()=>{ setModal(null); cargar(); showToast(modal==='nuevo'?'Gasto registrado ✓':'Gasto actualizado ✓'); }
    }),
    h(Toast,{msg:toast})
  );
}

// ── TAB REPORTES ──
function TabReportes({user}){
  const [data,setData] = useState(null);
  const [desde,setDesde] = useState(mesActual());
  const [hasta,setHasta] = useState(today());

  async function cargar(){
    const p = new URLSearchParams({desde,hasta});
    const r = await fetch(`${API}/resumen?${p}`,{headers:authHeaders()});
    setData(await r.json());
  }

  useEffect(()=>{ cargar(); },[desde,hasta]);
  if(!data) return h('div',{className:'spinner'});

  return h('div',null,
    h('div',{className:'top-bar'},
      h('div',{className:'page-title'},'Reportes'),
      h('div',{className:'filters'},
        h('input',{type:'date',value:desde,onChange:e=>setDesde(e.target.value)}),
        h('input',{type:'date',value:hasta,onChange:e=>setHasta(e.target.value)}),
        h('button',{className:'btn btn-primary',onClick:cargar},'Actualizar')
      )
    ),
    h('div',{className:'stats'},
      h('div',{className:'stat'},h('div',{className:'stat-val green'},'$'+fmt(data.total_ars)),h('div',{className:'stat-lbl'},'Total ARS')),
      h('div',{className:'stat'},h('div',{className:'stat-val gold'},'$'+fmt(data.total_usd)),h('div',{className:'stat-lbl'},'Total USD')),
      h('div',{className:'stat'},h('div',{className:'stat-val purple'},data.por_categoria.length),h('div',{className:'stat-lbl'},'Categorías')),
      h('div',{className:'stat'},h('div',{className:'stat-val red'},data.por_empleado.length),h('div',{className:'stat-lbl'},'Personas'))
    ),
    h('div',{className:'report-grid'},
      h('div',{className:'report-card'},
        h('h3',null,'Por categoría'),
        data.por_categoria.map((r,i)=>h('div',{key:i,className:'report-row'},
          h('span',null,r.categoria+' ('+r.moneda+')'),
          h('div',null,h('strong',null,'$'+fmt(r.total)),h('span',{style:{color:'var(--ink-soft)',marginLeft:'.5rem',fontSize:'.75rem'}},r.qty+' gastos'))
        ))
      ),
      h('div',{className:'report-card'},
        h('h3',null,'Por método de pago (ARS)'),
        data.por_metodo_pago.map((r,i)=>h('div',{key:i,className:'report-row'},
          h('span',null,(METODO_ICONS[r.metodo_pago]||'📋')+' '+r.metodo_pago),
          h('div',null,h('strong',null,'$'+fmt(r.total)),h('span',{style:{color:'var(--ink-soft)',marginLeft:'.5rem',fontSize:'.75rem'}},r.qty+' gastos'))
        ))
      ),
      h('div',{className:'report-card'},
        h('h3',null,'Por persona'),
        data.por_empleado.map((r,i)=>h('div',{key:i,className:'report-row'},
          h('span',null,r.nombre+' ('+r.moneda+')'),
          h('div',null,h('strong',null,'$'+fmt(r.total)),h('span',{style:{color:'var(--ink-soft)',marginLeft:'.5rem',fontSize:'.75rem'}},r.qty+' gastos'))
        ))
      ),
      h('div',{className:'report-card'},
        h('h3',null,'Por mes'),
        data.por_mes.map((r,i)=>h('div',{key:i,className:'report-row'},
          h('span',null,r.mes+' ('+r.moneda+')'),
          h('strong',null,'$'+fmt(r.total))
        ))
      )
    )
  );
}

// ── TAB USUARIOS (solo admin) ──
function TabUsuarios(){
  const [usuarios,setUsuarios] = useState([]);
  const [modal,setModal] = useState(false);
  const [form,setForm] = useState({username:'',password:'',nombre:'',rol:'empleado'});
  const [toast,setToast] = useState('');
  function showToast(m){ setToast(m); setTimeout(()=>setToast(''),2800); }
  const set = k => e => setForm(f=>({...f,[k]:e.target.value}));

  async function cargar(){ const r=await fetch(`${API}/usuarios`,{headers:authHeaders()}); setUsuarios(await r.json()); }
  useEffect(()=>{ cargar(); },[]);

  async function crear(){
    if(!form.username||!form.password||!form.nombre){ alert('Completá todos los campos'); return; }
    const r = await fetch(`${API}/usuarios`,{method:'POST',headers:authHeaders(),body:JSON.stringify(form)});
    if(!r.ok){ const e=await r.json(); alert(e.detail); return; }
    setModal(false); setForm({username:'',password:'',nombre:'',rol:'empleado'}); cargar(); showToast('Usuario creado ✓');
  }

  async function desactivar(u){
    if(!confirm(`¿Desactivar a ${u.nombre}?`)) return;
    await fetch(`${API}/usuarios/${u.id}`,{method:'DELETE',headers:authHeaders()});
    showToast('Usuario desactivado'); cargar();
  }

  return h('div',null,
    h('div',{className:'top-bar'},
      h('div',{className:'page-title'},'Usuarios',h('small',null,`${usuarios.filter(u=>u.activo).length} activos`)),
      h('button',{className:'btn btn-primary',onClick:()=>setModal(true)},'＋ Nuevo usuario')
    ),
    h('div',{className:'usr-grid'},
      usuarios.map(u=>h('div',{key:u.id,className:'usr-card',style:{opacity:u.activo?1:.5}},
        h('div',{className:`usr-avatar${u.rol==='empleado'?' emp':''}`},initials(u.nombre)),
        h('div',{style:{display:'flex',alignItems:'center',gap:'.5rem',marginBottom:'.25rem'}},
          h('h3',{style:{fontSize:'.95rem',fontWeight:600}},u.nombre),
          h('span',{className:`role-badge role-${u.rol}`},u.rol)
        ),
        h('p',{style:{fontSize:'.8rem',color:'var(--ink-soft)'}},u.username),
        u.activo && u.username!=='admin' && h('div',{style:{display:'flex',gap:'.5rem',marginTop:'.75rem'}},
          h('button',{className:'btn btn-ghost btn-sm btn-red',onClick:()=>desactivar(u)},'✕ Desactivar')
        )
      )),
      usuarios.length===0 && h('div',{className:'empty',style:{gridColumn:'1/-1'}},h('div',{className:'icon'},'👥'),h('p',null,'Sin usuarios'))
    ),
    modal && h('div',{className:'overlay',onClick:e=>e.target===e.currentTarget&&setModal(false)},
      h('div',{className:'modal'},
        h('h2',null,'Nuevo usuario'),
        h('div',{className:'form-grid'},
          h('div',{className:'field full'},h('label',null,'Nombre completo'),h('input',{value:form.nombre,onChange:set('nombre'),placeholder:'Juan Pérez'})),
          h('div',{className:'field'},h('label',null,'Usuario'),h('input',{value:form.username,onChange:set('username'),placeholder:'juanp'})),
          h('div',{className:'field'},h('label',null,'Contraseña'),h('input',{type:'password',value:form.password,onChange:set('password'),placeholder:'••••••••'})),
          h('div',{className:'field full'},
            h('label',null,'Rol'),
            h('select',{value:form.rol,onChange:set('rol')},
              h('option',{value:'empleado'},'👤 Empleado — solo ve sus gastos'),
              h('option',{value:'admin'},'⚡ Administrador — ve todo')
            )
          )
        ),
        h('div',{className:'modal-footer'},
          h('button',{className:'btn btn-ghost',onClick:()=>setModal(false)},'Cancelar'),
          h('button',{className:'btn btn-primary',onClick:crear},'Crear usuario')
        )
      )
    ),
    h(Toast,{msg:toast})
  );
}

// ── APP ──
function App(){
  const [user,setUser] = useState(getUser());
  const [tab,setTab] = useState('gastos');
  const [empleados,setEmpleados] = useState([]);

  useEffect(()=>{
    if(!user) return;
    fetch(`${API}/empleados`,{headers:authHeaders()}).then(r=>r.json()).then(setEmpleados).catch(()=>{});
  },[tab,user]);

  async function logout(){
    await fetch(`${API}/auth/logout`,{method:'POST',headers:authHeaders()});
    localStorage.removeItem('gp_token');
    localStorage.removeItem('gp_user');
    setUser(null);
  }

  if(!user) return h(Login,{onLogin:d=>setUser({nombre:d.nombre,rol:d.rol,username:d.username})});

  return h('div',null,
    h('header',null,
      h('div',{className:'logo'},'💰 Gastos ',h('span',null,'Pertrak')),
      h('nav',{className:'nav-tabs'},
        h('button',{className:`nav-tab${tab==='gastos'?' active':''}`,onClick:()=>setTab('gastos')},'💸 Gastos'),
        h('button',{className:`nav-tab${tab==='reportes'?' active':''}`,onClick:()=>setTab('reportes')},'📊 Reportes'),
        user.rol==='admin' && h('button',{className:`nav-tab${tab==='usuarios'?' active':''}`,onClick:()=>setTab('usuarios')},'👥 Usuarios')
      ),
      h('div',{className:'header-right'},
        h('div',{className:'user-chip'},
          h('span',null,'👤 '+user.nombre),
          h('span',{className:`role-badge role-${user.rol}`},user.rol)
        ),
        h('button',{className:'btn btn-ghost btn-sm',onClick:logout},'Salir')
      )
    ),
    h('div',{className:'container'},
      tab==='gastos'   && h(TabGastos,{empleados,user}),
      tab==='reportes' && h(TabReportes,{user}),
      tab==='usuarios' && user.rol==='admin' && h(TabUsuarios)
    )
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(h(App,null));
</script>
</body>
</html>
