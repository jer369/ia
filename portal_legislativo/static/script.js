let categoriaActual = null;
let esperandoCodigo = false;
let esperandoPassword = false;
let codigoTramite = "";
let estadoTimer = null;





function el(id) {
    return document.getElementById(id);
}

/* ============================================================
   CARAS DEL ASISTENTE / static/cara2/1.png ... 12.png
============================================================ */
const CARAS_ASISTENTE = {
    pensando: [1, 2, 3, 4],
    viendo: [5, 6, 7, 8],
    respondiendo: [9, 10, 11, 12]
};

const caraIndex = { pensando: 0, viendo: 0, respondiendo: 0 };

function rutaCara(numero) {
    return `/static/cara2/${numero}.png`;
}

function siguienteCara(estado = "respondiendo") {
    const grupo = CARAS_ASISTENTE[estado] || CARAS_ASISTENTE.respondiendo;
    const numero = grupo[caraIndex[estado] % grupo.length];
    caraIndex[estado] = (caraIndex[estado] + 1) % grupo.length;
    return rutaCara(numero);
}

function crearAvatarAsistente(estado = "respondiendo") {
    const avatar = document.createElement("img");
    avatar.className = `mensaje-avatar estado-${estado}`;
    avatar.src = siguienteCara(estado);
    avatar.alt = "Asistente Institucional";
    avatar.loading = "lazy";
    avatar.onerror = () => avatar.remove();
    return avatar;
}

function actualizarEstadoAsistente(estado, titulo, texto) {
    const panel = el("chatPensando");
    const imagen = el("chatPensandoImg");
    if (!panel || !imagen) return;
    imagen.src = siguienteCara(estado);
    imagen.alt = titulo || "Estado del asistente";
    el("chatEstadoTitulo").textContent = titulo || "Pensando…";
    el("chatEstadoTexto").textContent = texto || "Estoy revisando la información.";
    panel.dataset.estado = estado;
    panel.style.display = "flex";
}

function ocultarEstadoAsistente() {
    const panel = el("chatPensando");
    if (panel) panel.style.display = "none";
}

function iniciarAnimacionCarasPrincipales() {
    const header = el("chatHeaderAvatar");
    const flotante = el("botonChatAvatar");
    if (!header && !flotante) return;

    let numero = 9;
    setInterval(() => {
        numero = numero >= 12 ? 1 : numero + 1;
        const src = rutaCara(numero);
        [header, flotante].forEach((img) => {
            if (!img) return;
            img.classList.add("cambiando-cara");
            setTimeout(() => {
                img.src = src;
                img.classList.remove("cambiando-cara");
            }, 120);
        });
    }, 1800);
}

document.addEventListener("DOMContentLoaded", iniciarAnimacionCarasPrincipales);


/* ============================================================
   ABRIR / CERRAR CHAT
============================================================ */

function abrirChat() {

    const chatbot = el("chatbot");

    chatbot.classList.add("activo");

    if (el("chatMensajes").children.length === 0) {

        mensajeAsistente(
            "Hola 👋<br><br>" +
            "Soy el <strong>Asistente Institucional del Senado</strong>.<br><br>" +
            "Hazme directamente tu pregunta. Puedes consultar sobre trámites, leyes, " +
            "senadores, fiscalización o cualquier información institucional."
        );
    }

    el("entradaChat").focus();
}


function cerrarChat() {
    el("chatbot").classList.remove("activo");
}




/* ============================================================
   CONSULTA DE TRÁMITES
============================================================ */

function iniciarConsultaTramite() {

    esperandoCodigo = true;

    esperandoPassword = false;

    codigoTramite = "";


    mensajeAsistente(
        "Claro. Pásame el <strong>código del trámite</strong>."
    );


    el("entradaChat").placeholder =
        "Escribe el código del trámite...";

    el("entradaChat").focus();
}


/* ============================================================
   PROCESAR MENSAJE
============================================================ */

