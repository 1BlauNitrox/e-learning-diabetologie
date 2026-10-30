# 0003 – Data Analysis

> **Data storage:** The university Dropbox is the single source of truth for the raw data. Every team member keeps a local copy in `data/raw/`, which is git-ignored, so scripts and docs use the same relative paths for everyone and nothing is published.

## 1. Overview

We received one module of the website *Diabetologie online lernen*: **Ketonkörper**, in German, 44 slides, published on 2026-09-08 with Articulate Storyline 3. The delivery also contains a PDF handout and links to two modules on Articulate Review 360. All paths below are relative to `data/raw/2026 E-Learning Diabetologie/`.

### Delivered files

| Source | Size | Content | Use |
|---|---|---|---|
| `Ketonkörper/` | 26 MB, 120 files | Storyline HTML5 export of the module | Primary content |
| `Handout-Ketonkörper.pdf` | 4.2 MB, 12 pages | Printed with "Microsoft Print to PDF": 23 images and almost no extractable text | See [Source selection](#2-source-selection) |
| `Ketonkörper _ Review 360.webloc` | Link | Review 360 page of the same module | See [Source selection](#2-source-selection) |
| `Blutzuckermessung in Klinik und Praxis _ Review 360.webloc` | Link | Review 360 page of a second module; we have no export of it | See [Source selection](#2-source-selection) |
| `wetransfer_e-learning_2026-09-08_1658.zip` | 26 MB | Byte-for-byte identical to `Ketonkörper/` | Ignore |
| `Ketonkörper/story_content/external_files/Handout-Ketonkörper.pdf` | 4.2 MB | Identical to `Handout-Ketonkörper.pdf` (same MD5); offered as a download inside the module | Ignore |
| `.DS_Store` | | macOS system file | Ignore |

### Contents of the Storyline export

| Path | Content | Use |
|---|---|---|
| `html5/data/js/data.js` | Course structure: scenes, slides, their order, the quiz definition, variables | Structure |
| `html5/data/js/<slide-id>.js` (44 files) | Content of one slide each. File names are random IDs, which are resolved through `data.js`. | Content |
| `story_content/frame.xml` | Player configuration, including the navigation menu (25 entries with chapter titles) | Structure |
| `mobile/` (49 images) | Images and graphics shown on the slides | See [Content only in images](#5-content-only-in-images) |
| `meta.xml` | Title, author, publish date, slide count, Storyline version | Provenance |
| `story.html` | Entry point for viewing the module in a browser | Manual verification |
| `html5/lib/`, `html5/data/css/`, `analytics-frame.html`, `story_content/*.js` | Storyline player runtime, styles, fonts, tracking | Ignore |

`meta.xml` refers to `mobile/data.json`, `mobile/data.gz` and `story_content/data.swf`. None of these files exist in the export.

### Module outline

`data.js` defines 12 scenes. Scene 0 is a system scene for player dialogs ("Fortsetzen", "Warnung"). The other 11 scenes contain the 44 slides:

| Scene | Topic | Slides |
|---|---|---|
| 1 | Introduction: title, learning objectives, overview | 3 |
| 2 | Impressum and notes on learning with the module | 2 |
| 3 | When do ketone bodies occur? | 3 |
| 4 | Formation of ketone bodies: substances involved, formation, breakdown | 4 |
| 5 | Measurement: acetoacetate or β-OHB? | 4 |
| 6 | Assessment of measured values | 2 |
| 7 | Measures: fasting ketosis, diabetic ketoacidosis, ketosis under SGLT2 inhibitors | 5 |
| 8 | Patient education: understanding, recognizing and treating ketoacidosis; the personal plan | 6 |
| 9 | Quiz: 10 questions and a result slide | 13 |
| 10 | "Folie ohne Titel" | 1 |
| 11 | "Hungerketose" | 1 |

How scenes 10 and 11 are reached, and how the menu chapters map to the scenes, is described in [Content structure](#3-content-structure).
