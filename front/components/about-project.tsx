"use client";

import { useState, useRef, useEffect } from "react";

const TABS = [
  { id: "intro", label: "El Proyecto" },
  { id: "tour", label: "Recorrido" },
  { id: "data", label: "Datos y Modelos" },
  { id: "context", label: "Limitaciones" },
];

export function AboutProject() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("intro");
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Correct scroll position on tab change
    if (contentRef.current) {
      contentRef.current.scrollTo(0, 0);
    }
  }, [activeTab]);

  return (
    <>
      <button
        aria-expanded={isOpen}
        aria-haspopup="dialog"
        className="about-project-trigger"
        onClick={() => setIsOpen(true)}
        type="button"
      >
        Sobre el proyecto
      </button>

      {isOpen && (
        <div className="about-project-overlay">
          <div 
            aria-hidden="true" 
            className="about-project-backdrop" 
            onClick={() => setIsOpen(false)}
          />
          
          <div 
            aria-modal="true" 
            className="about-project-dialog"
            role="dialog"
          >
            <header className="about-project-header">
              <h2>Sobre Localízate</h2>
              <button 
                aria-label="Cerrar vista" 
                className="about-project-close explain-banner-close" 
                onClick={() => setIsOpen(false)}
                type="button"
              >
                ✕ Cerrar
              </button>
            </header>

            <nav className="about-project-tabs toggle-row">
              {TABS.map((tab) => (
                <button
                  key={tab.id}
                  data-active={activeTab === tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  type="button"
                >
                  {tab.label}
                </button>
              ))}
            </nav>

            <div className="about-project-content" ref={contentRef}>
              {activeTab === "intro" && (
                <div className="about-project-section">
                  <h3>¿Qué es Localízate?</h3>
                  <p>
                    Localízate es una herramienta analítica y de visualización creada como parte de un proyecto de innovación de datos abiertos para el <strong>Ayuntamiento de Madrid</strong>.
                  </p>
                  <h3>¿Para qué sirve y qué valor aporta?</h3>
                  <p>
                    Sirve para mitigar la incertidumbre al abrir un nuevo negocio en la ciudad. El objetivo es proporcionar información predictiva y descriptiva sobre diferentes zonas de Madrid para ayudar a emprendedores a entender sus probabilidades de éxito basándose en la supervivencia demostrada por los locales circundantes históricamente.
                  </p>
                  <h3>¿Qué información puedo consultar?</h3>
                  <p>
                    Datos de supervivencia histórica de los locales (cuánto aguantan abiertos), niveles de vulnerabilidad por zona, 
                    métricas socioeconómicas (renta, población), competencia activa, número de avisos ciudadanos (por limpieza u otras razones) 
                    y distancias a servicios esenciales como estaciones de Metro o equipamientos públicos.
                  </p>
                  <h3>Stack y despliegue del proyecto</h3>
                  <p>
                    El pipeline estadístico se basa en procesos en entorno asíncrono con Python. Posteriormente el frontend web orienta su arquitectura mediante el framework <strong>Next.js</strong> y componentes cartográficos MapLibre. Para lograr tiempos de latencia ínfimos, la web se exporta estáticamente. Todo el despliegue final está orquestado a través de flujos en <strong>GitHub Actions</strong>, y servido a través de ecosistemas resilientes: <strong>Cloudflare Pages</strong> para la red de entrega global estática, <strong>Cloudflare R2</strong> como datalake público estructurado mediante json estáticos pre-calculados, y <strong>Cloudflare Workers</strong> que aloja resoluciones dinámicas bajo demanda (como el geocoder por calle de la sección de oportunidades).
                  </p>
                </div>
              )}

              {activeTab === "tour" && (
                <div className="about-project-section">
                  <h3>Recorrido rápido</h3>
                  <div className="tour-grid">
                    <div className="tour-card stat-card">
                      <h4 className="label">1. Pestaña "Histórico"</h4>
                      <p>Muestra el comportamiento agregado a largo plazo. Puedes seleccionar un tipo de negocio (ej. Bar y cafetería) y explorar cómo le va a lo largo de toda la ciudad. Los colores y el mapa te ayudarán a detectar si un barrio es seguro o arriesgado para esa actividad.</p>
                    </div>
                    <div className="tour-card stat-card">
                      <h4 className="label">2. Escalas del mapa</h4>
                      <p>Para ver el pulso de la ciudad de forma agregada, puedes ver los datos por <strong>Distrito</strong> o por <strong>Barrio</strong>. Pero si necesitas hilar fino, puedes bajar al nivel de <strong>Hexágono (H3)</strong> y cambiar su tamaño (celdas que equivalen a un par de manzanas).</p>
                    </div>
                    <div className="tour-card stat-card">
                      <h4 className="label">3. Pestaña "Oportunidades"</h4>
                      <p>Si la vista de Histórico te ayuda a entender el mercado general, esta pestaña te ayuda a <strong>evaluar una ubicación en concreto</strong>. Ves locales vacíos (disponibles) por Madrid y puedes abrir una ficha que te recomienda qué negocio montar allí según algoritmos de supervivencia y dotaciones cercanas.</p>
                    </div>
                    <div className="tour-card stat-card">
                      <h4 className="label">4. Búsqueda de dirección</h4>
                      <p>Dentro de Oportunidades, no solo puedes ver los locales vacíos sugeridos, sino introducir la dirección de un lugar concreto en mente y obtener un informe comercial completo de la sección de características únicas de ese punto en la calle.</p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "data" && (
                <div className="about-project-section">
                  <h3>Fuentes de Datos</h3>
                  <p>
                    Toda la información ha sido modelada partiendo principalmente del catálogo de datos de <strong>datos.madrid.es</strong> y enriquecida con otras fuentes primarias. El repositorio base cruza múltiples universos estadísticos:
                  </p>
                  <ul>
                    <li>Censo de locales y sus actividades (histórico mensual desde 2015).</li>
                    <li>Padrón municipal (habitantes, rangos de edad, población extranjera).</li>
                    <li>Renta por hogar del distrito o la sección censal (fuente: INE).</li>
                    <li>Avisos ciudadanos en el barrio/distrito (ej: limpieza, vía pública).</li>
                    <li>Equipamientos públicos y privados de la ciudad (colegios, salud, deporte, zonas verdes).</li>
                    <li>Distancias calculadas a la red de Metro oficial de Madrid y su densidad.</li>
                    <li>Inspecciones de consumo e índices de vulnerabilidad (IGUALA).</li>
                  </ul>

                  <h3>Modelos Analíticos Utilizados</h3>
                  <p>
                    Este no es un mapa basado simplemente en medias o recuentos. Empleamos técnicas a la vanguardia del <strong>Machine Learning</strong>, profundizando en el área del <strong>Análisis de Supervivencia (Survival Analysis)</strong>. En particular, nuestro sistema se fundamenta en arquitecturas predictivas avanzadas como los <strong>Random Survival Forests (RSF)</strong> y la regresión de riesgos proporcionales de <strong>Cox</strong>. 
                  </p>
                  <p>
                    En lugar de limitarnos a clasificar si un negocio tendrá éxito o no de forma binaria, estos modelos aprenden de todo el histórico censal de la última década para predecir <em>cuánto tiempo es probable que sobreviva</em> un local en unas coordenadas específicas. El output más útil que obtenemos de estas inferencias es la <strong>métrica de riesgo</strong>, la cual materializamos de varias maneras a lo largo de toda la web en función de la finalidad buscada. Las principales señales que extrae nuestro algoritmo de machine learning incluyen la identidad del comercio, la saturación competitiva en su hexágono, y la atracción peatonal latente según infraestructuras.
                  </p>
                </div>
              )}

              {activeTab === "context" && (
                <div className="about-project-section">
                  <h3>Contexto y Limitaciones</h3>
                  <p>
                    Queremos ser muy transparentes sobre la fiabilidad de lo que mostramos. Existen desafíos y dificultades con las que tratamos de forma diaria:
                  </p>
                  <ul className="limitations-list">
                    <li><strong>Decalajes en el Censo:</strong> El dato municipal del censo de locales a veces sufre retrasos en reportar un cierre real (el epígrafe se queda "vivo" después de que echasen la persiana). Tratamos de usar técnicas de limpieza y alisamiento, pero el error geográfico basal existe.</li>
                    <li><strong>Falta de datos de Renta actualizados:</strong> El dato más detallado público de renta no es en tiempo real y el último consolidado es de 2023, por lo que aplicamos un acarreo asumiendo la renta disponible cercana, que imputamos cuando no hay registro para tu manzana.</li>
                    <li><strong>Categorización de "Locales sin datos":</strong> Una porción considerable de la muestra original viene sin epígrafe claro (casi un 30%). Se han modelado cuidadosamente omitiéndolos al buscar patrones comerciales específicos pero incluyéndolos en promedios generales para no deformar la densidad mostrada.</li>
                    <li><strong>Los hexágonos donde hay muy pocos locales (Soporte Débil):</strong> Cuando veas "Sin muestra" confía en esa honestidad. A nuestro modelo le exigimos un mínimo (por ejemplo al nivel Malla Grande no forzamos predicciones a ciegas con pocos registros).</li>
                    <li><strong>Disponibilidad de Anuncios:</strong> Para los locales que mostramos como anuncios reales en Oportunidades, solo extraemos los disponibles en portales como <em>locales.es</em>. No representan la totalidad de locales comerciales disponibles en Madrid. Por ello, si conoces de un local que no aparece, puedes seleccionar libremente su punto en el mapa o introducir su dirección para analizarlo.</li>
                    <li><strong>Límites del Servicio de Direcciones:</strong> La funcionalidad de búsqueda directa por dirección hace uso de un proveedor externo de geocodificación. Debido a esto, la búsqueda puede fallar ocasionalmente si se superan los límites de las solicitudes permitidas por ese servicio.</li>
                  </ul>
                  
                  <h3>Contexto Adicional Relevante</h3>
                  <p>
                    El trabajo algorítmico detrás se soporta con pipelines analíticos en Python (Pandas/Scikit-survival). El pipeline actual requiere cruzar espacialmente cada mes de los últimos diez años (una barbaridad computacional) para dar al frontend unos archivos ultra aligerados y estáticos (artifacts <code>.json</code>) con todo masticado, para que tu experiencia en esta interfaz sea en tiempo real, sin tiempos de carga de la base de datos principal.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
