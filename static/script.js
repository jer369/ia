let categoriaActual = null;
let esperandoCodigo = false;
let esperandoPassword = false;
let codigoTramite = "";

const nombresCategorias = {
    institucional: "Institucional",
    tramites: "Trámites y Servicios",
    legislacion: "Legislación",
    senadores: "Senadores",
    fiscalizacion: "Fiscalización",
    gestion: "Gestión",
    comunicacion: "Comunicación",
    facultades_legislativas: "Facultades Legislativas"
};

function el(id) {
    return document.getElementById(id);
}

function abrirChat() {
    const chatbot = el("chatbot");
    chatbot.classList.add("activo");

    if (el("chatMensajes").children.length === 0) {
        mensajeAsistente(
            "Hola 👋<br><br>" +
            "Soy el <strong>Asistente Institucional del Senado</strong>.<br><br>" +
            "Puedes preguntarme directamente lo que necesites: trámites, leyes, " +
            "senadores, fiscalización, gestión, información institucional y más.<br><br>" +
            "No necesitas escoger una categoría. <strong>Escribe tu pregunta y conversamos.</strong>"
        );
        mostrarOpcionesPrincipales();
    }

    el("entradaChat").focus();
}

function cerrarChat() {
    el("chatbot").classList.remove("activo");
}

function abrirChatConCategoria(categoria) {
    abrirChat();
    seleccionarCategoria(categoria);
}

function mostrarOpcionesPrincipales() {
    const opciones = el("opcionesChat");
    opciones.innerHTML = "";

    [
        ["🏛️ Institucional", "institucional"],
        ["📄 Trámites y Servicios", "tramites"],
        ["⚖️ Legislación", "legislacion"],
        ["👥 Senadores", "senadores"],
        ["🔎 Fiscalización", "fiscalizacion"],
        ["🏢 Gestión", "gestion"],
        ["📢 Comunicación", "comunicacion"],
        ["📚 Facultades Legislativas", "facultades_legislativas"]
    ].forEach(([texto, categoria]) => {
        const boton = document.createElement("button");
        boton.textContent = texto;
        boton.onclick = () => seleccionarCategoria(categoria);
        opciones.appendChild(boton);
    });
}

function seleccionarCategoria(categoria) {
    categoriaActual = categoria;
    mensajeUsuario(nombresCategorias[categoria]);

    if (categoria === "tramites") {
        iniciarConsultaTramite();
        return;
    }

    mostrarOpcionesCategoria(categoria);
    mensajeAsistente(
        `Claro. Puedes preguntarme directamente sobre <strong>${nombresCategorias[categoria]}</strong>.`
    );
}

function mostrarOpcionesCategoria(categoria) {
    const opciones = el("opcionesChat");
    opciones.innerHTML = "";

    const preguntas = {
        institucional: [
            ["📜 Mandato constitucional", "¿Cuál es el mandato constitucional del Senado?"],
            ["🏛️ Funciones del Senado", "¿Cuáles son las funciones del Senado?"],
            ["📚 Antecedentes históricos", "¿Cuáles son los antecedentes históricos del Senado?"]
        ],
        legislacion: [
            ["📄 Proyectos en tratamiento", "¿Cuántos proyectos de ley están en tratamiento?"],
            ["✅ Proyectos aprobados", "¿Cuántos proyectos de ley fueron aprobados?"],
            ["⚖️ Leyes sancionadas", "¿Cuántas leyes fueron sancionadas?"],
            ["📜 Leyes promulgadas", "¿Cuántas leyes fueron promulgadas?"],
            ["❌ Proyectos rechazados", "¿Cuántos proyectos de ley fueron rechazados?"]
        ],
        senadores: [
            ["👤 Senadores titulares", "¿Quiénes son los senadores titulares?"],
            ["👤 Senadores suplentes", "¿Quiénes son los senadores suplentes?"],
            ["🏛️ Comisiones", "¿Qué información hay sobre las comisiones?"]
        ],
        fiscalizacion: [
            ["📄 Informe escrito", "¿Qué son las peticiones de informe escrito?"],
            ["🎤 Informe oral", "¿Qué son las peticiones de informe oral?"]
        ],
        gestion: [
            ["📋 Resoluciones", "¿Qué son las resoluciones camarales?"],
            ["📜 Declaraciones", "¿Qué son las declaraciones camarales?"],
            ["📝 Minutas", "¿Qué son las minutas de comunicación?"]
        ],
        comunicacion: [
            ["📰 Noticias", "¿Cuáles son las noticias institucionales?"],
            ["📢 Comunicados", "¿Cuáles son los comunicados institucionales?"]
        ],
        facultades_legislativas: [
            ["⚖️ Facultades", "¿Cuáles son las facultades legislativas del Senado?"],
            ["📄 Proceso legislativo", "¿Cómo es el proceso legislativo?"]
        ]
    };

    (preguntas[categoria] || []).forEach(([texto, pregunta]) => agregarOpcion(texto, pregunta));

    const volver = document.createElement("button");
    volver.textContent = "↩️ Ver todas las opciones";
    volver.onclick = () => {
        categoriaActual = null;
        mostrarOpcionesPrincipales();
    };
    opciones.appendChild(volver);
}

