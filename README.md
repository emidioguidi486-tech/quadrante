# Quadrante

Cruscotto personale, pubblicato con GitHub Pages. I dati sono cifrati (AES-256-GCM): senza la chiave personale il sito mostra solo la richiesta della chiave.

## Come si aggiorna
L'automazione `.github/workflows/aggiorna.yml` gira da sola ogni mattina sui server di GitHub (nessun computer acceso):
scarica i dati di mercato, ricalcola, controlla la qualità e pubblica `data.enc` + `status.json`.
Se qualcosa non va il sito resta all'ultima versione buona e l'app mostra un avviso; GitHub manda un'email di errore.

- `private.enc` — motore di calcolo e dati personali, cifrati (si aprono con `ci/private_tool.py`)
- `seed.enc` — dati di mercato di riserva, cifrati
- secret richiesto: `QP_KEY`

Lancio manuale: tab **Actions** → *Aggiorna Quadrante* → *Run workflow*.
