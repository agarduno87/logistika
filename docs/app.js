(function(){
  "use strict";
  var $=function(i){return document.getElementById(i);};
  document.body.classList.remove("no-js");

  /* Traducción con respaldo: si i18n.js no cargó, se ve el inglés y nada se rompe. */
  function t(key, fallback){
    if (window.ttsI18n && typeof window.ttsI18n.t === "function") { return window.ttsI18n.t(key, fallback); }
    return fallback;
  }
  if($("yr")) $("yr").textContent=String(new Date().getFullYear());

  /* nav */
  var b=$("burger"),n=$("nav");
  if(b&&n){
    b.addEventListener("click",function(){
      var open=n.classList.toggle("open");
      b.setAttribute("aria-expanded",open?"true":"false");
      b.setAttribute("aria-label", open ? t("menu.close","Close menu") : t("menu.open","Open menu"));
    });
    n.addEventListener("click",function(e){if(e.target.tagName==="A"){n.classList.remove("open");b.setAttribute("aria-expanded","false");}});
    document.addEventListener("keydown",function(e){if(e.key==="Escape"&&n.classList.contains("open")){n.classList.remove("open");b.setAttribute("aria-expanded","false");b.focus();}});
  }

  /* ---------------- the travelling dot ----------------
     Progress is computed from how far the journey section has scrolled past
     the viewport centre. Everything here is decoration: if it never runs, the
     rail stays full and every stage stays legible. */
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var journey=$("journey"), fill=$("railfill"), dot=$("raildot"), stopsBox=$("railstops");
  var stages=[].slice.call(document.querySelectorAll("[data-stage]"));

  if(journey && fill && dot && stages.length && !reduce){
    /* one tick mark per stage, evenly spaced along the rail */
    stages.forEach(function(_,i){
      var s=document.createElement("span");
      s.className="railstop";
      s.style.top=((i+0.5)/stages.length*100)+"%";
      stopsBox.appendChild(s);
    });
    var stops=[].slice.call(stopsBox.children);

    var ticking=false;
    function update(){
      ticking=false;
      var rect=journey.getBoundingClientRect();
      var mid=window.innerHeight*0.5;
      var total=rect.height;
      var travelled=Math.min(Math.max(mid-rect.top,0),total);
      var pct=total>0 ? travelled/total : 0;

      fill.style.height=(pct*100)+"%";
      dot.style.top=(pct*100)+"%";
      stops.forEach(function(s,i){
        s.classList.toggle("done",(i+0.5)/stages.length<=pct);
      });
    }
    function onScroll(){ if(!ticking){ ticking=true; window.requestAnimationFrame(update); } }
    window.addEventListener("scroll",onScroll,{passive:true});
    window.addEventListener("resize",onScroll);
    update();

    /* highlight the stage the reader is actually on */
    if("IntersectionObserver" in window){
      var io=new IntersectionObserver(function(entries){
        entries.forEach(function(e){ e.target.classList.toggle("active", e.isIntersecting); });
      },{rootMargin:"-38% 0px -38% 0px"});
      stages.forEach(function(s){ io.observe(s); });
    } else {
      stages.forEach(function(s){ s.classList.add("active"); });
    }
  } else {
    stages.forEach(function(s){ s.classList.add("active"); });
    if(fill) fill.style.height="100%";
    if(dot) dot.style.display="none";
  }

  /* form */
  var f=$("form"),st=$("st"),ts=$("ts"),btn=f?f.querySelector('button[type="submit"]'):null;
  if(!f||!st) return;
  if(ts) ts.value=String(Date.now());
  var idleLabel = btn ? btn.textContent : "";

  function say(message, state){
    st.textContent = message;
    if (state) { st.setAttribute("data-state", state); } else { st.removeAttribute("data-state"); }
  }

  f.addEventListener("submit",function(e){
    e.preventDefault();

    /* Abierto con file:// no hay servidor al que enviar: se dice, no se falla en silencio. */
    if (window.location.protocol === "file:") {
      say(t("msg.fileProtocol","Open the site over http:// to send the form. Run ./run.sh and use http://127.0.0.1:8000"), "error");
      return;
    }
    /* Honeypot: si viene lleno es un bot. Se acepta en silencio para no avisarle.
       Se accede por f.elements y no por f.website: el acceso por nombre directo
       en el formulario no está garantizado en todos los entornos, y si devuelve
       undefined la trampa deja de existir sin que nadie lo note. */
    var trap = f.elements.website;
    if (trap && trap.value !== "") { say(t("msg.thanks","Thanks — we will be in touch."), null); return; }
    /* Trampa de tiempo, revalidada en el servidor. */
    if (ts && Date.now() - Number(ts.value) < 3000) { say(t("msg.tooFast","Take a moment to describe your operation, then send."), "error"); return; }
    if (!f.checkValidity()) { say(t("msg.invalid","Check the company, email and description fields."), "error"); f.reportValidity(); return; }

    var payload = {
      company: f.elements.company.value.trim(),
      email: f.elements.email.value.trim(),
      stage: f.elements.stage.value,
      message: f.elements.message.value.trim(),
      website: "",
      rendered_at: ts ? Number(ts.value) : 0,
      locale: window.ttsI18n ? window.ttsI18n.current : "en"
    };

    var controller = new AbortController();
    var timer = setTimeout(function(){ controller.abort(); }, 15000);

    if (btn) { idleLabel = btn.textContent; btn.disabled = true; btn.textContent = t("form.sending","Sending…"); }
    say(t("msg.sending","Sending your message…"), "sending");

    fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify(payload),
      credentials: "same-origin",
      signal: controller.signal
    })
      .then(function(r){
        clearTimeout(timer);
        if (r.ok) {
          f.reset();
          if (ts) { ts.value = String(Date.now()); }
          say(t("msg.sent","Message sent. You will get a written reply within one business day."), null);
          return;
        }
        if (r.status === 429) { say(t("msg.rate","Too many messages from this connection. Try again in an hour."), "error"); return; }
        if (r.status === 400 || r.status === 422) { say(t("msg.invalid","Check the company, email and description fields."), "error"); return; }
        say(t("msg.error","The message could not be sent right now. Please try again in a few minutes."), "error");
      })
      .catch(function(){
        clearTimeout(timer);
        say(t("msg.connection","Connection problem — the message was not sent. Please try again."), "error");
      })
      .then(function(){ if (btn) { btn.disabled = false; btn.textContent = idleLabel; } });
  });
})();