function procesarMensaje(mensaje) {

    const normalizado =
        mensaje.toLowerCase().trim();


    /* CANCELAR */

    if (
        normalizado === "cancelar" ||
        normalizado === "cancelar consulta"
    ) {

        esperandoCodigo = false;

        esperandoPassword = false;

        codigoTramite = "";

        el("entradaChat").placeholder =
            "Escribe tu consulta...";


        mensajeAsistente(
            "De acuerdo. Cancelé la consulta del trámite."
        );


        return;
    }


    /* ESPERANDO CÓDIGO */

    if (esperandoCodigo) {

        codigoTramite = mensaje;

        esperandoCodigo = false;

        esperandoPassword = true;


        mensajeAsistente(
            "Ahora pásame la <strong>contraseña</strong>."
        );


        el("entradaChat").placeholder =
            "Escribe la contraseña...";

        return;
    }


    /* ESPERANDO CONTRASEÑA */

    if (esperandoPassword) {

        esperandoPassword = false;

        el("entradaChat").placeholder =
            "Escribe otra consulta...";


        consultarTramite(
            codigoTramite,
            mensaje
        );

        return;
    }


    /* DETECTAR CONSULTA DE TRÁMITE */

    if (
        /\btr[aá]mite(s)?\b/.test(normalizado) &&
        /(consult|segu|estado|c[oó]digo)/.test(normalizado)
    ) {

        iniciarConsultaTramite();

        return;
    }


    enviarPregunta(mensaje);
}


/* ============================================================
   ENVIAR MENSAJE
============================================================ */

function enviarMensaje() {

    const input = el("entradaChat");

    const mensaje =
        input.value.trim();


    if (!mensaje) return;


    input.value = "";

    mensajeUsuario(mensaje);

    procesarMensaje(mensaje);
}


/* ============================================================
   CHAT NORMAL
============================================================ */

async function enviarPregunta(pregunta) {

    mostrarCargando();
    clearTimeout(estadoTimer);
    estadoTimer = setTimeout(() => {
        actualizarEstadoAsistente("viendo", "Viendo la información…", "Estoy consultando las fuentes disponibles.");
    }, 350);


    try {

        const response = await fetch(
            "/api/chat",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    pregunta: pregunta
                })
            }
        );


        const data =
            await response.json();


        quitarCargando();


        if (
            !response.ok ||
            data.error
        ) {

            mensajeAsistente(
                data.error ||
                "Tuve un problema al procesar la consulta."
            );

            return;
        }


        mensajeAsistente(
            data.respuesta ||
            "No encontré una respuesta para esa consulta.",
            "respondiendo",
            data.enlace_senador || null
        );


    } catch (error) {

        console.error(
            "Error /api/chat:",
            error
        );


        quitarCargando();


        mensajeAsistente(
            "No pude procesar la consulta. Intenta nuevamente."
        );
    }
}


/* ============================================================
   CONSULTAR TRÁMITE
============================================================ */

async function consultarTramite(
    codigo,
    password
) {

    mostrarCargando();


    try {

        const response = await fetch(
            "/api/tramite",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    code: codigo,
                    password: password
                })
            }
        );


        const resultado =
            await response.json();


        console.log(
            "HTTP:",
            response.status
        );

        console.log(
            "Respuesta completa:",
            resultado
        );


        quitarCargando();


        /* ====================================================
           ERROR DEL SERVIDOR
        ==================================================== */

        if (
            !response.ok ||
            resultado.ok === false
        ) {

            mensajeAsistente(
                resultado.error ||
                "No pude consultar el trámite."
            );

            return;
        }


        /* ====================================================
           OBTENER LOS DATOS REALES DEL TRÁMITE
           
           Soporta estas dos formas:
           
           1.
           {
              ok: true,
              data: {
                  status: "Success",
                  message: "success",
                  data: {...}
              }
           }
           
           2.
           {
              ok: true,
              data: {
                  code: "...",
                  title: "..."
              }
           }
        ==================================================== */


        let tramite = resultado.data;


        if (
            tramite &&
            tramite.data &&
            typeof tramite.data === "object"
        ) {

            tramite = tramite.data;
        }


        console.log(
            "Datos del trámite:",
            tramite
        );


        /* ====================================================
           VALIDAR
        ==================================================== */

        if (
            !tramite ||
            typeof tramite !== "object"
        ) {

            mensajeAsistente(
                "La consulta fue recibida, pero no se encontraron datos del trámite."
            );

            return;
        }


        /* ====================================================
           MOSTRAR RESULTADO
        ==================================================== */

        const resultadoHTML =
            formatearResultado(tramite);


        mensajeAsistente(
            "<strong>Encontré tu trámite.</strong><br><br>" +
            resultadoHTML
        );


        /* ====================================================
           LIMPIAR ESTADO
        ==================================================== */

        codigoTramite = "";

        esperandoCodigo = false;

        esperandoPassword = false;


        el("entradaChat").placeholder =
            "Escribe otra consulta...";



    } catch (error) {

        console.error(
            "Error real consultando trámite:",
            error
        );


        quitarCargando();


        mensajeAsistente(
            "Ocurrió un problema al consultar el trámite. Intenta nuevamente."
        );
    }
}


