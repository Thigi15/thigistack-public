# thigistack

A plugin marketplace with one plugin, `thigistack`: skills for claude.ai, Cowork and Claude Code that have proven
themselves in daily use. A skill is added here only once it is finished and has been used for real.

## Install

**claude.ai, Cowork:** in the plugin settings, add the GitHub repository `Thigi15/thigistack-public` as a
marketplace, then install `thigistack`.

**Claude Code:**

    /plugin marketplace add Thigi15/thigistack-public
    /plugin install thigistack@thigistack-public

Updates arrive when the marketplace syncs (claude.ai), or with `/plugin marketplace update` (Claude Code).

## Skills

`skills.json` lists the skills in the plugin and the commit they were built from. Each skill's `compatibility`
line says where it works: the account and project setup skills are for claude.ai only, the others work in claude.ai
and Claude Code.

## Changes and issues

This repository is generated from a private one and is changed only by its owner, so pull requests are not merged.
Issues with a bug or an idea are welcome.

## Licence

MIT, see `LICENSE`. A skill based on Lauren Tan's [pstack](https://github.com/cursor/plugins/tree/main/pstack)
carries pstack's MIT licence beside it, as `LICENSE-pstack.txt`.