function agregarOpcion(texto, pregunta) {
    const boton = document.createElement("button");
    boton.textContent = texto;
    boton.onclick = () => {
        mensajeUsuario(texto);
        enviarPregunta(pregunta);
    };
    el("opcionesChat").appendChild(boton);
}

function iniciarConsultaTramite() {
    esperandoCodigo = true;
    esperandoPassword = false;
    codigoTramite = "";

    mensajeAsistente(
        "Claro. Vamos a consultar tu trámite aquí mismo.<br><br>" +
        "1️⃣ Escríbeme el <strong>código del trámite</strong>.<br>" +
        "2️⃣ Después te pediré la contraseña.<br><br>" +
        "También puedes escribir <strong>cancelar</strong> para salir de la consulta."
    );

    el("opcionesChat").innerHTML = "";
    el("entradaChat").placeholder = "Escribe el código del trámite...";
    el("entradaChat").focus();
}

function procesarMensaje(mensaje) {
    const normalizado = mensaje.toLowerCase().trim();

    if (normalizado === "cancelar" || normalizado === "cancelar consulta") {
        esperandoCodigo = false;
        esperandoPassword = false;
        codigoTramite = "";
        el("entradaChat").placeholder = "Escribe tu consulta...";
        mensajeAsistente("De acuerdo. Cancelé la consulta del trámite. ¿Qué deseas consultar ahora?");
        mostrarOpcionesPrincipales();
        return;
    }

    if (esperandoCodigo) {
        codigoTramite = mensaje;
        esperandoCodigo = false;
        esperandoPassword = true;

        mensajeAsistente(
            "Perfecto 👍. Ahora escribe la <strong>contraseña del trámite</strong>."
        );
        el("entradaChat").placeholder = "Escribe la contraseña...";
        return;
    }

    if (esperandoPassword) {
        esperandoPassword = false;
        el("entradaChat").placeholder = "Escribe otra consulta...";
        consultarTramite(codigoTramite, mensaje);
        return;
    }

    // Si el usuario menciona un trámite sin haber entrado al flujo,
    // el mismo chat lo guía sin mandarlo al menú.
    if (/\btr[aá]mite(s)?\b/.test(normalizado) &&
        /(consult|segu|estado|c[oó]digo)/.test(normalizado)) {
        iniciarConsultaTramite();
        return;
    }

    enviarPregunta(mensaje);
}

function enviarMensaje() {
    const input = el("entradaChat");
    const mensaje = input.value.trim();
    if (!mensaje) return;

    input.value = "";
    mensajeUsuario(mensaje);
    procesarMensaje(mensaje);
}

async function enviarPregunta(pregunta) {
    mostrarCargando();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ pregunta })
        });

        const data = await response.json();

        quitarCargando();

        if (!response.ok || data.error) {
            mensajeAsistente(
                "Tuve un problema al procesar la consulta. " +
                (data.error || "Intenta nuevamente.")
            );
            return;
        }

        mensajeAsistente(
            data.respuesta || "No encontré una respuesta para esa consulta."
        );

        if (data.categoria && nombresCategorias[data.categoria]) {
            categoriaActual = data.categoria;
        }
    } catch (error) {
        console.error("Error /api/chat:", error);
        quitarCargando();
        mensajeAsistente(
            "No pude comunicarme con el asistente en este momento. " +
            "Verifica que el servidor y Ollama estén funcionando e inténtalo nuevamente."
        );
    }
}