/* ============================================================
   FORMATEAR TRÁMITE
============================================================ */

function formatearResultado(data) {

    if (
        data === null ||
        data === undefined
    ) {

        return (
            "No encontré información del trámite."
        );
    }


    /*
       IMPORTANTE:

       Aquí utilizamos los nombres EXACTOS
       que devuelve tu API.
    */


    const codigo =
        data.code ||
        "Sin código";


    const titulo =
        data.title ||
        data.detail ||
        "Sin título";


    const estado =
        data.status_txt ||
        traducirEstado(data.status) ||
        "Sin estado";


    const ubicacion =
        data.current_location ||
        "Sin ubicación asignada";


    const unidad =
        data.current_unit_name ||
        "";


    const actividad =
        data.current_activity_name ||
        "";


    const tiempo =
        data.time_proccessing ||
        "No disponible";


    const inicio =
        data.started_at ||
        "No disponible";


    let html = "";


    /* ========================================================
       CÓDIGO
    ======================================================== */

    html += `
        <div class="dato-tramite">
            <strong>Trámite</strong>
            <span>${escapeHtml(codigo)}</span>
        </div>
    `;


    /* ========================================================
       TÍTULO
    ======================================================== */

    if (titulo) {

        html += `
            <div class="dato-tramite">
                <strong>Asunto</strong>
                <span>${escapeHtml(titulo)}</span>
            </div>
        `;
    }


    /* ========================================================
       ESTADO
    ======================================================== */

    html += `
        <div class="dato-tramite">
            <strong>Estado</strong>
            <span>${escapeHtml(estado)}</span>
        </div>
    `;


    /* ========================================================
       UBICACIÓN
    ======================================================== */

    html += `
        <div class="dato-tramite">
            <strong>Ubicación</strong>
            <span>${escapeHtml(ubicacion)}</span>
        </div>
    `;


    /* ========================================================
       UNIDAD
    ======================================================== */

    if (unidad) {

        html += `
            <div class="dato-tramite">
                <strong>Unidad</strong>
                <span>${escapeHtml(unidad)}</span>
            </div>
        `;
    }


    /* ========================================================
       ACTIVIDAD
    ======================================================== */

    if (actividad) {

        html += `
            <div class="dato-tramite">
                <strong>Actividad</strong>
                <span>${escapeHtml(actividad)}</span>
            </div>
        `;
    }


    /* ========================================================
       TIEMPO
    ======================================================== */

    html += `
        <div class="dato-tramite">
            <strong>Tiempo de proceso</strong>
            <span>${escapeHtml(tiempo)}</span>
        </div>
    `;


    /* ========================================================
       FECHA DE INICIO
    ======================================================== */

    html += `
        <div class="dato-tramite">
            <strong>Inicio</strong>
            <span>${escapeHtml(inicio)}</span>
        </div>
    `;


    /* ========================================================
       RESUMEN HUMANO
    ======================================================== */

    html += `
        <div style="margin-top:12px;">
            Puedes consultar nuevamente cuando quieras para verificar si el estado cambió.
        </div>
    `;


    return html;
}


/* ============================================================
   TRADUCIR ESTADO
============================================================ */

function traducirEstado(estado) {

    if (!estado) {
        return "";
    }


    const estados = {

        NEW: "Nuevo",

        PENDING: "Pendiente",

        RECEIVED: "Recibido",

        DERIVED: "Derivado",

        SOLVED: "Resuelto",

        REJECTED: "Rechazado",

        FINISHED: "Finalizado",

        PAUSED: "Pausado",

        CANCELLED: "Cancelado"
    };


    return (
        estados[estado] ||
        estado
    );
}


/* ============================================================
   FORMATEAR CLAVE
============================================================ */

function formatearClave(clave) {

    return String(clave)
        .replaceAll("_", " ")
        .replace(/\b\w/g, letra =>
            letra.toUpperCase()
        );
}


