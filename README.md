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

### Host on Cipher PaaS (SSO-gated)

This repo includes `tool.yaml` manifests for [Cipher PaaS](https://console.tools.cipherhealth.dev).

#### Patient Prioritization Simulator

1. **Connect the repo** in the Cipher console (grants you deploy access).
2. **Sync and deploy** (uses `--commit --save --repo SolarCS/paas_apps` for persistence):

   ```bash
   ./scripts/sync-paas-deploy.sh
   ./scripts/deploy-paas-apps.sh priority-score-sim-mcarroll
   ```

   Or from repo root after syncing: `paas deploy --commit --save --repo SolarCS/paas_apps`

App name: `priority-score-sim-mcarroll` → https://priority-score-sim-mcarroll.tools.cipherhealth.dev

#### Hype flyers (separate PaaS apps)

Each editable hype flyer is its own SSO-gated app in the console:

| Flyer | App name | Manifest |
| --- | --- | --- |
| Staff SSR | `staff-ssr-hype-flyer-mcarroll` | `paas/staff-ssr-hype-flyer-mcarroll/tool.yaml` |
| Ambient Listening | `ambient-listening-hype-flyer-mcarroll` | `paas/ambient-listening-hype-flyer-mcarroll/tool.yaml` |
| Ambient Listening Device Requirements (combined) | `al-device-requirements-mcarroll` | `paas/al-device-requirements-mcarroll/tool.yaml` |
| Ambient Listening Device Requirements (iOS) | `al-device-requirements-ios-mcarroll` | `paas/al-device-requirements-ios-mcarroll/tool.yaml` |
| Ambient Listening Device Requirements (Android) | `al-device-requirements-android-mcarroll` | `paas/al-device-requirements-android-mcarroll/tool.yaml` |
| Patient Prioritization | `patient-prioritization-flyer-mcarroll` | `paas/patient-prioritization-flyer-mcarroll/tool.yaml` |
| Patient Prioritization Device Requirements (combined) | `pp-device-requirements-mcarroll` | `paas/pp-device-requirements-mcarroll/tool.yaml` |
| Patient Prioritization Device Requirements (iOS) | `pp-device-requirements-ios-mcarroll` | `paas/pp-device-requirements-ios-mcarroll/tool.yaml` |
| Patient Prioritization Device Requirements (Android) | `pp-device-requirements-android-mcarroll` | `paas/pp-device-requirements-android-mcarroll/tool.yaml` |
| Home final walkthrough | `home-final-walkthrough-mcarroll` | `paas/home-final-walkthrough-mcarroll/tool.yaml` |
| Change log voting | `change-log-voting-mcarroll` | `paas/change-log-voting-mcarroll/tool.yaml` |

```bash
./scripts/deploy-paas-apps.sh
```

Deploy one or more apps by name:

```bash
./scripts/deploy-paas-apps.sh pp-device-requirements-mcarroll al-device-requirements-mcarroll
```

#### Updating apps (persistence)

Each live app is keyed by the stable `name:` in its `tool.yaml` (for example `pp-device-requirements-mcarroll`). **Redeploying with the same name updates the existing app in place** — the URL does not change and the app is not recreated.

The deploy script syncs fresh bundles from `docs/` (or the simulator root), then runs:

```bash
paas deploy --commit --save --repo SolarCS/paas_apps
```

That commits deploy source to the org `SolarCS/paas_apps` monorepo and saves the preference for future deploys, so updates survive beyond your local machine.

**Do not rename** an app in `tool.yaml` unless you intentionally want a new PaaS app and URL. To undo a bad release: `paas rollback <app-name>`.

Live URLs (after deploy):

- https://staff-ssr-hype-flyer-mcarroll.tools.cipherhealth.dev
- https://ambient-listening-hype-flyer-mcarroll.tools.cipherhealth.dev
- https://al-device-requirements-mcarroll.tools.cipherhealth.dev
- https://al-device-requirements-ios-mcarroll.tools.cipherhealth.dev
- https://al-device-requirements-android-mcarroll.tools.cipherhealth.dev
- https://patient-prioritization-flyer-mcarroll.tools.cipherhealth.dev
- https://pp-device-requirements-mcarroll.tools.cipherhealth.dev
- https://pp-device-requirements-ios-mcarroll.tools.cipherhealth.dev
- https://pp-device-requirements-android-mcarroll.tools.cipherhealth.dev

The manifest uses `source_dir: deploy` so only static assets are uploaded — not the full repo.

## Customer-facing templates

| Template | Public URL |
| --- | --- |
| **Staff SSR Hype Flyer** (editable) | [mtmcallen.github.io/priority-score-simulator/docs/staff-ssr-hype-flyer.html](https://mtmcallen.github.io/priority-score-simulator/docs/staff-ssr-hype-flyer.html) |
| **Staff SSR Overview Slide** (16:9 — what it is, enablement, benefits) | [mtmcallen.github.io/priority-score-simulator/docs/staff-ssr-kickoff-slide.html](https://mtmcallen.github.io/priority-score-simulator/docs/staff-ssr-kickoff-slide.html) |
| **Staff SSR Overview Slide 2** (16:9 — overview, features, benefits + mobile screenshot) | [HTML preview](https://mtmcallen.github.io/priority-score-simulator/docs/staff-ssr-overview-slide-2.html) · [PPTX source](https://mtmcallen.github.io/priority-score-simulator/docs/staff-ssr-overview-slide-2.pptx) |
| **Ambient Listening Hype Flyer** (editable) | [mtmcallen.github.io/priority-score-simulator/docs/ambient-listening-hype-flyer.html](https://mtmcallen.github.io/priority-score-simulator/docs/ambient-listening-hype-flyer.html) |
| **Ambient Listening Overview Slide** (16:9 — what it is, enablement, benefits) | [mtmcallen.github.io/priority-score-simulator/docs/ambient-listening-kickoff-slide.html](https://mtmcallen.github.io/priority-score-simulator/docs/ambient-listening-kickoff-slide.html) |
| **Ambient Listening Device Requirements** (mobile — iOS &amp; Android combined) | [combined](https://mtmcallen.github.io/priority-score-simulator/docs/ambient-listening-device-requirements-one-pager.html) · [iOS only](https://mtmcallen.github.io/priority-score-simulator/docs/ambient-listening-device-requirements-ios-one-pager.html) · [Android only](https://mtmcallen.github.io/priority-score-simulator/docs/ambient-listening-device-requirements-android-one-pager.html) |
| **Patient Prioritization Overview Slide** (16:9 — what it is, enablement, benefits) | [mtmcallen.github.io/priority-score-simulator/docs/patient-prioritization-kickoff-slide.html](https://mtmcallen.github.io/priority-score-simulator/docs/patient-prioritization-kickoff-slide.html) |
| **Patient Prioritization Overview Slide 2** (16:9 — overview, features, benefits + mobile screenshot) | [HTML preview](https://mtmcallen.github.io/priority-score-simulator/docs/patient-prioritization-overview-slide-2.html) · [Google Slides (editable)](https://docs.google.com/presentation/d/1xvx5HCGP3SaX28-WuNd-jT9EGI3BOgeiFOfPBqUoe_w/edit) · [PPTX source](https://mtmcallen.github.io/priority-score-simulator/docs/patient-prioritization-overview-slide-2.pptx) |
| **Patient Prioritization Device Requirements** (mobile — iOS &amp; Android combined) | [combined](https://mtmcallen.github.io/priority-score-simulator/docs/patient-prioritization-device-requirements-one-pager.html) · [iOS only](https://mtmcallen.github.io/priority-score-simulator/docs/patient-prioritization-device-requirements-ios-one-pager.html) · [Android only](https://mtmcallen.github.io/priority-score-simulator/docs/patient-prioritization-device-requirements-android-one-pager.html) |
| **Patient Prioritization Hype Flyer** (editable) | [mtmcallen.github.io/priority-score-simulator/docs/patient-prioritization-hype-flyer.html](https://mtmcallen.github.io/priority-score-simulator/docs/patient-prioritization-hype-flyer.html) |
| **Conversational AI for Voice and SMS Hype Flyer** (editable) | [mtmcallen.github.io/priority-score-simulator/docs/conversational-ai-voice-hype-flyer.html](https://mtmcallen.github.io/priority-score-simulator/docs/conversational-ai-voice-hype-flyer.html) |
| **Automated Voice Talent and Language Enhancements Hype Flyer** (editable) | [mtmcallen.github.io/priority-score-simulator/docs/automated-voice-talent-language-enhancements-hype-flyer.html](https://mtmcallen.github.io/priority-score-simulator/docs/automated-voice-talent-language-enhancements-hype-flyer.html) |
| **Ambient Listening Consent by Roundable Type** (design spec — Evolve settings, mobile modals, API) | [mtmcallen.github.io/priority-score-simulator/docs/designs/ambient-listening-consent-by-roundable-type-spec.html](https://mtmcallen.github.io/priority-score-simulator/docs/designs/ambient-listening-consent-by-roundable-type-spec.html) |
| **Ambient Listening Background Processing** (design spec — processing modal, recording bar, toasts) | [mtmcallen.github.io/priority-score-simulator/docs/designs/ambient-listening-background-processing-spec.html](https://mtmcallen.github.io/priority-score-simulator/docs/designs/ambient-listening-background-processing-spec.html) |
| **Ambient Listening Background Processing Prototype** (interactive mobile mockup — blocking vs background flow) | [mtmcallen.github.io/priority-score-simulator/docs/designs/ambient-listening-background-processing-prototype.html](https://mtmcallen.github.io/priority-score-simulator/docs/designs/ambient-listening-background-processing-prototype.html) |
| **Ambient Listening Background Processing V3 Prototype** (dev proposal — blocking modal default, Continue in background, submit blocked until done) | [mtmcallen.github.io/priority-score-simulator/docs/designs/ambient-listening-background-processing-v3-prototype.html](https://mtmcallen.github.io/priority-score-simulator/docs/designs/ambient-listening-background-processing-v3-prototype.html) |
| **Ambient Listening Consent Modal Prototype** (interactive mockup — Consent Given, Declined, No Consent Needed) | [mtmcallen.github.io/priority-score-simulator/docs/designs/ambient-listening-consent-modal-prototype.html](https://mtmcallen.github.io/priority-score-simulator/docs/designs/ambient-listening-consent-modal-prototype.html) |
| **Multi-Photo Answer Option Prototype** (interactive web mockup — Nurse Leader Rounding, multiple thumbnails per answer) | [mtmcallen.github.io/priority-score-simulator/docs/designs/answer-option-multi-photo-prototype.html](https://mtmcallen.github.io/priority-score-simulator/docs/designs/answer-option-multi-photo-prototype.html) |
| **Multi-Photo Answer Option Mobile Prototype** (interactive mobile mockup — multi-select picker, up to 10 photos per answer) | [mtmcallen.github.io/priority-score-simulator/docs/designs/answer-option-multi-photo-mobile-prototype.html](https://mtmcallen.github.io/priority-score-simulator/docs/designs/answer-option-multi-photo-mobile-prototype.html) |
| **Multi-Photo History View Prototype** (interactive mockup — view all submitted photo thumbnails on past rounds via History / Activity Feed) | [mtmcallen.github.io/priority-score-simulator/docs/designs/answer-option-multi-photo-history-prototype.html](https://mtmcallen.github.io/priority-score-simulator/docs/designs/answer-option-multi-photo-history-prototype.html) |
| **Answer Option Multi-Photo Prototype** (interactive mockup — multiple photos per answer with removable thumbnails) | [mtmcallen.github.io/priority-score-simulator/docs/designs/answer-option-multi-photo-prototype.html](https://mtmcallen.github.io/priority-score-simulator/docs/designs/answer-option-multi-photo-prototype.html) |
| **Answer Option Multi-Photo — Mobile** (iOS &amp; Android mockup — multi-select picker up to 10, Choose button top right) | [mtmcallen.github.io/priority-score-simulator/docs/designs/answer-option-multi-photo-mobile-prototype.html](https://mtmcallen.github.io/priority-score-simulator/docs/designs/answer-option-multi-photo-mobile-prototype.html) |

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
