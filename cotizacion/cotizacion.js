"use strict";
var KEY = "logistika-cotizacion-v2";

var CATALOG = {
  start:        {concepto:"Start — Consultoría y plan de importación/exportación", descripcion:"Análisis de producto, proveedor y origen; impuestos y estimación de costo total en destino; Incoterm, régimen y ruta; expediente de viabilidad que te quedas.", cantidad:1, mxn:0, usd:0, unidad:"proyecto"},
  manage:       {concepto:"Manage — Gestión de comercio exterior (punta a punta)", descripcion:"Cada embarque coordinado: recepción de OC y seguimiento al proveedor, revisión documental, forwarder y transporte, despacho y liberación, entrega en planta y cierre con indicadores.", cantidad:1, mxn:0, usd:0, unidad:"mes"},
  partner:      {concepto:"Partner — Departamento externo de comercio exterior", descripcion:"Todo lo de Manage + acompañamiento en trámites y registros, gestión de proveedores, definición y seguimiento de KPIs, y control de costos con propuestas de mejora.", cantidad:1, mxn:0, usd:0, unidad:"mes"},
  healthcheck:  {concepto:"Supply Chain Health Check", descripcion:"Diagnóstico de 10–15 días: los problemas principales ordenados por impacto, costo estimado de cada uno, riesgos de cumplimiento, acciones para 30 días y hoja de ruta a 90. El reporte es tuyo.", cantidad:1, mxn:0, usd:0, unidad:"paquete"},
  import:       {concepto:"Gestión de importaciones", descripcion:"Coordinación de cada embarque del proveedor a tu bodega, con expediente cerrado e indicadores por operación.", cantidad:1, mxn:0, usd:0, unidad:"mes"},
  optimization: {concepto:"Optimización de cadena de suministro", descripcion:"Búsqueda de fugas de costo: compras, lead times, inventarios, rutas, aduanas, almacén y última milla.", cantidad:1, mxn:0, usd:0, unidad:"proyecto"},
  controltower: {concepto:"Torre de control logística", descripcion:"Monitoreo de embarques, ETA, retrasos, incidencias, OTIF y costo. Un solo punto de contacto.", cantidad:1, mxn:0, usd:0, unidad:"mes"},
  project:      {concepto:"Logística de proyectos", descripcion:"Suministro, importación, transporte especializado, cronograma e instalación para todo tipo de proyectos.", cantidad:1, mxn:0, usd:0, unidad:"proyecto"},
  interim:      {concepto:"Gerencia interina de logística", descripcion:"Sostenemos la operación entre tres y doce meses cuando se va quien la llevaba, y la entregamos ordenada.", cantidad:1, mxn:0, usd:0, unidad:"mes"}
};

var MESES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"];
function fmtDate(d){ return d.getDate() + " " + MESES[d.getMonth()] + " " + d.getFullYear(); }

function defaults(){
  var hoy = new Date();
  var vig = new Date(hoy.getTime() + 15*86400000);
  var yy = hoy.getFullYear();
  return {
    tagline:"Logística y Comercio Exterior",
    doctitle:"Cotización",
    folio:"COT-" + yy + "-001",
    fecha:fmtDate(hoy),
    vigencia:"15 días · vence " + fmtDate(vig),
    // Emisor y receptor: MISMA lista, mismo orden.
    emisor:{nombre:"Logistika", razon:"", rfc:"", direccion:"Santiago de Querétaro, Querétaro, México", correo:"hola@logistika.mx", telefono:"+52 442 608 4290"},
    cliente:{nombre:"Empresa Ejemplo, S.A. de C.V.", razon:"", rfc:"", direccion:"Ciudad, Estado", correo:"contacto@empresa.com", telefono:"+52 442 000 0000"},
    currency:"MXN", iva:true, descuento:0,
    rows:[
      {concepto:CATALOG.healthcheck.concepto, descripcion:CATALOG.healthcheck.descripcion, cantidad:1, precio:0},
      {concepto:CATALOG.manage.concepto, descripcion:CATALOG.manage.descripcion, cantidad:1, precio:0}
    ],
    notas:"La propuesta detalla los entregables, los tiempos de entrega y el alcance del servicio. Cualquier trabajo fuera del alcance acordado se cotiza por separado.",
    condiciones:[
      "Precios en pesos mexicanos, con IVA desglosado.",
      "50% de anticipo y 50% contra entrega.",
      "Alcance, entregables y plazos definidos por escrito antes de iniciar.",
      "Cualquier trabajo adicional se cotiza por separado y requiere su autorización previa.",
      "Usted es propietario de todos los entregables, incluidos los reportes, las hojas de ruta y los procesos documentados."
    ],
    sigLeft:"Aceptación del cliente · Nombre y firma",
    sigRight:"Por Logistika · Adriana Culebro Jiménez"
  };
}

var state = load();

