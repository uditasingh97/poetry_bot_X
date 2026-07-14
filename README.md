# Romance Poetry Bot 🌹

An automated X (Twitter) account that posts one public-domain romance verse per day, cycling across centuries — from Sappho and Catullus through the Renaissance, the Romantics, the Victorians, and the early moderns.

## How it works

- `verses.json` — the curated corpus. Each entry has the verse, poet, poem, year, era, and a provenance note.
- `bot.py` — picks the day's verse deterministically (day-of-year modulo corpus size, so no state file is needed) and posts it via the X API using `tweepy`.
- `.github/workflows/post.yml` — GitHub Actions cron job that runs the script once a day for free. No server required.

## Setup (one time, ~20 minutes)

### 1. Create the X account and get API access

1. Create the bot's X account.
2. In the account settings, go to **Your account → Account information → Automation** and label it as an automated account (required by X's rules).
3. Go to https://developer.x.com, sign in **as the bot account**, and sign up for the **Free** tier.
4. Create a Project + App. In the app's **User authentication settings**, enable **Read and Write** permissions (OAuth 1.0a).
5. From **Keys and tokens**, generate and copy four values:
   - API Key and API Key Secret (consumer keys)
   - Access Token and Access Token Secret
   
   If you generated the access token *before* enabling Read-and-Write, regenerate it afterwards — tokens inherit the permission level at creation time.

### 2. Create the GitHub repository

1. Create a new repo (private is fine) and push these files, keeping the folder structure (`.github/workflows/post.yml` must be at that exact path).
2. In the repo: **Settings → Secrets and variables → Actions → New repository secret**. Add four secrets with these exact names:
   - `X_API_KEY`
   - `X_API_SECRET`
   - `X_ACCESS_TOKEN`
   - `X_ACCESS_SECRET`

### 3. Test it

- Locally (optional): `pip install tweepy`, export the four env vars, then run `DRY_RUN=1 python bot.py` to preview without posting.
- On GitHub: go to the **Actions** tab → **Daily poetry post** → **Run workflow**. Check the log for the tweet preview and result.

After that, it posts automatically every day at the time in the cron line (default 9:00 AM IST). At one post a day you'll use ~30 of the free tier's ~500 monthly posts.

## Managing the corpus

- Add entries to `verses.json` any time — the rotation adjusts automatically.
- Keep every verse + attribution under ~280 characters (the script truncates long verses line-by-line as a fallback, but curating short excerpts looks better).
- **Copyright rules of thumb:**
  - Original works published before 1929: public domain in the US — safe.
  - Translations carry their *own* copyright. A medieval Persian poem in a 1995 translation is **not** safe; the same poem in an 1859 or 1898 translation is.
  - The Rumi entry in the starter corpus is deliberately flagged `REPLACE BEFORE USE` — the popular modern renderings of that passage are under copyright. Swap in a verified public-domain translation (R. A. Nicholson, *Selected Poems from the Divani Shamsi Tabriz*, 1898, or E. H. Whinfield's *Masnavi*, 1887 — both on archive.org). The script refuses to post any entry whose note contains `REPLACE BEFORE USE`, so nothing risky goes out by accident.
  - 20th-century poets published after 1928 (Neruda, Plath, Mary Oliver, etc.): skip, or link to the poem rather than reproducing it.

## Good sources for expanding the corpus

- **Project Gutenberg** (gutenberg.org) — full public-domain anthologies; search "love poems" or a poet's name.
- **PoetryDB** (poetrydb.org) — free API of public-domain poems, queryable by author/title.
- **Internet Archive** (archive.org) — scanned pre-1929 translations of Rumi, Hafiz, Sappho, etc.

## Ideas for later

- Tag entries with themes (`longing`, `devotion`, `heartbreak`) and rotate themes by weekday.
- Post threads for longer poems (the API supports `in_reply_to_tweet_id`).
- Add an image card (verse typeset on a background) using Pillow before posting.
