# daily-dot

**Pre-fires Claude Pro's 5-hour session window** by sending an automated `.`
message every day at **09:00 UTC** (04:00 AM Colombia, UTC-5), so the rolling
resets land inside your workday instead of being wasted while you sleep.

Supports up to two Pro accounts in parallel (one per secret). Each call runs
independently — if one account fails, the other still goes through — and the
response is saved to `logs/YYYY-MM-DD.txt` along with the header (date, UTC
time, model, auth type) and the message sent.

## Why?

Claude Pro uses a **rolling 5-hour session window** that starts on your first
message and resets exactly five hours later. If you open the window when you
sit down to work (say 9 AM), your resets fall at 2 PM, 7 PM, and midnight —
and the last two are wasted outside working hours.

If instead you pre-fire the window at 4 AM with a `.`:

- While you sleep, the first window burns down (you would have wasted it anyway).
- At **9 AM** the first reset hits → fresh window right when you start working.
- At **2 PM** the second reset hits → another fresh window for the afternoon.
- By **7 PM** you're past working hours.

Result: two useful resets inside the workday instead of one. For anyone
running Claude Code for several hours straight, that translates into real
extra capacity without paying more.

> Usage counts against your Pro subscription, **not** against API billing.
> The cost of each call (a `.` to Haiku) is marginal, but it does consume a
> tiny slice of your weekly limit — see the "Notes" section below.

## Layout

```
daily-dot/
├── .github/workflows/daily-dot.yml   # GitHub Actions workflow
├── logs/                             # Daily responses (auto-committed)
└── README.md
```

## Setup, step by step

### 1. Clone or fork the repository

Fork it on GitHub, or clone it directly:

```bash
git clone https://github.com/<your-user>/daily-dot.git
cd daily-dot
```

If you cloned (instead of forking), create a new repo and push the code:

```bash
git remote set-url origin https://github.com/<your-user>/daily-dot.git
git push -u origin main
```

### 2. Generate the Claude Pro OAuth token

You need an active **Claude Pro** or **Claude Max** subscription. The
`setup-token` command does not work with free accounts.

On your local machine:

```bash
# Install Claude Code (requires Node.js 18+)
npm install -g @anthropic-ai/claude-code

# First time: log in with your Pro account (opens a browser)
claude
# (follow the login flow, then exit the chat with Ctrl+C or /exit)

# Generate the long-lived token for CI
claude setup-token
```

`claude setup-token` prints a token that starts with `sk-ant-oat01-...`.
Copy it — you'll need it in the next step. This is a mechanism officially
supported by Anthropic for using Claude Code in CI with Pro auth.

> If you have two Pro accounts (in two browsers or in incognito), repeat
> `claude setup-token` while logged into each one to obtain two separate
> tokens. Each `claude /login` overwrites the previous one, so do it
> sequentially and save each token before switching accounts.

### 3. Add the secrets to GitHub

In your repository:

1. Go to **Settings → Secrets and variables → Actions**.
2. Click **New repository secret**.
3. Create the secrets:
   - **Name:** `CLAUDE_CODE_OAUTH_TOKEN_1` — **Value:** the token for your first Pro account.
   - **Name:** `CLAUDE_CODE_OAUTH_TOKEN_2` — **Value:** the token for your second Pro account (optional; if you don't set it, the workflow simply skips that step).

### 4. Enable workflow write permissions

So Actions can commit the generated log:

1. Go to **Settings → Actions → General**.
2. Scroll down to **Workflow permissions**.
3. Select **Read and write permissions**.
4. Click **Save**.

### 5. Test the workflow manually

1. Open the repo's **Actions** tab.
2. Select **Daily Dot** in the sidebar.
3. Click **Run workflow → Run workflow**.
4. When it finishes, check:
   - The output of the *Send dot - Account 1* and *Account 2* steps.
   - The `logs/YYYY-MM-DD.txt` file auto-committed to the repo.

### 6. Adjust the time to your schedule (optional)

The default cron (`0 9 * * *` = 09:00 UTC = 04:00 AM Colombia) is set for
someone who starts working at 9 AM Colombia time. If your schedule is
different, compute:

> **cron hour (UTC) = (your local start-of-day) − 5h + UTC offset**

The idea is that the first window burns down while you sleep so the first
reset hits exactly when you sit down to work, giving you a full fresh
5-hour window.

## How it works

- **Cron:** `0 9 * * *` → 09:00 UTC daily. Firing five hours before your
  start-of-day means the first window burns down while you sleep and the
  first reset coincides with the moment you start working.
- **Manual trigger:** `workflow_dispatch` allows on-demand runs.
- **Authentication:** the CLI uses `CLAUDE_CODE_OAUTH_TOKEN` as an env var
  and usage is deducted from your Pro quota, not from API balance.
- **Model:** `claude-haiku-4-5-20251001` (configured via `CLAUDE_MODEL` in
  the workflow). Haiku is chosen because it's the cheapest model against
  Pro quota for a message as trivial as a `.`.
- **Account isolation:** each account runs in a separate step with
  `continue-on-error: true`. One failure does not stop the other.
- **CLI isolation:** each `claude` invocation runs with:
  - `--max-turns 1` → a single response, no agentic loop.
  - `--disallowedTools` disabling Bash, Edit, Write, Read, Grep, Glob,
    WebFetch, WebSearch, Task, TodoWrite, and NotebookEdit → Claude can
    only reply with text, it can't explore the repo or run commands.
  - `CLAUDE_CONFIG_DIR` pointing to a different temp directory per account
    (`mktemp -d`) → no history, projects, or preferences are shared
    between the two accounts.
  - `cwd=/tmp` when invoking the CLI → it does not load `CLAUDE.md`,
    `.claude/`, or any other repo context files.
- **Log append:** if the workflow runs several times on the same day, the
  entries pile up in the same file separated by a line of `=`.

## When to use a separate repo for the second account

This repo already supports two accounts with a single workflow. You only
need a separate repo if:

- You want to keep logs separate per account (each repo has its own logs).
- Your org has policies that prevent mixing tokens from different users.

For a second repo: fork this same one, configure only
`CLAUDE_CODE_OAUTH_TOKEN_1` with the other account's token, and leave the
*Account 2* step without a secret (it gets skipped automatically).

## Notes

- **Self-sustaining workflow:** GitHub disables scheduled workflows if the
  repo receives no commits for 60 days. Since this workflow commits a log
  every day, it keeps itself alive.
- **Cron precision:** GitHub Actions can delay the cron by a few minutes
  during peak hours. It's not a precision scheduler — if the cron drifts
  10 minutes, your resets drift too.
- **Token expiration:** OAuth tokens may expire eventually. If the workflow
  starts failing with auth errors, regenerate with `claude setup-token`
  and update the secret.
- **Weekly limit:** in addition to the 5-hour session window, Pro has a
  weekly limit shared across all models. Each `.` consumes a tiny fraction
  — a message to Haiku is essentially free — but the pool is shared with
  your usage on claude.ai and local Claude Code.
- **This is not an account keep-alive:** Claude Pro does not deactivate
  from inactivity. This workflow does not "keep the subscription alive";
  it only aligns the session window resets with your schedule.
