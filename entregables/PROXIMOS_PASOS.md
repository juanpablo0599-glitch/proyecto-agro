# Próximos pasos (lo que necesita humanos)

Orden sugerido para las próximas 6 semanas. Todo es barato: el costo principal es el tiempo y los viáticos de la socia.

---

## 0. Antes de nada (semana 1)
- [ ] **JP: consultar con compliance de su empleador** y dejar por escrito que el proyecto no usa información, contactos ni bases de la empresa, no vende insumos y no recomienda productos. Si compliance pone condiciones, anotarlas en `DECISIONES.md`.
- [ ] Leer `RESUMEN_EJECUTIVO.md` y `ANALISIS_Y_DECISION.md` juntos y confirmar (o discutir) la decisión de ir por la Idea A.
- [ ] Probar el MVP (`cd mvp && python3 app.py`) en los dos celulares. Anotar todo lo que confunda.

## 1. A quién entrevistar primero (semanas 1–4)
Meta: **15 entrevistas** de 30–45 minutos, en persona y en el galpón si se puede. Prospectar **solo con la red propia de la socia** y contactos públicos (asociaciones, eventos).

| Prioridad | Perfil | Cuántos | Por qué |
|---|---|---|---|
| 1 | **Dueños de contratistas medianos** (2–6 equipos) de la red de la socia | 6 | Son el segmento inicial y los que pagan |
| 2 | **Maquinistas y operarios** (1 con mucha experiencia, 2 nuevos) | 3 | Son los usuarios; validar lenguaje, formato y si lo usarían |
| 3 | **Contratista grande o empresa agropecuaria** con 10+ equipos | 2 | Plan Empresa; estandarización |
| 4 | **Técnico de posventa de un concesionario** | 1 | Qué problemas ve más; posible canal |
| 5 | **Referente de una asociación de FACMA** (ej. Casilda, Tres Arroyos, Entre Ríos) | 1 | Canal y aval; qué hacen hoy en formación |
| 6 | **Referente de RENATRE o de una escuela agrotécnica** | 1 | Aval de la certificación |
| 7 | **Productor que contrata servicios** | 1 | ¿Valora la constancia de labor? ¿Pagaría más por un servicio "con registro"? |

## 2. Diez preguntas de validación para contratistas
*(Preguntar por hechos del pasado, no por opiniones del futuro. No mostrar el producto hasta la pregunta 8.)*

1. **Contame la última vez que entró un operario nuevo.** ¿Cuánto tardó en rendir bien? ¿Quién le enseñó y cuánto tiempo le llevó a esa persona?
2. **¿Cuántos operarios se te fueron en las últimas dos campañas?** ¿Por qué? ¿Cuánto te costó reemplazarlos?
3. **¿Cuál fue la última rotura que podría haberse evitado?** ¿Qué pasó, cuánto costó y cuántos días estuvo parada la máquina?
4. **¿Alguna vez un cliente te reclamó por la calidad del trabajo** (pérdidas, mala siembra, deriva)? ¿Cómo se resolvió? ¿Perdiste al cliente?
5. **¿Medís las pérdidas de cosecha o calibrás la pulverizadora?** ¿Cada cuánto? ¿Quién lo hace? ¿Dónde queda anotado?
6. **¿Cómo te enterás hoy de que una máquina salió mal revisada?** ¿Usás algún sistema, planilla o grupo de WhatsApp?
7. **¿Qué pagás hoy por software, monitores, telemetría o capacitación?** ¿Cuánto por mes o por año? ¿Qué dejaste de pagar y por qué?
8. *(Mostrar el MVP 5 minutos)* **¿Qué es lo primero que usarías? ¿Qué no usarías nunca?** ¿Tus operarios lo harían todos los días? ¿Qué los frenaría?
9. **Si esto te ahorrara una rotura por campaña, ¿cuánto pagarías por mes por máquina?** (Dejar que diga un número antes de mencionar USD 25.) ¿Quién más tendría que aprobarlo?
10. **¿Te sumás a un piloto de 60 días con 2–4 máquinas, con medición antes y después?** Si dice que sí: fecha, máquinas y operarios. Si dice que no: ¿por qué?

**Para acopios/cooperativas con servicio de maquinaria (si aparecen):** ¿cuántos equipos propios o tercerizados tienen?, ¿cómo controlan la calidad de la labor que les hacen a sus socios?, ¿pagarían una licencia para ofrecerlo a sus socios?

**Señales de éxito para seguir:** ≥5 de 10 contratistas cuentan un problema concreto con costo en las últimas dos campañas; ≥5 aceptan un piloto; ≥3 dicen un precio ≥ USD 15/máquina/mes sin que se lo sugieras.

## 3. Experimentos baratos antes de seguir construyendo

| # | Experimento | Costo | Qué valida | Criterio de éxito |
|---|---|---|---|---|
| 1 | **"Concierge" por WhatsApp**: durante 2 semanas, la socia (o un técnico) responde a mano las consultas de 3–5 operarios en un grupo, usando las guías del MVP | Tiempo | ¿Los operarios preguntan? ¿Qué preguntan? ¿A qué hora? | ≥3 consultas por operario por semana |
| 2 | **Checklist en papel → app**: dar el checklist impreso a 2 contratistas por 1 semana y después la app otra semana | Impresiones | ¿El checklist se hace? ¿Cuánto tarda? ¿La app mejora o empeora? | ≥60% de las jornadas con checklist; ≤2 minutos |
| 3 | **Medición de pérdidas gratis** en 3 lotes de soja en la cosecha gruesa 2027, con informe para el productor | Viáticos | ¿El contratista y el productor valoran el número? ¿Hay pérdidas sobre la tolerancia? | 2 de 3 piden repetirla o la pagarían |
| 4 | **Prueba de precio**: en el cierre del piloto, ofrecer el Plan Equipo a USD 25 a la mitad y a USD 15 a la otra mitad | Nada | Elasticidad del precio | ≥1 cierre a USD 25 |
| 5 | **Landing con lista de espera** para "Operario Copiloto" (sin publicar hasta que lo decidan ustedes), compartida solo en la red propia | Gratis | Interés por la certificación | ≥20 operarios o contratistas anotados |
| 6 | **Charla en una asociación de FACMA** con la demo | Viáticos | Interés institucional y canal | 1 asociación que quiera un piloto con varios socios |
| 7 | **Revisión técnica del contenido** por un técnico/ingeniero de la red de la socia (o un extensionista INTA) | 2–3 h de alguien | Calidad y seguridad de las guías | Lista de correcciones aplicada antes del piloto |

## 4. Lo que hay que agregar al MVP antes del piloto (técnico, JP)
- PIN por operario y clave del tablero.
- Varias empresas (cada contratista con sus datos).
- Hosting barato o un servidor en la oficina del contratista (decidir con el primer cliente; la misión no permitía hacer deploy).
- Revisar las guías con el técnico (experimento 7).
- Si se usa IA real: crear la cuenta de API y la key (lo tienen que hacer ustedes) y medir el costo real por consulta.
