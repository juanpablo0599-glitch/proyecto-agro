# Uso: .\correr_noche.ps1 -Horas 8
param([int]$Horas = 8)
$fin = (Get-Date).AddHours($Horas)
New-Item -ItemType Directory -Force -Path logs | Out-Null
$i = 0
$orden = "Lee MISION.md de esta carpeta y ejecutala siguiendo todas sus reglas. Si existe ESTADO.md, leelo primero y continua desde donde quedo. No hagas preguntas: decidi, documenta y segui."
while ((Get-Date) -lt $fin) {
  if (Test-Path DONE) { "Mision completa." | Tee-Object -FilePath logs\runner.log -Append; break }
  $i++
  "=== Ciclo $i - $(Get-Date) ===" | Tee-Object -FilePath logs\runner.log -Append
  claude -p $orden --dangerously-skip-permissions --max-turns 300 *> "logs\ciclo_$i.log"
  $code = $LASTEXITCODE
  "Ciclo $i termino con codigo $code" | Tee-Object -FilePath logs\runner.log -Append
  if (Test-Path DONE) { "Mision completa." | Tee-Object -FilePath logs\runner.log -Append; break }
  if ($code -ne 0) { Start-Sleep -Seconds 900 } else { Start-Sleep -Seconds 30 }
}
"Fin del runner - $(Get-Date)" | Tee-Object -FilePath logs\runner.log -Append
