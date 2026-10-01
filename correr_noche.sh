#!/usr/bin/env bash
# Uso: ./correr_noche.sh [horas]   (por defecto 8)
# Relanza Claude Code en ciclos hasta que aparezca el archivo DONE o se acabe el tiempo.
set -u
HORAS="${1:-8}"
FIN=$(( $(date +%s) + HORAS*3600 ))
mkdir -p logs
i=0
while [ "$(date +%s)" -lt "$FIN" ]; do
  [ -f DONE ] && { echo "Misión completa." | tee -a logs/runner.log; break; }
  i=$((i+1))
  echo "=== Ciclo $i — $(date) ===" | tee -a logs/runner.log
  claude -p "Leé MISION.md de esta carpeta y ejecutala siguiendo todas sus reglas. Si existe ESTADO.md, leelo primero y continuá desde donde quedó. No hagas preguntas: decidí, documentá y seguí." \
    --dangerously-skip-permissions \
    --max-turns 300 \
    > "logs/ciclo_$i.log" 2>&1
  CODE=$?
  echo "Ciclo $i terminó con código $CODE" | tee -a logs/runner.log
  [ -f DONE ] && { echo "Misión completa." | tee -a logs/runner.log; break; }
  # Si salió con error (ej. límite de uso), espera más antes de reintentar
  if [ "$CODE" -ne 0 ]; then sleep 900; else sleep 30; fi
done
echo "Fin del runner — $(date)" | tee -a logs/runner.log