/* ============================================================
   ESCAPAR HTML
============================================================ */

function escapeHtml(valor) {

    return String(valor)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );
}


/* ============================================================
   MENSAJE USUARIO
============================================================ */

function mensajeUsuario(texto) {

    const chat =
        el("chatMensajes");


    const div =
        document.createElement("div");


    div.className =
        "mensaje usuario";


    div.textContent =
        texto;


    chat.appendChild(div);


    bajarChat();
}


/* ============================================================
   MENSAJE ASISTENTE
============================================================ */

function mensajeAsistente(texto, estado = "respondiendo", enlaceSenador = null) {

    const chat = el("chatMensajes");
    const fila = document.createElement("div");
    fila.className = "mensaje-fila asistente-fila";

    fila.appendChild(crearAvatarAsistente(estado));

    const div = document.createElement("div");
    div.className = "mensaje asistente";
    div.innerHTML = texto;

    if (enlaceSenador) {
        const enlace = document.createElement("a");
        enlace.className = "enlace-mas-informacion";
        enlace.href = enlaceSenador;
        enlace.target = "_blank";
        enlace.rel = "noopener noreferrer";
        enlace.textContent = "Más información sobre este senador";
        enlace.setAttribute("aria-label", "Más información sobre este senador");

        div.appendChild(enlace);
    }

    fila.appendChild(div);
    chat.appendChild(fila);
    bajarChat();
}


/* ============================================================
   CARGANDO
============================================================ */

function mostrarCargando() {

    quitarCargando();
    actualizarEstadoAsistente("pensando", "Pensando…", "Estoy revisando la información.");

    const chat = el("chatMensajes");
    const fila = document.createElement("div");
    fila.id = "cargando";
    fila.className = "mensaje-fila asistente-fila cargando-fila";

    fila.appendChild(crearAvatarAsistente("pensando"));

    const div = document.createElement("div");
    div.className = "mensaje asistente escribiendo";
    div.innerHTML = `
        <span>Estoy consultando</span>
        <span class="puntos" aria-hidden="true">
            <i></i><i></i><i></i>
        </span>
    `;

    fila.appendChild(div);
    chat.appendChild(fila);
    bajarChat();
}


function quitarCargando() {
    clearTimeout(estadoTimer);
    estadoTimer = null;
    const elemento = el("cargando");
    if (elemento) elemento.remove();
    ocultarEstadoAsistente();
}


/* ============================================================
   SCROLL
============================================================ */

function bajarChat() {

    const chat =
        el("chatMensajes");


    chat.scrollTop =
        chat.scrollHeight;
}


/* ============================================================
   VOZ
============================================================ */

function activarVoz() {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    if (!SpeechRecognition) {

        mensajeAsistente(
            "Tu navegador no permite reconocimiento de voz. Puedes escribir la consulta."
        );

        return;
    }


    const reconocimiento =
        new SpeechRecognition();


    reconocimiento.lang =
        "es-BO";


    reconocimiento.interimResults =
        false;


    reconocimiento.maxAlternatives =
        1;


    const boton =
        el("btnVoz");


    boton.classList.add(
        "escuchando"
    );


    boton.textContent =
        "⏺️";


    reconocimiento.onresult =
        event => {

            el("entradaChat").value =
                event.results[0][0].transcript;


            boton.classList.remove(
                "escuchando"
            );


            boton.textContent =
                "🎙️";


            enviarMensaje();
        };


    reconocimiento.onerror =
        event => {

            console.error(
                "Reconocimiento de voz:",
                event.error
            );


            boton.classList.remove(
                "escuchando"
            );


            boton.textContent =
                "🎙️";


            mensajeAsistente(
                "No pude reconocer la voz. Puedes intentarlo nuevamente o escribir tu consulta."
            );
        };


    reconocimiento.onend =
        () => {

            boton.classList.remove(
                "escuchando"
            );


            boton.textContent =
                "🎙️";
        };


    reconocimiento.start();
}


/* ============================================================
   ENTER
============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const input =
            el("entradaChat");


        if (input) {

            input.addEventListener(
                "keydown",
                event => {

                    if (
                        event.key === "Enter" &&
                        !event.shiftKey
                    ) {

                        event.preventDefault();

                        enviarMensaje();
                    }
                }
            );
        }
    }
);