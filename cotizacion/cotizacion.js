"use strict";
var KEY = "logistika-cotizacion-v1";

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
    folio:"COT-" + yy + "-001",
    fecha:fmtDate(hoy),
    vigencia:"15 días · vence " + fmtDate(vig),
    emisor:{razon:"", rfc:""},
    cliente:{empresa:"Empresa Ejemplo, S.A. de C.V.", contacto:"Nombre del contacto", correo:"contacto@empresa.com", telefono:"+52 442 000 0000", direccion:"Ciudad, Estado"},
    currency:"MXN", iva:true, descuento:0,
    rows:[
      {concepto:CATALOG.healthcheck.concepto, descripcion:CATALOG.healthcheck.descripcion, cantidad:1, precio:0},
      {concepto:CATALOG.manage.concepto, descripcion:CATALOG.manage.descripcion, cantidad:1, precio:0}
    ],
    notas:"Cotización sujeta a diagnóstico y a confirmación de alcance. Tiempos de entrega y entregables se detallan en la propuesta. Cualquier trabajo fuera del alcance acordado se cotiza por separado. logistika no es agencia aduanal, forwarder ni transportista."
  };
}

var state = load();

function load(){
  try{ var raw = localStorage.getItem(KEY); if(raw){ return JSON.parse(raw); } }catch(e){}
  return defaults();
}
function save(){ try{ localStorage.setItem(KEY, JSON.stringify(state)); }catch(e){} }

function locale(){ return state.currency === "MXN" ? "es-MX" : "en-US"; }
function fmt(n){
  n = isFinite(n) ? n : 0;
  try{ return new Intl.NumberFormat(locale(), {style:"currency", currency:state.currency, minimumFractionDigits:2, maximumFractionDigits:2}).format(n); }
  catch(e){ return "$" + n.toFixed(2); }
}

function $(id){ return document.getElementById(id); }

function bindText(id, get, set){
  var el = $(id); if(!el) return;
  el.value = get() || "";
  el.addEventListener("input", function(){ set(el.value); save(); });
}
function autosize(t){ t.style.height="auto"; t.style.height=(t.scrollHeight)+"px"; }

function bindAll(){
  bindText("folio", function(){return state.folio;}, function(v){state.folio=v;});
  bindText("fecha", function(){return state.fecha;}, function(v){state.fecha=v;});
  bindText("vigencia", function(){return state.vigencia;}, function(v){state.vigencia=v;});
  bindText("em_razon", function(){return state.emisor.razon;}, function(v){state.emisor.razon=v;});
  bindText("em_rfc", function(){return state.emisor.rfc;}, function(v){state.emisor.rfc=v;});
  bindText("cl_empresa", function(){return state.cliente.empresa;}, function(v){state.cliente.empresa=v;});
  bindText("cl_contacto", function(){return state.cliente.contacto;}, function(v){state.cliente.contacto=v;});
  bindText("cl_correo", function(){return state.cliente.correo;}, function(v){state.cliente.correo=v;});
  bindText("cl_telefono", function(){return state.cliente.telefono;}, function(v){state.cliente.telefono=v;});
  bindText("cl_direccion", function(){return state.cliente.direccion;}, function(v){state.cliente.direccion=v;});

  var notas = $("notas");
  notas.value = state.notas || "";
  notas.addEventListener("input", function(){ state.notas=notas.value; autosize(notas); save(); });

  var desc = $("descuento");
  desc.value = state.descuento || 0;
  desc.addEventListener("input", function(){ state.descuento = parseFloat(desc.value)||0; recalc(); save(); });

  $("ivachk").checked = !!state.iva;
  $("ivachk").addEventListener("change", function(){ state.iva=this.checked; recalc(); save(); });

  var seg = $("curseg");
  seg.querySelectorAll("button").forEach(function(b){
    b.setAttribute("aria-pressed", b.dataset.cur===state.currency ? "true":"false");
    b.addEventListener("click", function(){
      state.currency = b.dataset.cur; save();
      seg.querySelectorAll("button").forEach(function(x){ x.setAttribute("aria-pressed", x.dataset.cur===state.currency?"true":"false"); });
      recalc();
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
  $("resetbtn").addEventListener("click", function(){
    if(!confirm("¿Reiniciar la cotización a la plantilla de ejemplo? Se borra lo que escribiste en este navegador.")) return;
    try{ localStorage.removeItem(KEY); }catch(e){}
    state = defaults(); rebind(); renderRows();
  });
}

function rebind(){
  ["folio","fecha","vigencia"].forEach(function(k){ $(k).value = state[k]||""; });
  $("em_razon").value=state.emisor.razon||""; $("em_rfc").value=state.emisor.rfc||"";
  $("cl_empresa").value=state.cliente.empresa||""; $("cl_contacto").value=state.cliente.contacto||"";
  $("cl_correo").value=state.cliente.correo||""; $("cl_telefono").value=state.cliente.telefono||"";
  $("cl_direccion").value=state.cliente.direccion||"";
  $("notas").value=state.notas||""; autosize($("notas"));
  $("descuento").value=state.descuento||0;
  $("ivachk").checked=!!state.iva;
  $("curseg").querySelectorAll("button").forEach(function(x){ x.setAttribute("aria-pressed", x.dataset.cur===state.currency?"true":"false"); });
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
    p.innerHTML='<input class="f" type="number" min="0" step="100">';
    var pi=p.querySelector("input"); pi.value=row.precio;
    pi.addEventListener("input", function(){ row.precio=parseFloat(pi.value)||0; imp.textContent=fmt((row.cantidad)*(row.precio)); recalc(); save(); });
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
