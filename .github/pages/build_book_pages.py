#!/usr/bin/env python3
"""
Generate the per-chapter playground pages from ``book_listings.json``.

Writes one Markdown file per chapter plus an index, into the directory given
as the first argument.  The workflow then renders each with the same pandoc
template as the rest of the site.

Because the listings come from the generated JSON, which itself comes from
``chapters/*.tex``, a code change in the book flows through to a runnable cell
with no hand-editing anywhere in the chain.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "sage", "playground", "book_listings.json")

BOOT = ('import urllib.request\n'
        'exec(urllib.request.urlopen("https://raw.githubusercontent.com/'
        'AppliedPQC/AppliedPQC/main/sage/playground.py").read())\n')


def cell(code):
    # No blank lines: CommonMark ends a raw HTML block at the first one.
    body = "\n".join(l for l in code.split("\n"))
    return '<div class="sage"><script type="text/x-sage">%s</script></div>\n' % body


def chapter_page(c):
    n_run = sum(1 for l in c["listings"] if l["runnable"])
    out = ["# %s\n" % c["title"],
           "Every code listing from this chapter of "
           "*Applied Post-Quantum Cryptography* — %d in total, %d of them "
           "runnable here. Edit any cell and press **Run**.\n"
           % (len(c["listings"]), n_run),
           "The book's snippets build on each other down the chapter, but a "
           "Sage Cell kernel runs one cell and keeps no state afterwards, so "
           "each cell replays the earlier listings first with `apqc_book`. "
           "That call is the only thing added to the book's code.\n",
           "[← all chapters](book-code.html) · "
           "[the four standards](playground.html)\n"]

    for l in c["listings"]:
        out.append("## Listing %d\n" % l["n"])
        if not l["runnable"]:
            out.append("Not runnable on its own: %s.\n" % l["note"])
            out.append("``` python\n%s\n```\n" % l["code"])
            continue
        pre = BOOT
        if l["n"] > 1:
            pre += "apqc_book('%s', upto=%d)\n" % (c["stem"], l["n"])
        elif l["requires"]:
            pre += "apqc_load(%s)\n" % ", ".join(repr(m) for m in l["requires"])
        out.append(cell(pre + l["code"]))
    return "\n".join(out)


def index_page(chapters):
    total = sum(len(c["listings"]) for c in chapters)
    out = ["# Code from the book\n",
           "All %d code listings from *Applied Post-Quantum Cryptography*, "
           "runnable in your browser. Nothing to install.\n" % total,
           "The cells are generated from the book's LaTeX sources, so they are "
           "the same code the chapters print.\n",
           "[The four standards →](playground.html)\n",
           "| Chapter | Listings | |",
           "| --- | --- | --- |"]
    for c in chapters:
        out.append("| %s | %d | [run](playground-%s.html) |"
                   % (c["title"], len(c["listings"]), c["stem"]))
    return "\n".join(out) + "\n"


def main():
    dest = sys.argv[1]
    os.makedirs(dest, exist_ok=True)
    chapters = json.load(open(DATA))["chapters"]
    for c in chapters:
        open(os.path.join(dest, "playground-%s.md" % c["stem"]), "w").write(chapter_page(c))
    open(os.path.join(dest, "book-code.md"), "w").write(index_page(chapters))
    print("%d chapter pages + index -> %s" % (len(chapters), dest))


if __name__ == "__main__":
    main()
