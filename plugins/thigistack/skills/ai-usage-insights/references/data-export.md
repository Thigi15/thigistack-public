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
> 3. You get an email with a download link. It works for 24 hours and can stop working once used. It opens a list
>    of separate files to download.
> 4. Download only `conversations-000.zip` and upload it here.
>
> **Don't upload the other files.** `light_metadata` holds your email, phone number and login history, and
> the rest (`memories`, `projects`, `frames`, `design_chats`) isn't needed.
>
> Personal chats are counted but never described in the report.

The steps above are for Free, Pro, Max and Ultra. Ask which plan they use when it isn't clear, and on a Team or
Enterprise plan send this instead of steps 1 and 2, in the user's language:

> **On a Team or Enterprise plan** it depends on your role:
> - **Member or Owner:** the same **Settings → Privacy → Export data**, but only once an owner has turned on
>   **Allow members to export their own data** (Organization settings → Data and privacy → Data management). Don't
>   see Export data? Ask an owner to turn it on. If you're offered a period, choose 90 days; if not, export
>   everything and I'll use the last 90 days.
> - **Primary Owner:** you have no personal export, only one for the whole organization, and that file holds
>   everyone's chats. **Don't upload it:** this report is only about your own chats, and I'll refuse a file with
>   more than one person's chats in it. For now there is no way to run this report on a Primary Owner's own chats.

Notes for these plans, from Anthropic's help pages
([members](https://support.claude.com/en/articles/9450526-export-your-claude-data),
[organizations](https://support.claude.com/en/articles/13346720-export-your-organization-s-data), checked
21-11-2026):
- A member's export holds their own chats, without the contents of uploaded files. The help pages don't say whether
  it offers a period or uses the same file names; if the user's download list looks different, ask them to upload
  the file with "conversations" in its name, and `read_claude_ai.py` reports what it found.
- For an organization export the help page says chats deleted by users or by retention settings are left out; it
  says nothing about deleted chats for a member's own export.
- `read_claude_ai.py` stops with exit code 3 when the conversations name more than one account, and keeps nothing.
  That check only works when the export carries account ids; tell a Primary Owner not to upload the organization
  export rather than rely on it.

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
>    Settings → Privacy → Export data. The email's download link works for 24 hours; download only
>    `conversations-000.zip`.
> 2. Start a new chat, upload `conversations-000.zip`, and ask for my AI usage insights. Nothing else is needed.

## Not supported yet in v0.4

- **ChatGPT** (Settings → Data controls → Export data): planned next.
- **Gemini** (Google Takeout → My Activity → Gemini Apps): planned.
- **Microsoft 365 Copilot**: employees can't export their own history; needs IT.
- **Claude Code**: use its built-in `/insights` command instead.
