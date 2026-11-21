"""Check every quote in the facet files against the user's own messages.

Usage:
    python3 -I check_quotes.py selected.jsonl facets_*.jsonl --out facets_checked.jsonl

A quote counts as found when it appears in one of that chat's user messages,
after normalising case, whitespace and curly quotes. Anything whose quote is not
found is dropped from the output and listed, so the report never rests on words
the user did not write. A recurrence signal whose quote is not found falls back to
"none". Personal chats lose all quotes and every loop signal, found or not.
"""
import argparse
import json
import re


def norm(s):
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("conversations")
    ap.add_argument("facets", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    user_text = {}
    for line in open(args.conversations, encoding="utf-8"):
        c = json.loads(line)
        user_text[c["id"][:8]] = norm(" \n ".join(m["text"] for m in c["messages"] if m["role"] == "user"))
    checked = found = 0
    missing, seen = [], set()
    with open(args.out, "w", encoding="utf-8") as out:
        for path in args.facets:
            for line in open(path, encoding="utf-8"):
                if not line.strip():
                    continue
                f = json.loads(line)
                if f["id"] in seen:
                    continue
                seen.add(f["id"])
                if f.get("scope") == "personal":
                    for k in ("friction", "instructions", "evidence", "checks"):
                        f[k] = []
                    f.pop("start_quote", None)
                    f["summary"] = "Personal topic."
                    f["recurrence"] = {"signal": "none", "quote": ""}
                    f["watch_subject"] = ""
                text = user_text.get(f["id"], "")

                def keep(items, key, kind):
                    nonlocal checked, found
                    kept = []
                    for item in items or []:
                        checked += 1
                        if norm(item.get(key)) and norm(item.get(key)) in text:
                            found += 1
                            kept.append(item)
                        else:
                            missing.append((f["id"], kind, item.get(key)))
                    return kept

                f["friction"] = keep(f.get("friction"), "quote", "friction")
                f["instructions"] = keep(f.get("instructions"), "text", "instruction")
                f["evidence"] = keep(f.get("evidence"), "quote", "evidence")
                if f.get("start_quote"):
                    checked += 1
                    if norm(f["start_quote"]) in text:
                        found += 1
                    else:
                        missing.append((f["id"], "start_quote", f.pop("start_quote")))
                rec = f.get("recurrence") or {}
                if rec.get("signal", "none") != "none":
                    checked += 1
                    if norm(rec.get("quote")) and norm(rec.get("quote")) in text:
                        found += 1
                    else:
                        missing.append((f["id"], "recurrence", rec.get("quote")))
                        f["recurrence"] = {"signal": "none", "quote": ""}
                out.write(json.dumps(f, ensure_ascii=False) + "\n")
    print(f"{len(seen)} chats; {found}/{checked} quotes found in the user's own messages")
    for m in missing:
        print("NOT FOUND (dropped):", m)


if __name__ == "__main__":
    main()