function load(){
  var d = defaults();
  try{
    var raw = localStorage.getItem(KEY);
    if(raw){
      var s = JSON.parse(raw);
      // Merge defensivo: si el estado guardado no trae algún campo nuevo, cae al default.
      return Object.assign({}, d, s, {
        emisor: Object.assign({}, d.emisor, s.emisor || {}),
        cliente: Object.assign({}, d.cliente, s.cliente || {}),
        condiciones: (s.condiciones && s.condiciones.length) ? s.condiciones : d.condiciones,
        rows: s.rows || d.rows
      });
    }
  }catch(e){}
  return d;
}
function save(){ try{ localStorage.setItem(KEY, JSON.stringify(state)); }catch(e){} }

function locale(){ return state.currency === "MXN" ? "es-MX" : "en-US"; }
function fmt(n){
  n = isFinite(n) ? n : 0;
  try{ return new Intl.NumberFormat(locale(), {style:"currency", currency:state.currency, minimumFractionDigits:2, maximumFractionDigits:2}).format(n); }
  catch(e){ return "$" + n.toFixed(2); }
}

function parseMoney(v){ v=(v||"").toString().replace(/[^0-9.\-]/g,""); var n=parseFloat(v); return isFinite(n)?n:0; }
function $(id){ return document.getElementById(id); }
function formatDescuento(){ var d=$("descuento"); if(d && document.activeElement!==d){ d.value = fmt(state.descuento||0); } }

/* Campos de texto (input/textarea) */
function bindText(id, get, set){
  var el = $(id); if(!el) return;
  el.value = get() || "";
  el.addEventListener("input", function(){ set(el.value); save(); });
}
/* Texto editable en sitio (contenteditable) */
function bindCE(id, get, set){
  var el = $(id); if(!el) return;
  el.setAttribute("contenteditable", "true");
  el.textContent = get() || "";
  el.addEventListener("input", function(){ set(el.textContent); save(); });
}
function autosize(t){ t.style.height="auto"; t.style.height=(t.scrollHeight)+"px"; }

/* Emisor / receptor: misma estructura de campos */
var PARTY_FIELDS = ["nombre","razon","rfc","direccion","correo","telefono"];
function bindParty(prefix, obj){
  PARTY_FIELDS.forEach(function(f){
    bindText(prefix + "_" + f, function(){ return obj[f]; }, function(v){ obj[f]=v; });
  });
}

/* Condiciones editables */
function renderCondiciones(){
  var ul = $("condiciones"); if(!ul) return;
  ul.innerHTML = "";
  (state.condiciones || []).forEach(function(txt, i){
    var li = document.createElement("li");
    li.className = "ce-li";
    li.setAttribute("contenteditable", "true");
    li.textContent = txt;
    li.addEventListener("input", function(){ state.condiciones[i] = li.textContent; save(); });
    ul.appendChild(li);
  });
}

function bindAll(){
  bindCE("tagline", function(){return state.tagline;}, function(v){state.tagline=v;});
  bindCE("doctitle", function(){return state.doctitle;}, function(v){state.doctitle=v;});
  bindText("folio", function(){return state.folio;}, function(v){state.folio=v;});
  bindText("fecha", function(){return state.fecha;}, function(v){state.fecha=v;});
  bindText("vigencia", function(){return state.vigencia;}, function(v){state.vigencia=v;});

  bindParty("em", state.emisor);
  bindParty("cl", state.cliente);

  var notas = $("notas");
  notas.value = state.notas || "";
  notas.addEventListener("input", function(){ state.notas=notas.value; autosize(notas); save(); });

  bindCE("sig_left", function(){return state.sigLeft;}, function(v){state.sigLeft=v;});
  bindCE("sig_right", function(){return state.sigRight;}, function(v){state.sigRight=v;});

  var desc = $("descuento");
  formatDescuento();
  desc.addEventListener("focus", function(){ desc.value = state.descuento ? String(state.descuento) : ""; });
  desc.addEventListener("blur", formatDescuento);
  desc.addEventListener("input", function(){ state.descuento = parseMoney(desc.value); recalc(); save(); });

  $("ivachk").checked = !!state.iva;
  $("ivachk").addEventListener("change", function(){ state.iva=this.checked; recalc(); save(); });

  var seg = $("curseg");
  seg.querySelectorAll("button").forEach(function(b){
    b.setAttribute("aria-pressed", b.dataset.cur===state.currency ? "true":"false");
    b.addEventListener("click", function(){
      state.currency = b.dataset.cur; save();
      seg.querySelectorAll("button").forEach(function(x){ x.setAttribute("aria-pressed", x.dataset.cur===state.currency?"true":"false"); });
      renderRows();
    });
  });

  $("addrow").addEventListener("click", function(){ state.rows.push({concepto:"", descripcion:"", cantidad:1, precio:0}); renderRows(); save(); });
  $("catalog").addEventListener("change", function(){
    var it = CATALOG[this.value]; this.value="";
    if(!it) return;
    var precio = state.currency==="MXN" ? it.mxn : it.usd;
    state.rows.push({concepto:it.concepto, descripcion:it.descripcion, cantidad:it.cantidad||1, precio:precio});
    renderRows(); save();
  });

  $("printbtn").addEventListener("click", function(){ window.print(); });
  // Reset SELECTIVO: solo montos, conceptos y datos del cliente. Tu info y el resto
  // de la cotización (emisor, folios, notas, condiciones, firmas) se conservan.
  $("resetbtn").addEventListener("click", function(){
    if(!confirm("¿Reiniciar montos, conceptos y datos del cliente? Tu información y el resto de la cotización se conservan.")) return;
    var d = defaults();
    state.rows = d.rows;
    state.descuento = 0;
    state.cliente = d.cliente;
    save(); rebind(); renderRows();
  });
}

