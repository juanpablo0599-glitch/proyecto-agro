# DECISIONES

Formato: fecha/hora (UTC) — decisión — alternativas — por qué.

## 2026-10-01 02:50 — Copiar MISION.md y runners al repo
- **Decisión:** el repo estaba vacío. Copié `MISION_1.md` (adjunto) como `MISION.md` en la raíz, más `correr_noche.sh` y `correr_noche.ps1`.
- **Alternativas:** dejarlos fuera del repo.
- **Por qué:** los runners buscan `MISION.md` en la raíz; si se relanza la sesión, la misión tiene que estar ahí. Además quedan versionados.

## 2026-10-01 02:50 — Rama de trabajo
- **Decisión:** todo se commitea y pushea a `claude/beautiful-goldberg-fowj1c`. No se toca `main` (no existe todavía) ni se abren PRs.
- **Por qué:** regla 3 de la misión y límites duros.
