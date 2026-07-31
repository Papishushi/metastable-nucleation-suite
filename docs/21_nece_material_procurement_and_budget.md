# 21. Aprovisionamiento de materiales y presupuesto para un demostrador NECE

## 21.1 Alcance

Este documento convierte la ruta de fabricación de `docs/20_nece_fabrication_and_individual_research_path.md`
en una lista de compras y servicios contratables para un primer demostrador NECE bidimensional o cuasi-bidimensional.

Las cantidades económicas son **rangos de planificación en euros de 2026**, no cotizaciones, tarifas públicas ni
compromisos de ningún proveedor. El precio real depende de la composición, el tamaño de muestra, la disponibilidad
del blanco, la contaminación permitida por la cámara, la caracterización y el desarrollo de receta.

El objetivo inicial no es fabricar una matriz industrial. Es obtener películas trazables con las que demostrar:

\[
R_A\approx R_B,
\qquad
\mathcal S_A\neq\mathcal S_B,
\qquad
F_A\neq F_B.
\]

## 21.2 Qué se compra y qué se contrata

El demostrador se divide en tres componentes:

1. **sustrato:** sílice fundida, vidrio óptico o silicio oxidado;
2. **película activa:** GST, Sb2Se3, Sb2S3 u otro calcogenuro justificado;
3. **servicio de deposición y caracterización:** sputtering, evaporación, encapsulación y metrología.

No es necesario comprar una máquina de sputtering. Una instalación de deposición es un laboratorio o empresa que
opera una cámara de vacío y deposita una película nanométrica sobre sustratos proporcionados por el cliente o por la
propia instalación.

En magnetron sputtering, un plasma de argón extrae material de un blanco sólido y lo deposita sobre el sustrato. La
instalación controla presión, potencia, temperatura, velocidad y espesor. La nucleación que codifica el NECE se
programa posteriormente mediante láser, microcalentadores u otra fuente térmica localizada.

## 21.3 Primera pila de muestra recomendada

### Demostrador óptico mínimo

```text
encapsulación dieléctrica
película calcogenura
sílice fundida o vidrio óptico
```

Ventajas:

- permite lectura en transmisión o reflexión;
- evita microfabricación eléctrica en la primera iteración;
- admite escritura láser y patrones de difracción;
- reduce coste y tiempo de ciclo.

### Demostrador electro-óptico posterior

```text
encapsulación dieléctrica
película calcogenura
espaciador dieléctrico
microcalentadores, pads y marcas
SiO2 térmico
wafer de silicio
```

El wafer de silicio es soporte, disipador e infraestructura de fabricación. La información NECE reside en la
configuración del calcogenuro.

## 21.4 Lista de compra de la etapa 0

Una primera solicitud conservadora puede especificar:

```text
Sustratos:
- 10 cupones de sílice fundida pulida
- dimensiones objetivo aproximadas: 20 mm x 20 mm
- varios testigos adicionales si la instalación los admite

Película:
- Ge2Sb2Te5 nominal o composición alternativa justificada
- estado inicial preferentemente amorfo
- espesor nominal inicial: 100 nm
- uniformidad y rugosidad declaradas

Encapsulación:
- Al2O3, SiO2 o capa dieléctrica validada por la instalación
- espesor objetivo sujeto a compatibilidad óptica y térmica
- preferiblemente depositada sin exposición intermedia al aire

Caracterización mínima:
- espesor
- composición aproximada
- rugosidad
- estado inicial
- muestra testigo para Raman, XRD o elipsometría cuando esté disponible
```

El espesor de 100 nm es un punto inicial de exploración, no una dimensión optimizada. Debe revisarse con el modelo
óptico y térmico, las limitaciones del proveedor y las primeras pruebas de escritura.

## 21.5 Orden correcto de aprovisionamiento

