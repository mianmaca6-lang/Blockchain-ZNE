document.addEventListener('DOMContentLoaded', () => {
    // --- SISTEMA DE TELEMETRÍA Y ACCESO ---
    const modalLogin = document.getElementById('modal-login');
    const formLogin = document.getElementById('form-login');
    const loginError = document.getElementById('login-error');
    
    // Función central para enviar telemetría
    function enviarTelemetria(accion, detalle = "") {
        const token = localStorage.getItem('zine_tester_token');
        if (!token) return;
        fetch('/zine/telemetria', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token, accion, detalle })
        }).catch(err => console.error("Error de telemetría", err));
    }

    // Verificar si ya está logueado
    if (localStorage.getItem('zine_tester_token')) {
        modalLogin.classList.add('hidden');
    }

    formLogin.addEventListener('submit', async (e) => {
        e.preventDefault();
        const tokenVal = document.getElementById('input-token').value.toLowerCase().trim();
        
        try {
            const resp = await fetch('/zine/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: tokenVal })
            });
            const data = await resp.json();
            
            if (data.status === 'success') {
                localStorage.setItem('zine_tester_token', tokenVal);
                modalLogin.style.opacity = '0';
                setTimeout(() => modalLogin.classList.add('hidden'), 500);
            } else {
                loginError.classList.remove('hidden');
            }
        } catch (err) {
            loginError.textContent = "Error de conexión con la Colmena.";
            loginError.classList.remove('hidden');
        }
    });

    // Inyectar telemetría a los botones existentes
    document.getElementById('btn-abrir-modal')?.addEventListener('click', () => enviarTelemetria('clic_boton', 'Abrir registro de gasto'));
    document.getElementById('btn-evolucionar')?.addEventListener('click', () => enviarTelemetria('clic_boton', 'Evolucionar Colmena'));
    const btnEvolucionar = document.getElementById('btn-evolucionar');
    const imgColmena = document.getElementById('img-colmena');
    const hudNivel = document.getElementById('hud-nivel');
    const hudDesc = document.getElementById('hud-desc');
    const contenedorAbejas = document.getElementById('contenedor-abejas');

    // Elementos del Modal de Registro Manual
    const modalRegistro = document.getElementById('modal-registro');
    const btnAbrirModal = document.getElementById('btn-abrir-modal');
    const btnCerrarModal = document.getElementById('btn-cerrar-modal');
    const formGasto = document.getElementById('form-gasto');

    // Leer el nivel inicial inyectado desde FastAPI (colmena.db)
    const bodyTag = document.body;
    let nivelActual = parseInt(bodyTag.getAttribute('data-nivel-inicial')) || 1;

    const URL_ABEJA = "/static/img/colmena/Abeja%20caricaturesca%20volando%20hacia%20la%20derecha.png";
    
    const etapasEvolucion = {
        1: { 
            src: "/static/img/colmena/Colmena%20dorada%20colgando%20de%20una%20rama.png", 
            titulo: "Nivel 1", desc: "Silvestre",
            piqueraX: 0.65, piqueraY: 0.68 
        },
        2: { 
            src: "/static/img/colmena/Ilustraci%C3%B3n%20de%20colmena%20de%20madera%20estilizada.png", 
            titulo: "Nivel 2", desc: "Langstroth Simple",
            piqueraX: 0.50, piqueraY: 0.85 
        },
        3: { 
            src: "/static/img/colmena/Colmena%20de%20Madera%20Dorada.png", 
            titulo: "Nivel 3", desc: "Langstroth Doble",
            piqueraX: 0.50, piqueraY: 0.88 
        }
    };

    // Aplicar el estado inicial real al cargar la vista
    function aplicarNivel(nivel) {
        const dataNivel = etapasEvolucion[nivel];
        imgColmena.src = dataNivel.src;
        hudNivel.textContent = dataNivel.titulo;
        hudDesc.textContent = dataNivel.desc;
    }

    aplicarNivel(nivelActual);

    // --- CONTROL DEL MODAL DE REGISTRO MANUAL ---
    if (btnAbrirModal && modalRegistro) {
        btnAbrirModal.addEventListener('click', () => {
            modalRegistro.classList.remove('hidden');
        });
    }

    if (btnCerrarModal && modalRegistro) {
        btnCerrarModal.addEventListener('click', () => {
            modalRegistro.classList.add('hidden');
        });
    }

    if (modalRegistro) {
        modalRegistro.addEventListener('click', (e) => {
            if (e.target === modalRegistro) {
                modalRegistro.classList.add('hidden');
            }
        });
    }

    // Envío del formulario conectado al backend
    if (formGasto) {
        formGasto.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData();
            formData.append('concepto', document.getElementById('input-concepto').value);
            formData.append('monto', document.getElementById('input-monto').value);
            
            const inputArchivo = document.getElementById('input-archivo');
            if (inputArchivo && inputArchivo.files[0]) {
                formData.append('archivo', inputArchivo.files[0]);
            }

            try {
                const response = await fetch('/zine/registrar', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const resultado = await response.json();
                    alert(resultado.mensaje);
                    
                    formGasto.reset();
                    modalRegistro.classList.add('hidden');
                    
                    // Recarga la página para actualizar las métricas y la evolución de la colmena
                    window.location.reload();
                } else {
                    alert('Hubo un error al guardar el registro en la colmena.');
                }
            } catch (error) {
                console.error('Error de red:', error);
                alert('No se pudo conectar con el servidor.');
            }
        });
    }

    // --- SISTEMA DE ENJAMBRE EN OCHO (SENTIDO HORARIO) ---
    const MAX_ABEJAS = 10;
    let abejasActivas = 0;

    function obtenerEntradaColmena() {
        const rect = imgColmena.getBoundingClientRect();
        const config = etapasEvolucion[nivelActual];
        return {
            x: rect.left + (rect.width * config.piqueraX),
            y: rect.top + (rect.height * config.piqueraY)
        };
    }

    function spawnAbeja() {
        if (abejasActivas >= MAX_ABEJAS || imgColmena.style.opacity === '0') return;

        const entrada = obtenerEntradaColmena();
        const abeja = document.createElement('img');
        
        abeja.src = URL_ABEJA;
        abeja.className = 'abeja-instancia';
        
        const size = Math.random() * 15 + 20;
        abeja.style.width = `${size}px`;

        abeja.style.left = `${entrada.x}px`;
        abeja.style.top = `${entrada.y}px`;
        abeja.style.transform = 'translate(-50%, -50%) scale(0)';
        abeja.style.opacity = '0';

        contenedorAbejas.appendChild(abeja);
        abejasActivas++;

        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                const offsetX = (Math.random() - 0.5) * 150 + 100;
                const offsetY = (Math.random() - 0.5) * 150 - 50;
                
                const vueloX = entrada.x + offsetX;
                const vueloY = entrada.y + offsetY;

                abeja.style.transition = 'left 1.5s ease-out, top 1.5s ease-out, transform 1.5s ease-out, opacity 0.5s';
                abeja.style.left = `${vueloX}px`;
                abeja.style.top = `${vueloY}px`;
                abeja.style.transform = 'translate(-50%, -50%) scale(1)';
                abeja.style.opacity = '1';

                setTimeout(() => {
                    let tiempo = 0;
                    const radioX = 80 + Math.random() * 40;
                    const radioY = 40 + Math.random() * 20;
                    const centroX = vueloX;
                    const centroY = vueloY;

                    const intervaloOcho = setInterval(() => {
                        tiempo += 0.04;
                        const x = centroX + radioX * Math.sin(tiempo);
                        const y = centroY + (radioY * Math.sin(2 * tiempo)) / 2;
                        const derivadaX = Math.cos(tiempo);
                        const escalaX = derivadaX >= 0 ? 1 : -1;

                        abeja.style.transition = 'left 0.05s linear, top 0.05s linear, transform 0.1s';
                        abeja.style.left = `${x}px`;
                        abeja.style.top = `${y}px`;
                        abeja.style.transform = `translate(-50%, -50%) scaleX(${escalaX})`;
                    }, 50);

                    const tiempoPolinizacion = Math.random() * 4000 + 3000;
                    setTimeout(() => {
                        clearInterval(intervaloOcho);
                        const entradaActual = obtenerEntradaColmena();
                        
                        abeja.style.transition = 'left 1.5s ease-in, top 1.5s ease-in, transform 1.5s ease-in, opacity 1s';
                        abeja.style.left = `${entradaActual.x}px`;
                        abeja.style.top = `${entradaActual.y}px`;
                        abeja.style.transform = 'translate(-50%, -50%) scale(0.1)';
                        abeja.style.opacity = '0';

                        setTimeout(() => {
                            abeja.remove();
                            abejasActivas--;
                        }, 1500);
                    }, tiempoPolinizacion);
                }, 1500);
            });
        });
    }

    setInterval(() => {
        if (Math.random() > 0.3) spawnAbeja();
    }, 800);

    // Botón de prueba manual (rota niveles cíclicamente)
    if (btnEvolucionar) {
        btnEvolucionar.addEventListener('click', () => {
            nivelActual = nivelActual >= 3 ? 1 : nivelActual + 1;
            
            imgColmena.style.opacity = '0';
            imgColmena.style.transform = 'translateY(20px) scale(0.9)';

            setTimeout(() => {
                aplicarNivel(nivelActual);
                imgColmena.style.opacity = '1';
                imgColmena.style.transform = 'translateY(0) scale(1)';
            }, 300);
        });
    }
 
    ['mousedown', 'touchstart'].forEach(evt => {
        if (imgColmena) imgColmena.addEventListener(evt, () => imgColmena.classList.add('click-efecto'));
    });
    ['mouseup', 'mouseleave', 'touchend'].forEach(evt => {
        if (imgColmena) imgColmena.addEventListener(evt, () => imgColmena.classList.remove('click-efecto'));
    });
    // --- SISTEMA DE VISUALIZACIÓN (CHART.JS) ---
    const modalGraficas = document.getElementById('modal-graficas');
    const btnAbrirGraficas = document.getElementById('btn-abrir-graficas');
    const btnCerrarGraficas = document.getElementById('btn-cerrar-graficas');
    let chartInstancia = null;

    if (btnAbrirGraficas && modalGraficas) {
        btnAbrirGraficas.addEventListener('click', async () => {
            modalGraficas.classList.remove('hidden');
            enviarTelemetria('clic_boton', 'Abrir panel de balance financiero');

            try {
                const response = await fetch('/zine/estadisticas');
                const data = await response.json();

                const ctx = document.getElementById('chart-finanzas').getContext('2d');
                
                // Destruir gráfica anterior si el usuario abre y cierra el modal repetidas veces
                if (chartInstancia) {
                    chartInstancia.destroy();
                }

                chartInstancia = new Chart(ctx, {
                    type: 'bar', // Cambiable a 'doughnut' o 'pie'
                    data: {
                        labels: data.etiquetas,
                        datasets: [{
                            label: 'Monto ($)',
                            data: data.valores,
                            backgroundColor: data.colores,
                            borderColor: data.bordes,
                            borderWidth: 1,
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        color: '#d6d3d1', // Texto stone-300
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: { color: 'rgba(255,255,255,0.05)' },
                                ticks: { color: '#a8a29e' }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { color: '#a8a29e' }
                            }
                        }
                    }
                });
            } catch (error) {
                console.error("Error cargando gráfica:", error);
            }
        });
    }

    if (btnCerrarGraficas) {
        btnCerrarGraficas.addEventListener('click', () => modalGraficas.classList.add('hidden'));
    }

    // Cerrar modal al hacer clic fuera
    if (modalGraficas) {
        modalGraficas.addEventListener('click', (e) => {
            if (e.target === modalGraficas) modalGraficas.classList.add('hidden');
        });
    }
});