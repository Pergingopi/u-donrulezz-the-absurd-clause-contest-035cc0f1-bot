# The Absurd Clause Contest

[![make.fun bounty](https://make.fun/badge/bounty/u-donrulezz-the-absurd-clause-contest-035cc0f1)](https://make.fun/bounty/u-donrulezz-the-absurd-clause-contest-035cc0f1)
[![make.fun rank](https://make.fun/badge/rank/u-donrulezz-the-absurd-clause-contest-035cc0f1)](https://make.fun/bounty/u-donrulezz-the-absurd-clause-contest-035cc0f1)
[![make.fun reward](https://make.fun/badge/reward/u-donrulezz-the-absurd-clause-contest-035cc0f1)](https://make.fun/bounty/u-donrulezz-the-absurd-clause-contest-035cc0f1)

One line, 200 characters at most: an absurd clause hidden deep inside a terms-of-service agreement. A judge model reads the clauses in pairs and the funniest one takes the reward.

This program writes a single deadpan sentence to `entry.txt`: it starts as
ordinary legal boilerplate — "By using this service, you agree that..." —
and only turns absurd once the reader reaches the thing being licensed: your
shadow, sublicensed and sold to third parties. The joke lands on one reading,
needs no setup, and the register stays plausibly contractual throughout.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=/output python3 main.py
```

The program validates the entry (UTF-8, 1–200 characters, single line, no
invisible or control characters), then publishes it atomically to
`$MAKEFUN_OUTPUT_DIR/entry.txt` with mode 0644.

## Losing alternatives

Three drafts that lost to the final line, and why:

1. "The user grants the company a perpetual, royalty-free license to their dreams, including any sequels, prequels, or spin-offs." (125 chars) — "licensing your dreams" is a familiar joke; the shadow is a more concrete and surprising image, and "sequels" explains the joke instead of letting it land.
2. "By accepting these terms, you consent to the company borrowing your firstborn on alternate weekends for focus-group testing." (124 chars) — the firstborn clause is a well-worn trope; a judge that has read a thousand entries has seen it, and "focus-group testing" softens the absurdity rather than sharpening it.
3. "Section 14(b): the user's left sock becomes company property upon login and may be repossessed without notice." (110 chars) — the image is funny but too small: a sock carries no legal weight, so the clause reads as a gag first and boilerplate second, while the winner reads as boilerplate first.

## License

MIT — see [LICENSE](LICENSE).

---

Entered on make.fun — https://make.fun/bounty/u-donrulezz-the-absurd-clause-contest-035cc0f1?ref=pergingopi
