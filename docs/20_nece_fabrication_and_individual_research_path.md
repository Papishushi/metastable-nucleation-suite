# 20. Fabricación de un NECE y ruta para un investigador individual

## 20.1 Respuesta directa

Un investigador individual con acceso a una sala blanca modesta **puede construir un demostrador NECE mesoscópico**.
No puede fabricar por sí solo, de forma realista, una matriz industrial tridimensional sub-10-nm con materiales,
selectores y metrología de frontera.

El primer objetivo no es fabricar una memoria masiva. Es demostrar que dos configuraciones de nucleación o
dominios pueden:

\[
R_A\approx R_B,
\qquad
\mathcal S_A\neq\mathcal S_B,
\qquad
F_A\neq F_B.
\]

`R` es la respuesta PCM agregada, `S` la microconfiguración resuelta y `F` una función física verificada.

## 20.2 La fotolitografía no tiene que escribir los núcleos

La fotolitografía convencional puede fabricar:

- marcas de alineamiento;
- ventanas y mesas de muestra;
- electrodos;
- microcalentadores;
- guías, resonadores o aperturas de lectura;
- aislamiento y contactos.

La configuración NECE se produciría **después** mediante una receta localizada de nucleación y crecimiento:

- escritura óptica directa;
- pulsos en microcalentadores;
- sonda térmica o eléctrica escaneada;
- gradientes térmicos y semillas controladas;
- en fases posteriores, haz de electrones o iones como herramienta de investigación.

Por tanto, la nucleación funciona como una litografía material interna. La litografía convencional fabrica el
andamiaje de acceso; no necesita definir cada dominio informativo.

## 20.3 Escala correcta para el primer demostrador

La primera muestra debe trabajar con dominios resolubles, aproximadamente entre cientos de nanómetros y varios
micrómetros. Esta escala permite:

- escritura con óptica enfocada o calentadores micrométricos;
- lectura mediante microscopía óptica, Raman o AFM;
- ciclos rápidos de diseño, escritura y análisis;
- evitar que el éxito dependa de TEM, FIB o litografía sub-10-nm.

Una demostración bidimensional o cuasi-tridimensional es suficiente para validar la semántica NECE. La estructura
3D debe plantearse después de demostrar información y función configuracionales en una sola película.

## 20.4 Materiales de partida

### Ruta recomendada: película encargada

La opción más reproducible es comprar o encargar un sustrato con una película calcogenura depositada y encapsulada.
La solicitud al proveedor o instalación debe especificar:

- composición nominal y tolerancia;
- método de deposición;
- espesor y uniformidad;
- rugosidad;
- estado inicial amorfo o cristalino;
- sustrato;
- capa de encapsulación;
- caracterización entregada: composición, espesor y, cuando sea posible, Raman, XRD o elipsometría.

Esto evita que el proyecto dependa inicialmente de sintetizar un vidrio de alta pureza o de instalar una línea de
sputtering compatible con antimonio, selenio o telurio.

### Familias candidatas

- **GST, por ejemplo Ge2Sb2Te5:** material de referencia para conmutación térmica y comparación con PCM eléctrico;
- **Sb2Se3:** candidato óptico de pérdida baja y contraste de índice no volátil;
- **Sb2S3:** candidato para prototipado fotónico visible y cercano al infrarrojo;
- otras composiciones solo deben incorporarse con datos de transición, estabilidad y seguridad suficientes.

La elección no debe basarse en la mayor cifra publicada. Debe maximizar la probabilidad de escribir, leer y repetir
configuraciones diferenciadas con el instrumental disponible.

## 20.5 Proceso mínimo sin nanolitografía avanzada

### Opción A: demostrador óptico sobre película continua

1. adquirir un sustrato de sílice, vidrio o silicio oxidado con película PCM;
2. añadir encapsulación si no viene incluida;
3. crear marcas macroscópicas o micrométricas de coordenadas;
4. preparar un estado inicial uniforme;
5. escribir patrones A y B mediante calentamiento óptico localizado;
6. ajustar las recetas para igualar aproximadamente la transmisión o reflectancia agregada;
7. leer la morfología mediante microscopía, Raman o imagen de fase;
8. medir una función: difracción, filtrado, fase, respuesta espectral o acoplamiento;
9. repetir ciclos ciegos y calcular la matriz de confusión e `I(W;R)`.

