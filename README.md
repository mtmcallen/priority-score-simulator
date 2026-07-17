# Patient Prioritization Score Simulator

Interactive simulator for modeling CipherHealth Patient Prioritization priority scores from encounter and patient scenarios.

## Use locally

Open `index.html` in any browser, or serve the folder with any static file server.

## Share with others

### Copy link (easiest)

1. Configure your program and scenario in the simulator.
2. Click **Copy link** in the Share row.
3. Send the URL to a colleague — opening it loads your exact program and scenario.

Preset-only links also work:

```
https://your-host.example/#preset=builtin-ed-program
```

Built-in preset IDs: `builtin-central-hospital`, `builtin-default-program`, `builtin-ed-program`, `builtin-best-practice`

### Export / import file

- **Export file** — downloads a `.json` file you can email or attach.
- **Import file** — loads a previously exported program.

### Host on the web (GitHub Pages)

1. Push this repo to GitHub.
2. In the repo, go to **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Push to `main` — the included workflow publishes the site automatically.

Your team can then use a stable URL like `https://<org>.github.io/priority-score-simulator/`.

## Customer-facing templates

| Template | Public URL |
| --- | --- |
| **Staff SSR Hype Flyer** (editable) | [mtmcallen.github.io/priority-score-simulator/docs/staff-ssr-hype-flyer.html](https://mtmcallen.github.io/priority-score-simulator/docs/staff-ssr-hype-flyer.html) |
| **Ambient Listening Hype Flyer** (editable) | [mtmcallen.github.io/priority-score-simulator/docs/ambient-listening-hype-flyer.html](https://mtmcallen.github.io/priority-score-simulator/docs/ambient-listening-hype-flyer.html) |
| **Automated Voice Talent and Language Enhancements Hype Flyer** (editable) | [mtmcallen.github.io/priority-score-simulator/docs/conversational-ai-voice-hype-flyer.html](https://mtmcallen.github.io/priority-score-simulator/docs/conversational-ai-voice-hype-flyer.html) |

Open the flyer in a browser, click highlighted fields to customize for an account, paste a QR code image, then print or save as PDF.

## Scoring formula

```
Priority Score = ceil( (W1×V1 + W2×V2 + … + Wn×Vn) / (W1 + W2 + … + Wn) )
```

Only factors with a matching rule contribute to the calculation.

## Built-in programs

- **Central Hospital** — activation: Unit Facility = Central Hospital
- **Default Program** — no activation criteria
- **ED Program** — activation: Rounding Flag = ED Admit; LOS, expected discharge, age
- **Best Practice** — LOS, age, negative response thresholds

Based on the [Patient Prioritization configuration spreadsheet](https://docs.google.com/spreadsheets/d/1qfN5BVynmE5TqNHpZOQRDkt5Q-FFMM33Hh9aU_Erg5M/edit?gid=700465482).
