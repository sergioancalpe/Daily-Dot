# daily-dot

Envía automáticamente un mensaje `.` a la API de Anthropic usando el modelo
`claude-haiku-4-5-20251001`, todos los días a las **11:00 UTC** (6:00 AM hora
Colombia). Hace dos llamadas independientes — una por cada API key — y guarda
la respuesta en `logs/YYYY-MM-DD.txt`.

## Estructura

```
daily-dot/
├── .github/workflows/daily-dot.yml   # Workflow de GitHub Actions
├── scripts/send_dot.py               # Script que llama a la API
├── logs/                             # Respuestas diarias (commit automático)
└── README.md
```

## Configuración paso a paso

### 1. Clonar o hacer fork del repositorio

Haz fork desde GitHub, o clónalo directamente:

```bash
git clone https://github.com/<tu-usuario>/daily-dot.git
cd daily-dot
```

Si clonaste (en vez de forkear), crea un repo nuevo en GitHub y empuja el
código:

```bash
git remote set-url origin https://github.com/<tu-usuario>/daily-dot.git
git push -u origin main
```

### 2. Agregar los secrets de la API

En tu repositorio de GitHub:

1. Ve a **Settings → Secrets and variables → Actions**.
2. Haz clic en **New repository secret**.
3. Crea los dos siguientes secrets:
   - **Name:** `ANTHROPIC_API_KEY_1` — **Value:** tu primera API key de Anthropic.
   - **Name:** `ANTHROPIC_API_KEY_2` — **Value:** tu segunda API key de Anthropic.

Puedes generar las keys en <https://console.anthropic.com/settings/keys>.

### 3. Activar permisos de escritura del workflow

Para que Actions pueda hacer commit del log generado:

1. Ve a **Settings → Actions → General**.
2. Baja hasta la sección **Workflow permissions**.
3. Selecciona **Read and write permissions**.
4. (Opcional pero recomendado) Activa **Allow GitHub Actions to create and
   approve pull requests**.
5. Haz clic en **Save**.

### 4. Probar el workflow manualmente

1. Ve a la pestaña **Actions** del repositorio.
2. Selecciona **Daily Dot** en la barra lateral.
3. Haz clic en **Run workflow → Run workflow**.
4. Cuando termine, revisa:
   - La salida del paso *Send dot to Anthropic API* (muestra la respuesta).
   - El archivo `logs/YYYY-MM-DD.txt` commiteado al repo.

## Cómo funciona

- **Cron:** `0 11 * * *` → 11:00 UTC todos los días (6:00 AM en Colombia, UTC-5).
- **Trigger manual:** `workflow_dispatch` permite ejecuciones on-demand.
- **Dos llamadas independientes:** cada key se invoca con su propio
  `try/except`; si una falla, la otra se ejecuta igual.
- **Log append:** si se ejecuta varias veces el mismo día, las entradas se
  añaden al mismo archivo `logs/YYYY-MM-DD.txt` separadas por `====`.

## Notas

- GitHub desactiva los workflows programados si el repo queda inactivo 60
  días. Haz un commit o ejecuta manualmente cada tanto para mantenerlo vivo.
- El cron de GitHub Actions puede retrasarse algunos minutos en horas pico.
