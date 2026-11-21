# Getting the user's chat history

## Opening message (when the skill starts without an export)

Send this, in the user's language, and wait for the upload. Keep the structure; adapt the wording.

> I can make you a personal report on how you use Claude: what you spend time on, what works,
> where it goes wrong, what you could turn into preferences, prompts or skills, and which work comes
> back often enough to run on its own. It takes a few minutes and the report is only for you.
>
> **What I need:** your chat export from claude.ai, the file called `conversations-000.zip`
> (plus `conversations-001.zip` and so on if your export has more parts). That's all: if you ran this before,
> the export already holds a short summary of that run, so I can compare with it.
>
> **How to get it:**
> 1. In claude.ai on the web or desktop app (not the phone app), go to **Settings → Privacy → Export data**.
> 2. Choose **90 days**, every time. (The report covers the last 30 days; the 60 days before them only show which
>    work comes back every month.)
> 3. You get an email with download links. Each link works for 24 hours and can stop working once used, so let each download finish.
> 4. Download only `conversations-000.zip` and upload it here.
>
> **Don't upload the other files.** `light_metadata` holds your email, phone number and login history, and
> the rest (`memories`, `projects`, `frames`, `design_chats`) isn't needed.
>
> Personal chats are counted but never described in the report.

On a Claude Team or Enterprise plan, add: "If you don't see Export data, an owner of your organization
has to allow members to export their own data first."

## When the user uploads something else

- **`light_metadata`, `memories`, `projects`, `frames` or `design_chats`:** say it isn't needed, don't open it, and ask for `conversations-000.zip`. Remind them `light_metadata` holds personal account details.
- **A ChatGPT export** (`conversations.json` with a `mapping` field, or a ZIP with `chat.html`): say this version reads claude.ai exports only and ChatGPT support is planned.
- **A Gemini Takeout, a Copilot file or a Claude Code log:** not supported in this version. For Claude Code, point to its built-in `/insights` command.
- **A conversations file from a period that's too short:** run `prepare.py` anyway; its message says what's possible and whether to export a longer period.

## Monthly reminder (SKILL.md step 15)

The scheduled task is named exactly **AI usage insights: monthly reminder** and runs on the 1st of the month, in the
morning, in the user's time zone, with push notifications on when the tool allows it. Its prompt is this fixed
text, with nothing personal added. The first line stays exactly as it is, in English, in every language: the next
run recognises the reminder's own chats by it and leaves them out. The rest is in the user's language.

> AI usage insights: monthly reminder
> Remind me of my monthly AI usage insights, in a few short lines, and do nothing else: don't read my chats, open
> files or run any analysis.
> 1. Request a claude.ai data export of the last 90 days: on the web or desktop app (not the phone app), go to
>    Settings → Privacy → Export data. The email's download links work for 24 hours; download only
>    `conversations-000.zip`.
> 2. Start a new chat, upload `conversations-000.zip`, and ask for my AI usage insights. Nothing else is needed.

## Not supported yet in v0.4

- **ChatGPT** (Settings → Data controls → Export data): planned next.
- **Gemini** (Google Takeout → My Activity → Gemini Apps): planned.
- **Microsoft 365 Copilot**: employees can't export their own history; needs IT.
- **Claude Code**: use its built-in `/insights` command instead.