1. consultar primero a la instalación que realizará la deposición;
2. confirmar qué calcogenuros admite su cámara;
3. confirmar si ya posee blanco y receta;
4. confirmar dimensiones, sustratos y encapsulación compatibles;
5. pedir una cotización con y sin caracterización;
6. comprar un blanco únicamente si la instalación lo requiere y aprueba su especificación;
7. reservar la fabricación de microcalentadores solo después de validar la escritura óptica.

No se debe comprar un blanco por adelantado. La instalación puede exigir diámetro, espesor, pureza, backing plate,
bonding y compatibilidad RF o DC concretos.

## 21.6 Candidatos a consultar

Los siguientes nombres son **puntos de contacto potenciales**, no proveedores preaprobados ni garantía de que
acepten una composición en una cámara concreta. Debe verificarse su capacidad, política de contaminación, acceso a
usuarios externos, condiciones contractuales y disponibilidad actual.

### Infraestructuras científicas y de microfabricación

- IMB-CNM, Barcelona: consultar acceso externo, deposición, litografía y compatibilidad con Sb, Se y Te;
- International Iberian Nanotechnology Laboratory, Braga: consultar micro/nanofabricación, materiales,
  nanofotónica y caracterización;
- otras salas blancas universitarias o infraestructuras compartidas con sputtering no-CMOS o cámaras dedicadas a
  materiales funcionales.

### Empresas de películas finas a medida

- Kerdry/Neyco, Francia: consultar recubrimientos PVD, sputtering, evaporación, sustratos y encapsulación a medida;
- otras empresas europeas de thin-film coating que acepten composiciones calcogenuras y lotes pequeños de I+D.

### Proveedores de blancos

- Testbourne y proveedores equivalentes de sputtering targets: solicitar composición, pureza, geometría y bonding
  únicamente después de recibir la especificación de la instalación.

Páginas de entrada para verificación:

- `https://www.imb-cnm.csic.es/`
- `https://www.inl.int/`
- `https://www.neyco.fr/`
- `https://www.testbourne.com/sputtering-targets`

## 21.7 Preguntas que deben resolverse antes de pedir precio

La solicitud debe preguntar explícitamente:

- ¿aceptan Ge2Sb2Te5, Sb2Se3, Sb2S3 o los elementos constituyentes en la cámara propuesta?;
- ¿la cámara es dedicada, compartida con CMOS o restringida por contaminación?;
- ¿disponen de blanco y receta previa?;
- ¿pueden entregar la película en estado amorfo?;
- ¿pueden encapsular sin ruptura de vacío?;
- ¿qué sustratos, dimensiones y temperaturas son compatibles?;
- ¿qué uniformidad y rugosidad pueden declarar?;
- ¿qué caracterización está incluida?;
- ¿qué parte del coste corresponde a desarrollo de receta?;
- ¿se entregan muestras testigo y parámetros de proceso?;
- ¿qué reglas EHS, transporte y gestión de residuos se aplican?;
- ¿los datos y parámetros pueden publicarse en un repositorio abierto?;

La pregunta crítica no es simplemente si existe un equipo de sputtering. Es si la instalación permite el material
concreto sin comprometer sus procesos y si puede entregar una película trazable.

## 21.8 Rangos de planificación

| Elemento | Rango orientativo |
|---|---:|
| 10-20 cupones de sílice fundida | 100-400 EUR |
| Wafer Si/SiO2 para cortar en cupones | 80-250 EUR |
| Deposición de un lote si existen blanco y receta | 700-2.000 EUR |
| Encapsulación dieléctrica | 300-1.000 EUR |
| Blanco calcogenuro personalizado, si se exige | 1.000-3.500 EUR |
| Perfilometría y verificación básica de espesor | 100-400 EUR |
| Raman, XRD, AFM o SEM básicos | 500-2.000 EUR |
| Desarrollo de una receta nueva | 1.000-5.000 EUR adicionales |

Estos intervalos tienen incertidumbre alta. No deben citarse como precios de mercado ni como presupuesto adjudicado.
Deben sustituirse por cotizaciones fechadas y archivadas en la procedencia del proyecto.

### Escenario favorable

La instalación ya posee blanco, receta y encapsulación compatible:

- objetivo de planificación: **1.500-4.000 EUR**;
- resultado: lote de películas y caracterización mínima.

### Escenario normal de I+D

Es necesario adaptar receta, comprar blanco o ampliar caracterización:

- objetivo de planificación: **4.000-10.000 EUR**.

### Demostrador con microcalentadores

Incluye diseño de máscara, fotolitografía, metalización, contactos, deposición PCM, encapsulación y varias
iteraciones:

- objetivo de planificación: **8.000-25.000 EUR**.

La compra de microscopía, Raman, SEM o un sistema láser profesional no está incluida. Se presupone equipo propio,
acceso institucional o pago por horas.

## 21.9 Estrategia de reducción de coste

El orden de menor riesgo económico es:

1. validar óptica, control XY y adquisición con muestras inertes o un soporte de entrenamiento;
2. contratar un único espesor y una única composición;
3. obtener varios cupones del mismo lote;
4. comenzar con escritura óptica sobre película continua;
5. usar caracterización compartida solo cuando una medida cambie una decisión experimental;
6. añadir microcalentadores después de demostrar configuraciones isoagregadas;
7. reservar EBL, FIB y TEM para preguntas submicrométricas justificadas.

Un CD-RW puede utilizarse intacto para entrenar posicionamiento, enfoque y lectura de contraste. No debe sustituir la
muestra científica porque su composición, espesor, pista, reflector y capas protectoras no están controlados, y no
debe lijarse, rasparse o ablacionarse para extraer material.

## 21.10 Plantilla de solicitud de cotización

```text
Subject: Request for small-batch chalcogenide thin-film deposition for research

We are preparing a mesoscopic phase-change/nucleation experiment and request a quotation for a small batch of
traceable chalcogenide-coated substrates.

Requested baseline:
- substrate: polished fused-silica coupons, approximately 20 mm x 20 mm;
- quantity: 10 coated coupons plus process witnesses where possible;
- film: nominal Ge2Sb2Te5, initially amorphous;
- nominal film thickness: 100 nm;
- cap: Al2O3, SiO2, or your validated compatible dielectric;
- preference: cap deposited without intermediate air exposure;
- measurements: film thickness, approximate composition, roughness and initial-state verification;
- deliverables: process parameters that may be disclosed, measurement files, sample map and witness identification.

Please indicate:
- whether this material is permitted in your deposition system;
- whether you already have a compatible target and process;
- substrate and temperature constraints;
- achievable uniformity and roughness;
- whether process development is required;
- price with and without optional Raman/XRD/ellipsometry;
- expected contractual lead time;
- EHS, shipping and waste-handling requirements;
- publication or confidentiality restrictions.
```

La plantilla debe adaptarse a la composición y al instrumental real. No debe prometer dimensiones, estado inicial o
encapsulación que la instalación no pueda verificar.

## 21.11 Registro en MNS

Cada cotización o fabricación debe registrarse con:

- proveedor o instalación;
- fecha y versión de la especificación;
- composición nominal y medida;
- sustrato, espesor y encapsulación;
- identificadores de lote y cupones;
- parámetros de proceso divulgables;
- coste contratado y moneda;
- caracterización recibida;
- restricciones de publicación;
- desviaciones respecto a la solicitud;
- artefactos originales y hashes.

Los rangos de este documento se eliminan de cualquier cálculo de coste en cuanto existan cotizaciones reales. El
modelo económico debe utilizar el coste contratado y separar material, proceso, metrología, tiempo de sala blanca y
equipamiento reutilizable.

## 21.12 Decisión inmediata

La primera acción no es comprar materiales. Es enviar la misma especificación a tres tipos de interlocutor:

1. una infraestructura científica española o ibérica;
2. una empresa europea de películas finas a medida;
3. la sala blanca o laboratorio al que el investigador ya tenga acceso.

El proyecto debe comparar las respuestas por compatibilidad material, trazabilidad, caracterización, coste,
restricciones de publicación y riesgo de desarrollo, no solo por el precio más bajo.