Esta opción puede demostrar el principio NECE sin fabricar transistores, selectores ni una matriz de memoria.

### Opción B: demostrador electro-óptico con sala blanca modesta

1. fotolitografía de contacto para marcas, pads y microcalentadores;
2. metalización y lift-off;
3. deposición o transferencia de la película PCM;
4. encapsulación dieléctrica;
5. apertura de contactos si es necesaria;
6. calibración temperatura-pulso-respuesta;
7. escritura combinando calentadores y láser;
8. lectura eléctrica agregada y lectura óptica configuracional.

Aquí la comparación es especialmente fuerte: dos configuraciones pueden presentar resistencia semejante y, aun
así, producir respuestas ópticas o de acoplamiento diferentes.

### Opción C: fase avanzada en instalación compartida

Solo después de validar A o B:

- EBL para calentadores, resonadores o ventanas submicrométricas;
- FIB para secciones o modificación localizada;
- SEM/TEM para confirmar dominios por debajo de la resolución óptica;
- deposición multicapa para estudiar direccionamiento cuasi-3D;
- integración con guías de silicio o microcavidades.

Estas técnicas pueden contratarse como servicio o realizarse mediante colaboración. No deben ser una condición de
entrada al programa.

## 20.6 Cómo generar dos configuraciones isoagregadas

El experimento no debe limitarse a escribir más o menos material cristalino. Debe producir morfologías diferentes
con una respuesta media semejante. Ejemplos de pares de receta:

- muchos dominios pequeños frente a pocos dominios grandes;
- anillo frente a disco con área transformada equivalente;
- dominios separados frente a una cadena conectada;
- distribución central frente a periférica;
- misma fracción transformada con diferente orientación o historia térmica.

La igualdad agregada se define con una tolerancia preregistrada, no mediante selección posterior. La variable
agregada puede ser resistencia, transmisión integrada, reflectancia o fracción cristalina inferida.

La variable funcional debe medirse por separado. Puede ser:

- patrón de difracción;
- fase óptica;
- espectro;
- acoplamiento modal;
- anisotropía;
- respuesta a una segunda señal de prueba.

## 20.7 Instrumentación por nivel

### Instrumentación que puede poseer u operar el investigador

- etapa XY y control de enfoque;
- microscopio óptico con cámara;
- fuente óptica de lectura de baja perturbación;
- generador de pulsos y adquisición eléctrica;
- control de temperatura;
- software MNS para recetas, procedencia y análisis;
- recinto láser y enclavamientos adecuados.

### Instrumentación razonable de una sala blanca o instalación compartida

- sputtering, evaporación o ALD;
- fotolitografía, metalización y perfilometría;
- Raman, elipsometría, AFM y SEM;
- wire bonding y estaciones de puntas;
- medición espectral y óptica integrada.

### Instrumentación normalmente colaborativa

- TEM in situ;
- difracción y espectroscopía de alta resolución;
- EBL/FIB de frontera;
- crecimiento o síntesis de materiales no comerciales;
- integración multicapa nanométrica con selectores.

## 20.8 Qué puede hacer una sola persona

Una sola persona puede liderar y ejecutar:

- definición de la hipótesis y falsificación;
- diseño de patrones y recetas;
- automatización de escritura y lectura;
- control del experimento;
- modelo térmico y óptico inicial;
- análisis ciego, información mutua y procedencia;
- diseño de máscaras sencillas;
- preparación de solicitudes de deposición y caracterización;
- construcción de un banco óptico seguro a escala mesoscópica;
- publicación de datos positivos o negativos reproducibles.

No es necesario esperar a que un grupo descubra el repositorio espontáneamente. El camino práctico es convertir MNS
en un paquete que una instalación pueda cotizar o evaluar: dibujo de muestra, proceso, material, mediciones,
contrato de datos y criterio de éxito.

## 20.9 Cuándo hace falta un equipo científico

