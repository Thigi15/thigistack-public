# thigistack

A plugin marketplace with one plugin, `thigistack`. It holds ten skills for claude.ai, Cowork and Claude Code. Each
skill was used for real before it was added here.

## Skills

| Skill | What it does | Works in |
|---|---|---|
| `bruh` | Restates the last answer, or the part you name, in plain words. Keeps every number and decision. | claude.ai, Claude Code |
| `sharpen` | Makes a task deeper instead of bigger. It asks what a top professional would do, then rewrites your prompt to ask for that. | claude.ai, Claude Code |
| `mece-tree` | Turns a messy list into a tree with no overlaps and no gaps. A how-tree sorts ideas and options. A why-tree finds the causes of a problem. Each branch ends in a next step or in a cause you can test. | claude.ai, Claude Code |
| `first-principles` | Breaks an idea or business case down to what is true. It labels each claim as a fact, an assumption or a habit, then rebuilds the options and names the cheapest test. | claude.ai, Claude Code |
| `decide` | Helps you choose between options. It checks how reversible the choice is and what is at stake. It ends with a decision card and a date to look at the choice again. | claude.ai, Claude Code |
| `ai-usage-insights` | Reads your own claude.ai chat export and writes a private report. The report covers where your time goes, what works and what goes wrong. It also lists what you could turn into preferences, prompts, skills or work that runs on its own. Needs Python 3.9 or newer. | claude.ai, Claude Code |
| `account-setup` | Sets up and reviews your claude.ai Instructions, memory and skills. It drafts a short Instructions block from an interview. | claude.ai |
| `new-project` | Sets up a claude.ai project: instructions, a project log and the right skills. | claude.ai |
| `review-project` | Reviews a claude.ai project against its log. It reports progress, open items that have stalled, drift from the goal, and an update for a steering group. | claude.ai |
| `memory-cleanup` | Cleans up what Claude remembers about you across your account. It checks each memory against recent chats and changes nothing without your yes. | claude.ai |

Most skills also start from a phrase such as "help me choose". Those phrases are in English and Dutch. `ai-usage-insights`
counts languages and spots corrections in those two only.

## Install

**claude.ai and Cowork.** Your plan must support custom plugin marketplaces. In the plugin settings, add the GitHub
repository `Thigi15/thigistack-public` as a marketplace, then install `thigistack`.

**Claude Code.**

    /plugin marketplace add Thigi15/thigistack-public
    /plugin install thigistack@thigistack-public

claude.ai picks up updates when the marketplace syncs. In Claude Code, run `/plugin marketplace update`.

## Changes and issues

This repository is generated from a private one, and only its owner changes it. Pull requests are not merged.
Issues with a bug or an idea are welcome.

`skills.json` lists the skills in the plugin and the commit they were built from.

## Licence

MIT, see `LICENSE`. `sharpen` is based on Lauren Tan's [pstack](https://github.com/cursor/plugins/tree/main/pstack),
and its folder holds pstack's MIT licence as `LICENSE-pstack.txt`. `bruh` is inspired by pstack's `bro` and was
written anew.
