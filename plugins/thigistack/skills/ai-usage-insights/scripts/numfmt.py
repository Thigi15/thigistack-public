"""Numbers in the report language, for both renderers: 1,180 and 0.5 in English, 1.180 and 0,5 in Dutch.

The language comes from synthesis.json's "language" ("en" or "nl"); anything else is English.
"""

SEPARATORS = {"en": (",", "."), "nl": (".", ",")}  # (thousands, decimal)
JS_LOCALES = {"en": "en-US", "nl": "nl-NL"}


def lang_of(syn):
    found = (syn or {}).get("language")
    return found if found in SEPARATORS else "en"


def number(value, lang="en"):
    """An int with thousands separators, or a float as Python's :g shows it, in the language's separators."""
    thousands, decimal = SEPARATORS.get(lang, SEPARATORS["en"])
    text = f"{value:,}" if isinstance(value, int) else f"{value:,.10g}"
    return text.replace(",", "\0").replace(".", decimal).replace("\0", thousands)


def percent(value, lang="en"):
    """A share rounded to a whole percent; a share above 0 and under 1 reads <1%."""
    return "<1%" if 0 < value < 1 else f"{number(round(value), lang)}%"


def js_locale(lang):
    return JS_LOCALES.get(lang, JS_LOCALES["en"])