function rebind(){
  $("tagline").textContent = state.tagline || "";
  $("doctitle").textContent = state.doctitle || "";
  ["folio","fecha","vigencia"].forEach(function(k){ $(k).value = state[k]||""; });
  PARTY_FIELDS.forEach(function(f){
    $("em_"+f).value = state.emisor[f] || "";
    $("cl_"+f).value = state.cliente[f] || "";
  });
  $("notas").value = state.notas || ""; autosize($("notas"));
  $("sig_left").textContent = state.sigLeft || "";
  $("sig_right").textContent = state.sigRight || "";
  formatDescuento();
  $("ivachk").checked = !!state.iva;
  $("curseg").querySelectorAll("button").forEach(function(x){ x.setAttribute("aria-pressed", x.dataset.cur===state.currency?"true":"false"); });
  renderCondiciones();
}

function renderRows(){
  var tb = $("rows"); tb.innerHTML="";
  state.rows.forEach(function(row, i){
    var tr = document.createElement("tr");

    var del = document.createElement("td"); del.className="delcell";
    del.innerHTML = '<button class="rowdel" title="Quitar" aria-label="Quitar concepto">&times;</button>';
    del.querySelector("button").addEventListener("click", function(){ state.rows.splice(i,1); renderRows(); save(); });
    tr.appendChild(del);

    var c = document.createElement("td"); c.className="c-concepto";
    c.innerHTML = '<input class="f concepto-t" placeholder="Concepto"><textarea class="f" rows="1" placeholder="Descripción"></textarea>';
    var ci=c.querySelector("input"), cd=c.querySelector("textarea");
    ci.value=row.concepto||""; cd.value=row.descripcion||"";
    ci.addEventListener("input", function(){ row.concepto=ci.value; save(); });
    cd.addEventListener("input", function(){ row.descripcion=cd.value; autosize(cd); save(); });
    tr.appendChild(c);

    var q = document.createElement("td"); q.className="c-num cell-num";
    q.innerHTML='<input class="f" type="number" min="0" step="1">';
    var qi=q.querySelector("input"); qi.value=row.cantidad;
    qi.addEventListener("input", function(){ row.cantidad=parseFloat(qi.value)||0; imp.textContent=fmt((row.cantidad)*(row.precio)); recalc(); save(); });
    tr.appendChild(q);

    var p = document.createElement("td"); p.className="c-num cell-num";
    p.innerHTML='<input class="f" type="text" inputmode="decimal">';
    var pi=p.querySelector("input");
    function pShow(){ pi.value = fmt(row.precio||0); }
    pShow();
    pi.addEventListener("focus", function(){ pi.value = row.precio ? String(row.precio) : ""; });
    pi.addEventListener("blur", pShow);
    pi.addEventListener("input", function(){ row.precio=parseMoney(pi.value); imp.textContent=fmt((row.cantidad)*(row.precio)); recalc(); save(); });
    tr.appendChild(p);

    var impTd=document.createElement("td"); impTd.className="importe";
    var imp=document.createElement("span"); imp.textContent=fmt((row.cantidad||0)*(row.precio||0));
    impTd.appendChild(imp);
    tr.appendChild(impTd);

    tb.appendChild(tr);
    autosize(cd);
  });
  recalc();
}

function recalc(){
  var sub=0;
  state.rows.forEach(function(r){ sub += (parseFloat(r.cantidad)||0)*(parseFloat(r.precio)||0); });
  var descv = parseFloat(state.descuento)||0;
  var pct = sub>0 ? (descv/sub*100) : 0;
  var pctEl = $("descpct");
  if(pctEl){ pctEl.textContent = descv>0 ? ("· " + (pct%1===0?pct.toFixed(0):pct.toFixed(1)) + "%") : ""; }
  formatDescuento();
  var base = Math.max(0, sub - descv);
  var iva = state.iva ? base*0.16 : 0;
  var total = base + iva;

  $("t_sub").textContent = fmt(sub);
  $("t_iva").textContent = fmt(iva);
  $("ivarow").hidden = !state.iva;
  $("t_total").textContent = fmt(total);
  $("t_cur").textContent = state.currency;

  var cells = $("rows").querySelectorAll(".importe span");
  state.rows.forEach(function(r,idx){ if(cells[idx]) cells[idx].textContent = fmt((r.cantidad||0)*(r.precio||0)); });
}

bindAll();
rebind();
renderRows();