Un colaborador especialista es necesario o muy recomendable cuando se requiera:

- asegurar estequiometría, pureza y estructura de la película;
- interpretar mecanismos de nucleación y crecimiento;
- demostrar dominios por debajo de la resolución óptica;
- descartar oxidación, segregación o daño por ablación;
- operar TEM, FIB, EBL o deposición compleja;
- publicar afirmaciones de mecanismo microscópico;
- integrar múltiples capas o dispositivos fotónicos avanzados.

La colaboración no sustituye el trabajo del investigador principal. El repositorio, el protocolo, la automatización
y el análisis pueden estar completos antes de solicitar una muestra o una sesión de microscopía.

## 20.10 De película a estructura tridimensional

Una ruta 3D plausible es incremental:

1. una película con configuraciones planas;
2. varias películas PCM separadas por dieléctrico;
3. direccionamiento óptico selectivo por profundidad o absorción;
4. calentadores y electrodos por capa;
5. lectura tomográfica, espectral o modal;
6. compilación de una función entre capas.

La impresión directa de calcogenuros mediante procesos de dos fotones es una vía emergente para estructuras
tridimensionales libres, pero todavía debe tratarse como una técnica de investigación, no como el proceso base de
NECE.

## 20.11 Seguridad y contaminación

Los calcogenuros pueden contener elementos y compuestos que requieren controles de exposición y residuos. La
fabricación debe seguir las SDS y las reglas EHS de la instalación.

- no mecanizar, lijar ni pulverizar blancos o películas fuera de equipos aprobados;
- evitar cualquier generación de polvo;
- usar deposición, limpieza y residuos autorizados para la composición concreta;
- encapsular la película cuando sea compatible con la transición;
- no operar láseres de escritura sin recinto, gafas seleccionadas para la longitud de onda, enclavamientos y
  evaluación de reflexiones;
- tratar ablación, humos y delaminación como fallos del proceso, no como mecanismos de escritura aceptables.

## 20.12 Plan de ejecución recomendado

### Etapa 0: muestra comercial o encargada

Obtener varias películas testigo y verificar transición, contraste y repetibilidad global.

### Etapa 1: escritura óptica mesoscópica

Producir A y B isoagregados, leerlos ópticamente y medir retención.

### Etapa 2: función

Hacer que A y B produzcan patrones de difracción, espectros o acoplamientos diferentes.

### Etapa 3: microcalentadores

Añadir direccionamiento eléctrico y comparar escritura óptica frente a térmica.

### Etapa 4: resolución submicrométrica

Usar una instalación compartida solo cuando los resultados mesoscópicos justifiquen el coste.

### Etapa 5: capas múltiples

Explorar geometría cuasi-3D y medir cross-talk térmico y óptico.

## 20.13 Criterio práctico de éxito personal

El primer resultado publicable no necesita ser un chip. Puede ser una muestra y un dataset que demuestren:

- dos o más configuraciones escritas repetidamente;
- respuesta PCM agregada igualada;
- clasificación ciega de la configuración;
- retención medida;
- función física diferente;
- datos, recetas y análisis reproducibles en MNS.

Con ese resultado, el repositorio deja de ser solo una visión y se convierte en una plataforma experimental a la
que un grupo de materiales o fotónica puede incorporarse con una pregunta concreta.

## 20.14 Referencias técnicas de partida

- M. Delaney et al., *Non-volatile programmable silicon photonics using an ultralow loss Sb2Se3 phase change material*, 2021, arXiv:2101.03623.
- S. Abdollahramezani et al., *Electrically driven programmable phase-change meta-switch reaching 80% efficiency*, 2021, arXiv:2104.10381.
- C. C. Popescu et al., *Electrically reconfigurable phase-change transmissive metasurface*, 2023, arXiv:2312.10468.
- S. Zarei, *On-chip rewritable phase-change metasurface for programmable diffractive deep neural networks*, 2024, arXiv:2411.05723.
- A. Dey et al., *Two-Photon-Induced Direct 3D Printing of Freeform High-Index Phase-Change Sb2S3 Nanostructures*, 2026, arXiv:2605.01054.
