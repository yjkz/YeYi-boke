import re

from pypinyin import Style, pinyin


def generate_slug(text: str) -> str:
    if not text:
        return ""

    parts = []
    for segment in re.split(r'([一-鿿]+)', text):
        if not segment:
            continue
        if re.match(r'[一-鿿]+', segment):
            py = pinyin(segment, style=Style.NORMAL)
            for item in py:
                parts.append(item[0].lower())
        else:
            words = re.findall(r'[a-zA-Z0-9]+', segment)
            parts.extend(w.lower() for w in words)

    slug = "-".join(parts)
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')

    return slug or "untitled"
