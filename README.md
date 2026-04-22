# daily-dot

Mantiene activa tu cuenta de **Claude Pro** enviando un mensaje `.` automáticamente
todos los días a las **11:00 UTC** (6:00 AM hora Colombia) usando el CLI de
Claude Code autenticado con OAuth. El uso cuenta contra tu suscripción Pro,
**no** contra billing de API.

Soporta hasta dos cuentas Pro en paralelo (una por secret). Cada llamada se
ejecuta de forma independiente — si una cuenta falla, la otra corre igual — y
la respuesta queda guardada en `logs/YYYY-MM-DD.txt`.

## Estructura

```
daily-dot/
├── .github/workflows/daily-dot.yml   # Workflow de GitHub Actions
├── logs/                             # Respuestas diarias (commit automático)
└── README.md
```

## Configuración paso a paso

### 1. Clonar o hacer fork del repositorio

Fork desde GitHub, o clónalo directamente:

```bash
git clone https://github.com/<tu-usuario>/daily-dot.git
cd daily-dot
```

Si clonaste (en vez de forkear), crea un repo nuevo y sube el código:

```bash
git remote set-url origin https://github.com/<tu-usuario>/daily-dot.git
git push -u origin main
```

### 2. Generar el OAuth token de Claude Pro

Necesitas tener una suscripción activa de **Claude Pro** o **Claude Max**.
El comando `setup-token` no funciona con cuentas gratis.

En tu máquina local:

```bash
# Instala Claude Code (requiere Node.js 18+)
npm install -g @anthropic-ai/claude-code

# Primera vez: logueate con tu cuenta Pro (abre el navegador)
claude
# (sigue el flujo de login y luego sal del chat con Ctrl+C o /exit)

# Genera el token de larga duración para CI
claude setup-token
```

`claude setup-token` imprime un token que empieza con `sk-ant-oat01-...`.
Cópialo — lo necesitarás en el siguiente paso.

> Si tienes dos cuentas Pro (en dos navegadores o en incógnito), repite
> `claude setup-token` estando logueado con cada una para obtener dos tokens
> separados. Cada `claude /login` sobreescribe el anterior, así que házlo
> secuencialmente y guarda cada token antes de cambiar de cuenta.

### 3. Agregar los secrets en GitHub

En tu repositorio:

1. Ve a **Settings → Secrets and variables → Actions**.
2. Haz clic en **New repository secret**.
3. Crea los secrets:
   - **Name:** `CLAUDE_CODE_OAUTH_TOKEN_1` — **Value:** el token de tu primera cuenta Pro.
   - **Name:** `CLAUDE_CODE_OAUTH_TOKEN_2` — **Value:** el token de tu segunda cuenta Pro (opcional; si no lo configuras, el workflow simplemente omite ese paso).

### 4. Activar permisos de escritura del workflow

Para que Actions pueda hacer commit del log generado:

1. Ve a **Settings → Actions → General**.
2. Baja hasta **Workflow permissions**.
3. Selecciona **Read and write permissions**.
4. Haz clic en **Save**.

### 5. Probar el workflow manualmente

1. Ve a la pestaña **Actions** del repositorio.
2. Selecciona **Daily Dot** en la barra lateral.
3. Haz clic en **Run workflow → Run workflow**.
4. Cuando termine, revisa:
   - La salida de los steps *Send dot - Account 1* y *Account 2*.
   - El archivo `logs/YYYY-MM-DD.txt` commiteado automáticamente al repo.

## Cómo funciona

- **Cron:** `0 11 * * *` → 11:00 UTC diarios (6:00 AM Colombia, UTC-5).
- **Trigger manual:** `workflow_dispatch` permite ejecuciones on-demand.
- **Autenticación:** el CLI usa `CLAUDE_CODE_OAUTH_TOKEN` como env var y el
  uso descuenta de tu cuota de Pro, no de saldo de API.
- **Aislamiento entre cuentas:** cada cuenta corre en un step separado con
  `continue-on-error: true`. El fallo de una no detiene a la otra.
- **Log append:** si el workflow corre varias veces el mismo día, las entradas
  se acumulan en el mismo archivo separadas por una línea de `=`.

## Cuándo usar un repo separado para la segunda cuenta

Este repo ya soporta dos cuentas con un solo workflow. Solo necesitas un repo
separado si:

- Quieres separar los logs por cuenta (cada repo tiene sus propios logs).
- Tu organización tiene políticas que impiden mezclar tokens de usuarios distintos.

Para un segundo repo: fork este mismo, configura solo `CLAUDE_CODE_OAUTH_TOKEN_1`
con el token de la otra cuenta, y deja el step *Account 2* sin secret (se omite
automáticamente).

## Notas

- **Inactividad:** GitHub desactiva los workflows programados si el repo no
  recibe commits por 60 días. Como este workflow commitea el log cada día,
  se mantiene vivo solo.
- **Precisión del cron:** GitHub Actions puede retrasar el cron algunos
  minutos en horas pico. No es un scheduler de precisión.
- **Expiración del token:** los tokens OAuth pueden caducar eventualmente. Si
  el workflow empieza a fallar con errores de auth, regenera con
  `claude setup-token` y actualiza el secret.
- **Cuotas de Pro:** cada llamada consume una porción mínima de tu cupo de
  mensajes de Pro (una request por día con un `.` es insignificante), pero
  comparte el pool con el uso que hagas en claude.ai y Claude Code local.
