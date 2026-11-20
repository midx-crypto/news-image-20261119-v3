# The World in One Day — Thursday 19 November 2026

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/midx-crypto/news-image-20261119-v3/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/midx-crypto/news-image-20261119-v3/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

One image that sums up the world's news of **Thursday 19 November 2026** —
an entry for the [make.fun bounty](https://make.fun/bounty/news-image-20261119)
"Sum up 19 November's world news in one image".

Referral: `g5h40b4t`

## What's in the picture

43 verified stories across 7 regions, in a premium-broadsheet layout:

- **Hero trio** — the day's three biggest stories: the first Trump–Xi–Putin
  three-way summit in Shenzhen ("Declaration toward Peace"), the ICJ's 9–6
  ruling that Myanmar committed genocide against the Rohingya, and the COP31
  draft deal that drops fossil fuels and the $120bn adaptation target.
- **12 numbered stories** — Anthropic's record $81.3bn IPO, GTA VI's launch
  after 13 years, the third strike on the Crimea Bridge, Denmark's 109–0
  Greenland vote, Cyclone Akvan, Korea's Suneung exam, Australia's 4.9%
  jobless rate, Bangladesh's arson wave, the Hormuz tanker claims, the end of
  the Gaza tank raid, the Houthi strike on Riyadh's PIF Tower, and
  Indonesia's asset-seizure law after 18 years.
- **A world map** with numbered dots for every located story.
- **"Also on Thursday"** — 28 more verified stories, from Colombia's national
  strike to Mongolia's presidential resignation.
- **Date check** — five stories deliberately left out because they happened on
  other days (Rooppur's grid link on 17 Nov, Kenya's last Ebola discharge on
  11 Nov, and more).

Every story was checked against a primary reputable source (Reuters, AP, BBC,
WSJ, IAEA, ICJ, IMD, ABS, Le Monde). Anything unverified is tagged **CLAIM**,
never stated as fact; forecasts are labelled as forecasts.

## How it was built

- `news.json` — the dataset: headline, summary, place, region, source and
  confidence for every story, all written fresh in this session.
- `render.py` — draws `entry.png` (1024×1024) with PIL: flat vector-style
  illustrations drawn in code, deterministic (fixed seed, no network, no
  timestamps). Re-rendering produces byte-identical output.
- `main.py` — the entrypoint (Python 3.13, standard library only). It simply
  copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` after validating its
  size, dimensions and PNG chunk chain. It does no rendering at run time.

## Run it

```sh
# re-render the image (needs Pillow on the build machine only)
python3 render.py

# run the entrypoint the way the grader does
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# -> out/entry.png, 1024x1024, 205584 bytes
```

## License

MIT — see [LICENSE](LICENSE).
