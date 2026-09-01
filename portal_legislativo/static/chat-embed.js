(function () {
  "use strict";

  /* =========================================================
     CONFIGURACIÓN
     ========================================================= */

  const tag = document.currentScript;

  if (!tag) {
    console.error("Asistente Institucional: no se encontró el script.");
    return;
  }

  /*
   * IMPORTANTE:
   * Este archivo vive en el Portal Legislativo.
   * Página Express solo lo carga mediante <script>.
   *
   * LOCAL:
   *   http://127.0.0.1:5000
   * PRODUCCIÓN:
   *   https://portal-legislativo.tu-dominio.bo
   *
   * Las URLs se pueden cambiar desde los atributos del <script>
   * sin modificar este archivo.
   */

  const base = new URL(tag.src, window.location.href).origin;

  const cfg = {
    apiUrl:
      tag.getAttribute("api-url") ||
      `${base}/api/chat`,

    avatar:
      tag.getAttribute("avatar") ||
      `${base}/static/cara2/9.png`,

    avatarThinking:
      tag.getAttribute("avatar-thinking") ||
      `${base}/static/cara2/8.png`,

    avatarViewing:
      tag.getAttribute("avatar-viewing") ||
      `${base}/static/cara2/10.png`,

    avatarResponding:
      tag.getAttribute("avatar-responding") ||
      `${base}/static/cara2/9.png`,

    title:
      tag.getAttribute("title") ||
      "Asistente Institucional",

    subtitle:
      tag.getAttribute("subtitle") ||
      "Senado",

    primaryColor:
      tag.getAttribute("primary-color") ||
      "#1a237e",

    trackingUrl:
      tag.getAttribute("tracking-url") ||
      `${base}/track-document`,

    requestTimeout:
      Number(tag.getAttribute("request-timeout")) ||
      30000,

    welcome:
      tag.getAttribute("welcome-message") ||
      "¡Hola! ¿En qué puedo ayudarte?"
  };


  /* =========================================================
     EVITAR CARGAR EL CHAT DOS VECES
     ========================================================= */

  if (window.__senadoChatWidgetLoaded) {
    console.warn(
      "Asistente Institucional: el widget ya fue cargado."
    );
    return;
  }

  window.__senadoChatWidgetLoaded = true;


  /* =========================================================
     ESTILOS
     ========================================================= */

  const style = document.createElement("style");

  style.textContent = `

    #slcw-root,
    #slcw-root * {
      box-sizing: border-box;
    }

    #slcw-root {
      font-family:
        Arial,
        Helvetica,
        sans-serif;
    }


    /* =====================================================
       BOTÓN FLOTANTE
       ===================================================== */

    #slcw-btn {
      position: fixed;

      right: 20px;
      bottom: 20px;

      width: 68px;
      height: 68px;

      border: 0;
      border-radius: 50%;

      background: ${cfg.primaryColor};

      box-shadow:
        0 5px 22px rgba(0, 0, 0, 0.25);

      padding: 4px;

      cursor: pointer;

      z-index: 2147483000;

      transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
    }


    #slcw-btn:hover {
      transform: scale(1.05);

      box-shadow:
        0 7px 26px rgba(0, 0, 0, 0.30);
    }


    #slcw-btn:active {
      transform: scale(0.96);
    }


    #slcw-btn img {
      width: 100%;
      height: 100%;

      border-radius: 50%;

      object-fit: cover;

      background: #ffffff;

      display: block;
    }


    /* =====================================================
       VENTANA DEL CHAT
       ===================================================== */

    #slcw-window {
      position: fixed;

      right: 20px;
      bottom: 100px;

      width: 390px;
      height: 590px;

      max-width:
        calc(100vw - 30px);

      max-height:
        calc(100vh - 120px);

      background: #ffffff;

      border-radius: 18px;

      overflow: hidden;

      box-shadow:
        0 12px 45px rgba(0, 0, 0, 0.25);

      display: none;

      flex-direction: column;

      z-index: 2147482999;

      border: 1px solid rgba(0, 0, 0, 0.08);
    }


    #slcw-window.open {
      display: flex;
    }


    /* =====================================================
       CABECERA
       ===================================================== */

    #slcw-head {
      background: ${cfg.primaryColor};

      color: #ffffff;

      padding: 13px 15px;

      display: flex;

      align-items: center;

      gap: 10px;

      flex-shrink: 0;
    }


    #slcw-head img {
      width: 44px;
      height: 44px;

      border-radius: 50%;

      object-fit: cover;

      background: #ffffff;

      display: block;
    }


    #slcw-head-info {
      flex: 1;

      min-width: 0;
    }


    #slcw-title {
      font-size: 16px;

      font-weight: 700;

      display: block;

      overflow: hidden;

      text-overflow: ellipsis;

      white-space: nowrap;
    }


    #slcw-sub {
      font-size: 12px;

      opacity: 0.85;

      display: block;

      margin-top: 2px;
    }


    #slcw-close {
      border: 0;

      background: transparent;

      color: #ffffff;

      font-size: 28px;

      cursor: pointer;

      line-height: 1;

      width: 36px;

      height: 36px;

      display: flex;

      align-items: center;

      justify-content: center;

      border-radius: 50%;
    }


    #slcw-close:hover {
      background: rgba(255, 255, 255, 0.12);
    }


    /* =====================================================
       ESTADO DEL ASISTENTE
       ===================================================== */

    #slcw-state {
      display: none;

      align-items: center;

      gap: 8px;

      padding: 8px 14px;

      background: #f4f6f8;

      border-bottom: 1px solid #e5e7eb;

      font-size: 12px;

      color: #555555;

      flex-shrink: 0;
    }


    #slcw-state.show {
      display: flex;
    }


    #slcw-state img {
      width: 28px;
      height: 28px;

      border-radius: 50%;

      object-fit: cover;

      background: #ffffff;

      display: block;
    }


    /* =====================================================
       MENSAJES
       ===================================================== */

    #slcw-messages {
      flex: 1;

      overflow-y: auto;

      padding: 16px;

      background: #f7f8fa;

      scroll-behavior: smooth;
    }


    #slcw-messages::-webkit-scrollbar {
      width: 6px;
    }


    #slcw-messages::-webkit-scrollbar-thumb {
      background: #c7cbd1;

      border-radius: 10px;
    }


    .slcw-msg {
      display: flex;

      margin: 0 0 11px;
    }


    .slcw-msg.user {
      justify-content: flex-end;
    }


    .slcw-bubble {
      max-width: 82%;

      padding: 10px 13px;

      border-radius: 15px;

      font-size: 14px;

      line-height: 1.48;

      white-space: pre-wrap;

      overflow-wrap: anywhere;

      word-break: break-word;
    }


    .slcw-msg.bot .slcw-bubble {
      background: #ffffff;

      color: #222222;

      border-bottom-left-radius: 4px;

      box-shadow:
        0 1px 4px rgba(0, 0, 0, 0.08);
    }


    .slcw-msg.user .slcw-bubble {
      background: ${cfg.primaryColor};

      color: #ffffff;

      border-bottom-right-radius: 4px;
    }


    /* =====================================================
       BOTÓN SEGUIMIENTO
       ===================================================== */

    #slcw-track {
      display: none;

      margin: 0 14px 10px;

      border: 0;

      border-radius: 10px;

      padding: 9px 12px;

      background: #eef1ff;

      color: ${cfg.primaryColor};

      font-size: 12px;

      cursor: pointer;

      flex-shrink: 0;
    }


    #slcw-track.show {
      display: block;
    }


    #slcw-track:hover {
      filter: brightness(0.97);
    }


    /* =====================================================
       PIE / INPUT
       ===================================================== */

    #slcw-foot {
      padding: 9px;

      border-top: 1px solid #e5e7eb;

      background: #ffffff;

      display: flex;

      gap: 6px;

      align-items: center;

      flex-shrink: 0;
    }


    #slcw-input {
      flex: 1;

      border: 1px solid #d5d9df;

      border-radius: 22px;

      padding: 10px 13px;

      outline: 0;

      font-size: 14px;

      min-width: 0;

      background: #ffffff;

      color: #222222;
    }


    #slcw-input:focus {
      border-color: ${cfg.primaryColor};

      box-shadow:
        0 0 0 2px rgba(26, 35, 126, 0.08);
    }


    #slcw-input::placeholder {
      color: #8a8f98;
    }


    .slcw-action {
      width: 38px;

      height: 38px;

      min-width: 38px;

      border-radius: 50%;

      border: 0;

      cursor: pointer;

      background: ${cfg.primaryColor};

      color: #ffffff;

      font-size: 17px;

      display: flex;

      align-items: center;

      justify-content: center;
    }


    .slcw-action:hover {
      filter: brightness(1.08);
    }


    .slcw-action:disabled {
      opacity: 0.5;

      cursor: not-allowed;
    }


    #slcw-mic {
      background: transparent;

      color: ${cfg.primaryColor};

      font-size: 18px;
    }


    /* =====================================================
       INDICADOR DE ERROR
       ===================================================== */

    .slcw-error {
      color: #8b1e1e !important;

      background: #fff2f2 !important;
    }


    /* =====================================================
       RESPONSIVE
       ===================================================== */

    @media (max-width: 480px) {

      #slcw-window {
        right: 0;

        bottom: 0;

        width: 100vw;

        height: 100vh;

        max-width: none;

        max-height: none;

        border-radius: 0;
      }


      #slcw-btn {
        right: 14px;

        bottom: 14px;

        width: 58px;

        height: 58px;
      }


      #slcw-bubble {
        max-width: 88%;
      }
    }


    /* =====================================================
       REDUCCIÓN DE MOVIMIENTO
       ===================================================== */

    @media (prefers-reduced-motion: reduce) {

      #slcw-btn {
        transition: none;
      }

      #slcw-messages {
        scroll-behavior: auto;
      }
    }

  `;

  document.head.appendChild(style);


  /* =========================================================
     HTML DEL WIDGET
     ========================================================= */

  const root = document.createElement("div");

  root.id = "slcw-root";

  root.innerHTML = `

    <!-- BOTÓN -->

    <button
      id="slcw-btn"
      type="button"
      aria-label="Abrir asistente institucional"
      title="Abrir asistente"
    >

      <img
        src="${escapeHtml(cfg.avatar)}"
        alt="Asistente Institucional"
      >

    </button>


    <!-- VENTANA -->

    <section
      id="slcw-window"
      aria-label="Asistente Institucional"
      role="dialog"
      aria-modal="false"
    >


      <!-- CABECERA -->

      <header id="slcw-head">

        <img
          id="slcw-head-img"
          src="${escapeHtml(cfg.avatar)}"
          alt="Asistente Institucional"
        >


        <div id="slcw-head-info">

          <span id="slcw-title">
            ${escapeHtml(cfg.title)}
          </span>

          <span id="slcw-sub">
            ${escapeHtml(cfg.subtitle)}
          </span>

        </div>


        <button
          id="slcw-close"
          type="button"
          aria-label="Cerrar asistente"
          title="Cerrar"
        >
          ×
        </button>

      </header>


      <!-- ESTADO -->

      <div id="slcw-state">

        <img
          id="slcw-state-img"
          src="${escapeHtml(cfg.avatarThinking)}"
          alt=""
        >

        <span id="slcw-state-text">
          El asistente está pensando...
        </span>

      </div>


      <!-- MENSAJES -->

      <main
        id="slcw-messages"
        aria-live="polite"
        aria-label="Conversación"
      ></main>


      <!-- SEGUIMIENTO -->

      <button
        id="slcw-track"
        type="button"
      >
        Consultar seguimiento del trámite
      </button>


      <!-- PIE -->

      <footer id="slcw-foot">

        <button
          class="slcw-action"
          id="slcw-mic"
          type="button"
          title="Hablar"
          aria-label="Hablar"
        >
          🎙️
        </button>


        <input
          id="slcw-input"
          type="text"
          placeholder="Escribe tu consulta..."
          autocomplete="off"
          aria-label="Escribe tu consulta"
        >


        <button
          class="slcw-action"
          id="slcw-send"
          type="button"
          title="Enviar"
          aria-label="Enviar"
        >
          ➤
        </button>

      </footer>

    </section>

  `;


  document.body.appendChild(root);


  /* =========================================================
     REFERENCIAS
     ========================================================= */

  const $ = (id) =>
    document.getElementById(id);


  const btn =
    $("slcw-btn");

  const win =
    $("slcw-window");

  const close =
    $("slcw-close");

  const input =
    $("slcw-input");

  const send =
    $("slcw-send");

  const mic =
    $("slcw-mic");

  const messages =
    $("slcw-messages");

  const state =
    $("slcw-state");

  const stateImg =
    $("slcw-state-img");

  const stateText =
    $("slcw-state-text");

  const track =
    $("slcw-track");


  /* =========================================================
     SESIÓN
     ========================================================= */

  const sessionKey =
    "senado_chat_session";


  let sessionId =
    null;


  try {

    sessionId =
      sessionStorage.getItem(sessionKey);

  } catch (error) {

    console.warn(
      "No se pudo acceder a sessionStorage.",
      error
    );

  }


  if (!sessionId) {

    try {

      if (
        window.crypto &&
        typeof window.crypto.randomUUID === "function"
      ) {

        sessionId =
          window.crypto.randomUUID();

      } else {

        sessionId =
          Date.now() +
          "-" +
          Math.random()
            .toString(36)
            .substring(2);

      }

    } catch (error) {

      sessionId =
        Date.now() +
        "-" +
        Math.random()
          .toString(36)
          .substring(2);

    }


    try {

      sessionStorage.setItem(
        sessionKey,
        sessionId
      );

    } catch (error) {

      console.warn(
        "No se pudo guardar la sesión.",
        error
      );

    }

  }


  /* =========================================================
     ESCAPAR HTML
     ========================================================= */

  function escapeHtml(value) {

    const div =
      document.createElement("div");

    div.textContent =
      String(value ?? "");

    return div.innerHTML;
  }


  /* =========================================================
     AGREGAR MENSAJE
     ========================================================= */

  function add(type, text) {

    const row =
      document.createElement("div");

    row.className =
      "slcw-msg " + type;


    const bubble =
      document.createElement("div");

    bubble.className =
      "slcw-bubble";


    bubble.textContent =
      String(text ?? "");


    row.appendChild(bubble);

    messages.appendChild(row);


    messages.scrollTop =
      messages.scrollHeight;


    return row;
  }


  /* =========================================================
     MENSAJE INICIAL
     ========================================================= */

  add(
    "bot",
    cfg.welcome
  );


  /* =========================================================
     ESTADO DEL ASISTENTE
     ========================================================= */

  function setState(
    on,
    mode = "thinking"
  ) {

    state.classList.toggle(
      "show",
      Boolean(on)
    );


    if (!on) {
      return;
    }


    if (mode === "viewing") {

      stateImg.src =
        cfg.avatarViewing;

      stateText.textContent =
        "Estoy consultando la información...";

    }

    else if (mode === "responding") {

      stateImg.src =
        cfg.avatarResponding;

      stateText.textContent =
        "Estoy preparando la respuesta...";

    }

    else {

      stateImg.src =
        cfg.avatarThinking;

      stateText.textContent =
        "El asistente está pensando...";

    }

  }


  /* =========================================================
     ABRIR CHAT
     ========================================================= */

  function openChat() {

    win.classList.add("open");

    btn.style.display =
      "none";

    setTimeout(() => {

      input.focus();

    }, 50);

  }


  /* =========================================================
     CERRAR CHAT
     ========================================================= */

  function closeChat() {

    win.classList.remove("open");

    btn.style.display =
      "block";

  }


  btn.addEventListener(
    "click",
    openChat
  );


  close.addEventListener(
    "click",
    closeChat
  );


  /* =========================================================
     ESCAPE PARA CERRAR
     ========================================================= */

  document.addEventListener(
    "keydown",
    function (event) {

      if (
        event.key === "Escape" &&
        win.classList.contains("open")
      ) {

        closeChat();

      }

    }
  );


  /* =========================================================
     BOTÓN DE SEGUIMIENTO
     ========================================================= */

  track.addEventListener(
    "click",
    function () {

      window.open(
        cfg.trackingUrl,
        "_blank",
        "noopener,noreferrer"
      );

    }
  );


  /* =========================================================
     CONTROL DE ENVÍO
     ========================================================= */

  let busy = false;


  /* =========================================================
     DETECTAR SI LA RESPUESTA ES DE TRÁMITE
     ========================================================= */

  function containsTrackingInfo(text) {

    return /tr[aá]mite|seguimiento|documento|c[oó]digo|consulta.*estado/i
      .test(
        String(text ?? "")
      );

  }


  /* =========================================================
     ENVIAR MENSAJE
     ========================================================= */

  async function sendMessage() {

    const text =
      input.value.trim();


    if (!text) {
      return;
    }


    if (busy) {
      return;
    }


    /* -----------------------------
       Mostrar pregunta
       ----------------------------- */

    add(
      "user",
      text
    );


    input.value = "";


    /* -----------------------------
       Estado ocupado
       ----------------------------- */

    busy = true;

    send.disabled = true;

    mic.disabled = true;


    track.classList.remove(
      "show"
    );


    /* -----------------------------
       Pensando
       ----------------------------- */

    setState(
      true,
      "thinking"
    );


    /*
     * Después de unos milisegundos
     * mostramos el estado "consultando".
     */

    const viewingTimer =
      setTimeout(
        function () {

          if (busy) {

            setState(
              true,
              "viewing"
            );

          }

        },
        350
      );


    try {

      /* =====================================================
         PETICIÓN AL PORTAL LEGISLATIVO
         ===================================================== */

      const controller =
        new AbortController();

      const timeoutId =
        setTimeout(function () {
          controller.abort();
        }, cfg.requestTimeout);

      const response =
        await fetch(
          cfg.apiUrl,
          {
            method: "POST",

            headers: {

              "Content-Type":
                "application/json",

              "Accept":
                "application/json"

            },

            /*
             * NO dependemos de cookies entre dominios.
             * El session_id viaja explícitamente en JSON.
             */

            credentials:
              "omit",

            signal:
              controller.signal,

            body:
              JSON.stringify({

                /*
                 * Tu backend puede utilizar
                 * cualquiera de estos campos.
                 */

                mensaje:
                  text,

                message:
                  text,

                /*
                 * Mantiene la conversación
                 * independiente por visitante.
                 */

                session_id:
                  sessionId

              })

          }
        );

      clearTimeout(timeoutId);


      /* =====================================================
         LEER RESPUESTA
         ===================================================== */

      const contentType =
        response.headers.get(
          "content-type"
        ) || "";


      let data;


      if (
        contentType.includes(
          "application/json"
        )
      ) {

        data =
          await response.json();

      } else {

        const raw =
          await response.text();

        data = {
          error:
            raw ||
            "El servidor no devolvió JSON."
        };

      }


      /* =====================================================
         ERROR HTTP
         ===================================================== */

      if (!response.ok) {

        throw new Error(
          data.error ||
          data.message ||
          "Error HTTP " +
            response.status
        );

      }


      /* =====================================================
         ESTADO RESPONDIENDO
         ===================================================== */

      clearTimeout(
        viewingTimer
      );


      setState(
        true,
        "responding"
      );


      /* =====================================================
         OBTENER RESPUESTA
         ===================================================== */

      const answer =
        data.respuesta ??
        data.message ??
        data.response ??
        data.answer ??
        "No se pudo procesar tu consulta.";


      /* =====================================================
         MOSTRAR RESPUESTA
         ===================================================== */

      setTimeout(
        function () {

          add(
            "bot",
            String(answer)
          );


          setState(
            false
          );


          busy = false;

          send.disabled =
            false;

          mic.disabled =
            false;


          /* -----------------------------
             Mostrar seguimiento
             ----------------------------- */

          if (
            containsTrackingInfo(
              answer
            )
          ) {

            track.classList.add(
              "show"
            );

          }

        },
        250
      );

    }

    catch (error) {

      clearTimeout(
        viewingTimer
      );

      if (error && error.name === "AbortError") {
        error = new Error(
          "El Portal Legislativo tardó demasiado en responder. Intenta nuevamente."
        );
      }


      console.error(
        "Asistente Institucional:",
        error
      );


      /* =====================================================
         MENSAJE DE ERROR
         ===================================================== */

      add(
        "bot",
        "Lo siento, hubo un error al conectar con el asistente. Verifica que el servidor institucional esté funcionando e intenta nuevamente."
      );


      setState(
        false
      );


      busy = false;

      send.disabled =
        false;

      mic.disabled =
        false;

    }

  }


  /* =========================================================
     BOTÓN ENVIAR
     ========================================================= */

  send.addEventListener(
    "click",
    sendMessage
  );


  /* =========================================================
     ENTER PARA ENVIAR
     ========================================================= */

  input.addEventListener(
    "keydown",
    function (event) {

      if (
        event.key === "Enter" &&
        !event.shiftKey
      ) {

        event.preventDefault();

        sendMessage();

      }

    }
  );


  /* =========================================================
     RECONOCIMIENTO DE VOZ
     ========================================================= */

  mic.addEventListener(
    "click",
    function () {

      const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


      /* -----------------------------
         Comprobar compatibilidad
         ----------------------------- */

      if (!SpeechRecognition) {

        alert(
          "Tu navegador no soporta reconocimiento de voz."
        );

        return;

      }


      /* -----------------------------
         Crear reconocimiento
         ----------------------------- */

      const recognition =
        new SpeechRecognition();


      recognition.lang =
        "es-BO";


      recognition.continuous =
        false;


      recognition.interimResults =
        false;


      recognition.maxAlternatives =
        1;


      /* -----------------------------
         Comenzar
         ----------------------------- */

      try {

        recognition.start();

      }

      catch (error) {

        console.error(
          "No se pudo iniciar el reconocimiento de voz:",
          error
        );

      }


      /* -----------------------------
         Resultado
         ----------------------------- */

      recognition.onresult =
        function (event) {

          const transcript =
            event.results[0][0].transcript;


          input.value =
            transcript;


          sendMessage();

        };


      /* -----------------------------
         Error
         ----------------------------- */

      recognition.onerror =
        function (event) {

          console.error(
            "Error de reconocimiento de voz:",
            event.error
          );

        };


      /* -----------------------------
         Finalización
         ----------------------------- */

      recognition.onend =
        function () {

          console.log(
            "Reconocimiento de voz finalizado."
          );

        };

    }
  );


  /* =========================================================
     MOSTRAR INFORMACIÓN DE CONFIGURACIÓN
     ========================================================= */

  console.log(
    "Asistente Institucional cargado correctamente."
  );

  console.log(
    "API:",
    cfg.apiUrl
  );

})();