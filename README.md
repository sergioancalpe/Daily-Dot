# daily-dot

**Pre-dispara la session window de 5 horas de Claude Pro** enviando un mensaje
`.` automáticamente cada día a las **9:00 UTC** (4:00 AM hora Colombia, UTC-5),
para que los resets de la ventana caigan dentro de tu jornada laboral en vez de
desperdiciarse mientras duermes.

Soporta hasta dos cuentas Pro en paralelo (una por secret). Cada llamada se
ejecuta de forma independiente — si una cuenta falla, la otra corre igual — y
la respuesta queda guardada en `logs/YYYY-MM-DD.txt` junto con la cabecera
(fecha, hora UTC, modelo, tipo de auth) y el mensaje enviado.

## ¿Por qué?

Claude Pro funciona con una **session window rolling de 5 horas** que arranca
con el primer mensaje que envías y se resetea exactamente 5 horas después. Si
abres la ventana cuando empiezas a trabajar (digamos 8 AM), tus resets caen a
la 1 PM, 6 PM y 11 PM — y los dos últimos se desperdician fuera de horario.

Si en cambio pre-disparas la ventana a las 4 AM con un `.`:

- Mientras duermes, la primera ventana corre y se "quema" (la ibas a desperdiciar igual).
- A las **9 AM** llega el primer reset → ventana fresca justo cuando empiezas a trabajar.
- A las **2 PM** llega el segundo reset → otra ventana fresca para la tarde.
- A las **7 PM** ya estás fuera de horario.

Resultado: dos resets útiles dentro del día laboral en vez de uno solo. Para
quien usa Claude Code varias horas seguidas, eso se traduce en cupo extra real
sin pagar más.

> El uso cuenta contra tu suscripción Pro, **no** contra billing de API. El
> costo de cada llamada (un `.` a Haiku) es marginal, pero sí descuenta una
> porción mínima de tu weekly limit — ver sección "Notas" más abajo.

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
Cópialo — lo necesitarás en el siguiente paso. Es un mecanismo soportado
oficialmente por Anthropic para usar Claude Code en CI con auth de Pro.

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

### 6. Ajustar la hora al horario tuyo (opcional)

El cron por defecto (`0 9 * * *` = 9:00 UTC = 4:00 AM Colombia) está pensado
para alguien que empieza a trabajar a las 9 AM hora Colombia. Si tu horario
es distinto, calcula:

> **hora del cron (UTC) = (hora de inicio de jornada local) − 5h + offset UTC**

La idea es que la primera ventana se "queme" mientras duermes y el primer
reset caiga justo al sentarte a trabajar, dándote 5 horas frescas completas.

## Cómo funciona

- **Cron:** `0 9 * * *` → 9:00 UTC diarios. Disparar 5 horas antes del inicio
  de jornada hace que la primera ventana se queme mientras duermes y el primer
  reset coincida con el momento de empezar a trabajar.
- **Trigger manual:** `workflow_dispatch` permite ejecuciones on-demand.
- **Autenticación:** el CLI usa `CLAUDE_CODE_OAUTH_TOKEN` como env var y el
  uso descuenta de tu cuota de Pro, no de saldo de API.
- **Modelo:** `claude-haiku-4-5-20251001` (configurado via `CLAUDE_MODEL` en
  el workflow). Se elige Haiku porque es el modelo más barato en cupo de Pro
  para un mensaje tan trivial como un `.`.
- **Aislamiento entre cuentas:** cada cuenta corre en un step separado con
  `continue-on-error: true`. El fallo de una no detiene a la otra.
- **Aislamiento del CLI:** cada invocación de `claude` corre con:
  - `--max-turns 1` → una sola respuesta, sin loop agéntico.
  - `--disallowedTools` deshabilitando Bash, Edit, Write, Read, Grep, Glob,
    WebFetch, WebSearch, Task, TodoWrite y NotebookEdit → Claude solo puede
    responder texto, no puede explorar el repo ni ejecutar comandos.
  - `CLAUDE_CONFIG_DIR` apuntando a un directorio temporal distinto por
    cuenta (`mktemp -d`) → no se comparte historial, proyectos ni preferencias
    entre las dos cuentas.
  - `cwd=/tmp` al invocar el CLI → no carga `CLAUDE.md`, `.claude/` ni otros
    archivos de contexto del repo.
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

- **Workflow autosostenido:** GitHub desactiva los workflows programados si el
  repo no recibe commits por 60 días. Como este workflow commitea el log cada
  día, se mantiene vivo solo.
- **Precisión del cron:** GitHub Actions puede retrasar el cron algunos
  minutos en horas pico. No es un scheduler de precisión — si el cron se
  retrasa 10 minutos, tus resets también.
- **Expiración del token:** los tokens OAuth pueden caducar eventualmente. Si
  el workflow empieza a fallar con errores de auth, regenera con
  `claude setup-token` y actualiza el secret.
- **Weekly limit:** además de la session window de 5 horas, Pro tiene un
  límite semanal compartido entre todos los modelos. Cada `.` consume una
  fracción mínima — un mensaje a Haiku es prácticamente gratis — pero el pool
  se comparte con tu uso en claude.ai y Claude Code local.
- **No es un keep-alive de la cuenta:** Claude Pro no se desactiva por
  inactividad. Este workflow no "mantiene viva" la suscripción; solo alinea
  los resets de la session window con tu horario.