async function consultarTramite(codigo, password) {
    mostrarCargando();

    try {
        const response = await fetch("/api/tramite", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({code: codigo, password})
        });

        const data = await response.json();
        quitarCargando();

        if (!response.ok || !data.ok) {
            mensajeAsistente(
                "No pude completar la consulta del trámite.<br><br>" +
                "Motivo: " +
                (data.error || "La información no está disponible actualmente.") +
                "<br><br>Puedes volver a intentarlo escribiendo <strong>consultar trámite</strong>."
            );
            return;
        }

        mensajeAsistente(
            "<strong>Consulta del trámite realizada correctamente.</strong><br><br>" +
            formatearResultado(data.data)
        );

        codigoTramite = "";
        esperandoCodigo = false;
        esperandoPassword = false;
        el("entradaChat").placeholder = "Escribe otra consulta...";
        mostrarOpcionesPrincipales();
    } catch (error) {
        console.error("Error /api/tramite:", error);
        quitarCargando();
        mensajeAsistente(
            "No se pudo conectar con el sistema de trámites. " +
            "Puedes intentar nuevamente en unos momentos."
        );
    }
}

function formatearResultado(data) {
    if (data === null || data === undefined) return "Sin datos disponibles.";
    if (typeof data === "string") return escapeHtml(data);

    if (Array.isArray(data)) {
        return data.map(item => `<div class="dato-tramite">${escapeHtml(String(item))}</div>`).join("");
    }

    let html = "";
    Object.entries(data).forEach(([clave, valor]) => {
        let valorHtml;

        if (valor && typeof valor === "object") {
            valorHtml = `<pre>${escapeHtml(JSON.stringify(valor, null, 2))}</pre>`;
        } else {
            valorHtml = escapeHtml(String(valor ?? "-"));
        }

        html += `
            <div class="dato-tramite">
                <strong>${escapeHtml(formatearClave(clave))}</strong>
                <span>${valorHtml}</span>
            </div>
        `;
    });

    return html || "La consulta no devolvió datos.";
}

function formatearClave(clave) {
    return String(clave)
        .replaceAll("_", " ")
        .replace(/\b\w/g, letra => letra.toUpperCase());
}

function escapeHtml(valor) {
    return String(valor)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function mensajeUsuario(texto) {
    const chat = el("chatMensajes");
    const div = document.createElement("div");
    div.className = "mensaje usuario";
    div.textContent = texto;
    chat.appendChild(div);
    bajarChat();
}

function mensajeAsistente(texto) {
    const chat = el("chatMensajes");
    const div = document.createElement("div");
    div.className = "mensaje asistente";
    div.innerHTML = texto;
    chat.appendChild(div);
    bajarChat();
}

function mostrarCargando() {
    quitarCargando();

    const chat = el("chatMensajes");
    const div = document.createElement("div");
    div.id = "cargando";
    div.className = "mensaje asistente escribiendo";
    div.innerHTML = `
        <span>El asistente está pensando</span>
        <span class="puntos"><i></i><i></i><i></i></span>
    `;
    chat.appendChild(div);
    bajarChat();
}

function quitarCargando() {
    const elemento = el("cargando");
    if (elemento) elemento.remove();
}

function bajarChat() {
    const chat = el("chatMensajes");
    chat.scrollTop = chat.scrollHeight;
}

function activarVoz() {
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        mensajeAsistente(
            "Tu navegador no permite reconocimiento de voz. Puedes usar Firefox/Chrome con un navegador compatible o escribir la consulta."
        );
        return;
    }

    const reconocimiento = new SpeechRecognition();
    reconocimiento.lang = "es-BO";
    reconocimiento.interimResults = false;
    reconocimiento.maxAlternatives = 1;

    const boton = el("btnVoz");
    boton.classList.add("escuchando");
    boton.textContent = "⏺️";

    reconocimiento.onresult = event => {
        el("entradaChat").value = event.results[0][0].transcript;
        boton.classList.remove("escuchando");
        boton.textContent = "🎙️";
        enviarMensaje();
    };

    reconocimiento.onerror = event => {
        console.error("Reconocimiento de voz:", event.error);
        boton.classList.remove("escuchando");
        boton.textContent = "🎙️";
        mensajeAsistente("No pude reconocer la voz. Puedes intentarlo nuevamente o escribir tu consulta.");
    };

    reconocimiento.onend = () => {
        boton.classList.remove("escuchando");
        boton.textContent = "🎙️";
    };

    reconocimiento.start();
}

document.addEventListener("DOMContentLoaded", () => {
    const input = el("entradaChat");
    if (input) {
        input.addEventListener("keydown", event => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                enviarMensaje();
            }
        });
    }
});
