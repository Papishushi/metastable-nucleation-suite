## Trabajo vinculado

Closes #

Épica principal: #

## Resultado entregado

Describe el resultado científico, operativo o visible para el usuario. No enumeres únicamente archivos modificados.

## Hipótesis o problema que aborda

Para documentación, CI o tooling puede indicarse `No aplica` con una justificación breve.

## Predicción nula o comportamiento esperado

Para cambios no científicos, describe el comportamiento previo y el resultado esperado o indica `No aplica` con una justificación breve.

## Cambios principales

- 

## Validación ejecutada

- [ ] `make check`
- [ ] Los cálculos críticos nuevos o modificados tienen pruebas de regresión.
- [ ] Los cambios semánticos pasan JSON Schema y SHACL.
- [ ] Los cambios de hardware conservan ensayos fallidos, exclusiones y diagnósticos.
- [ ] Se añadieron o actualizaron fuentes primarias cuando procede.
- [ ] Los análisis exploratorios están identificados como tales.
- [ ] La documentación y los ejemplos describen el comportamiento implementado.
- [ ] Los checks no aplicables se explican en la descripción.

## Riesgos científicos y operativos

Explica confundidores, postselección, memoria, drift, límites de causalidad, compatibilidad, migraciones de datos y riesgos de seguridad de hardware. Para un cambio sin impacto en estas áreas, indica por qué el riesgo es bajo.

## Checklist de revisión

- [ ] Los criterios de aceptación del PBI están satisfechos.
- [ ] No quedan hilos de revisión sin resolver.
- [ ] La CI pasa sobre el commit actual.
- [ ] Los artifacts y datasets no contienen secretos ni datos personales no controlados.
- [ ] No se divulgan vulnerabilidades ni credenciales en el PR.
- [ ] La contribución respeta `CODE_OF_CONDUCT.md` y `SECURITY.md`.