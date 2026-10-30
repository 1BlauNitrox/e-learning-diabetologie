# 0003 – Data Analysis

> **Data storage:** The university Dropbox is the single source of truth for the raw data. Every team member keeps a local copy in `data/raw/`, which is git-ignored, so scripts and docs use the same relative paths for everyone and nothing is published.

## 1. Overview

We received one module of the website *Diabetologie online lernen*: **Ketonkörper**, in German, 44 slides, published on 2026-09-08 with Articulate Storyline 3. The delivery also contains a PDF handout and links to two modules on Articulate Review 360. The first design and implementation of the pipeline uses only this module; further modules may be added later to scale it. All paths below are relative to `data/raw/2026 E-Learning Diabetologie/`.

### Delivered files

| Source | Size | Content | Use |
|---|---|---|---|
| `Ketonkörper/` | 26 MB, 120 files | Storyline HTML5 export of the module | Primary content |
| `Handout-Ketonkörper.pdf` | 4.2 MB, 12 pages | Printed with "Microsoft Print to PDF": 23 images and almost no extractable text | See [Source selection](#2-source-selection) |
| `Ketonkörper _ Review 360.webloc` | Link | Review 360 page of the same module | See [Source selection](#2-source-selection) |
| `Blutzuckermessung in Klinik und Praxis _ Review 360.webloc` | Link | Review 360 page of a second module; we have no export of it | Out of scope, see [Source selection](#2-source-selection) |
| `wetransfer_e-learning_2026-09-08_1658.zip` | 26 MB | Byte-for-byte identical to `Ketonkörper/` | Ignore |
| `Ketonkörper/story_content/external_files/Handout-Ketonkörper.pdf` | 4.2 MB | Identical to `Handout-Ketonkörper.pdf` (same MD5); offered as a download inside the module | Ignore |
| `.DS_Store` | | macOS system file | Ignore |

### Contents of the Storyline export

| Path | Content | Use |
|---|---|---|
| `html5/data/js/data.js` | Course structure: scenes, slides, their order, the quiz definition, variables | Structure |
| `html5/data/js/<slide-id>.js` (44 files) | Content of one slide each. File names are random IDs, which are resolved through `data.js`. | Content |
| `story_content/frame.xml` | Player configuration, including the navigation menu (25 entries with chapter titles) | Structure |
| `mobile/` (49 images) | Images and graphics shown on the slides | See [Media](#5-media) |
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

## 2. Source selection

| Source | Complete | Machine-readable | Decision |
|---|---|---|---|
| Storyline export: `data.js` and the 44 slide files | Yes: all text including pop-up layers, the structure and the quiz | Yes: JSON wrapped in JavaScript | **Primary source** |
| `mobile/` images | Not a slide source: images used inside slides | No | Existence and position recorded, see [Media](#5-media) |
| PDF handout | No: screenshots of 23 of the 44 slides; no quiz, Impressum or patient education | No: text only via OCR | Not used |
| Review 360, Ketonkörper | Same content as the export, newer publish | Yes | Not used, see below |
| Review 360, Blutzuckermessung | Same template and format | Yes | Out of scope |

- **Export over handout:** Terms that appear in the handout images, including those in pop-up layers (e.g. "Penicillamin", "osmotische Diurese", "accelerated starvation", "ADA Position"), are all present as text in the export. The handout adds no content.
- **Version:** The Review 360 page of Ketonkörper is a newer publish (2026-09-15, project ID `6RKvklppYka`) than our export (2026-09-08, `63XwQxu12fb`). A comparison of all slide files, `data.js` and `paths.js` shows the same slides, texts, quiz, navigation and image references. The only differences are the version label on the title slide (`V07/2026` in the export, `V09/2026` on Review 360), the quiz resume dialog in player scene 0 (only in the export) and IDs regenerated on publishing. Image files were not compared byte by byte. **We use the local export.**
- **Other modules:** Blutzuckermessung uses the same Storyline template (`DiabetesDE_Template_360u22_20190111`) and export format. A pipeline built on this format should therefore carry over to further modules. Nothing was downloaded from Review 360.

## 3. Content structure

The module connects its content in two ways: through **navigation** (which slide leads to which) and through **meaning** (which objectives, concepts and questions refer to which content). The export only encodes the first. The second is derived here by reading the texts and will have to be modelled by us.

### 3.1 Navigation

The module is built as a hub. The *Übersicht* slide links to the start slide of every chapter, and every chapter returns to it at the end.

```
Title → Learning objectives → Übersicht (hub)
                                ├─ Ch. 1  Wann treten Ketonkörper auf?                      (scene 3)
                                ├─ Ch. 2  Wie entstehen Ketonkörper?                        (scene 4)
                                ├─ Ch. 3  Was wird wie und wann sollte gemessen werden?     (scene 5)
                                ├─ Ch. 4  Beurteilung der erhobenen Werte                   (scene 6)
                                ├─ Ch. 5  Maßnahmen                                         (scene 7)
                                ├─ Ch. 6  Patientenschulung zum Thema                       (scene 8)
                                ├─ Quiz                                                     (scene 9)
                                └─ Abschluss                                                (scene 10)
```

| Chapter | Slides | Sub-topics | Content pop-ups |
|---|---|---|---|
| Ch. 1 | 3 | Knowledge check, explanation of the situations | 5 |
| Ch. 2 | 4 | Beteiligte, Entstehung, was passiert mit ihnen | 8 |
| Ch. 3 | 4 | Verschiedene Ketonkörper, Nachweisorte, wann messen | 8 |
| Ch. 4 | 2 | Bewertung der Messung | 2 |
| Ch. 5 | 5 | Weitere Diagnostik, Hungerketose, diabetische Ketoazidose, SGLT2-Inhibitoren | 6 |
| Ch. 6 | 6 | Kursübersicht, Ketoazidose verstehen, Risikofaktoren und erkennen, behandeln, persönlicher Plan | 0 |

- Each chapter starts with a *Kapitelstart* slide that holds only navigation hints and, in Ch. 2, 3, 5 and 6, tabs to the sub-topics. These slides have no learning content.
- A large part of the medical detail sits in **pop-up layers** ("Hier klicken") on top of a slide. In total the module has 60 layers: 29 content pop-ups, 27 feedback layers of the knowledge check and quiz, and 4 excluded layers: 3 that are never shown in Ch. 6 and 1 on scene 11 (see [3.7](#37-unreachable-and-duplicated-content)).
- Scene 2 (Impressum, Hinweise) is not linked from any slide. It is opened by the player button "Informationen". A second player button leads to the Übersicht.
- The navigation menu (`frame.xml`) lists the chapters, the sub-topic slides of Ch. 2, the quiz questions and the Abschluss.

### 3.2 Chapter and slide titles

Titles exist in three places and do not agree:

| Source | Example |
|---|---|
| Slide title in `data.js` | Generic or repeated: "Kapitelstart" (7×), "Acetoacetat oder ß-OHB ? /1" (2×), "Entstehung von Ketonkörpern" in Ch. 2 and Ch. 3, "Weitere Maßnahmen" for the sub-topic "Weitere Diagnostik" |
| Navigation menu in `frame.xml` | "Was wird wie und wann sollte gemessen werden?", "Beurteilung der erhobenen Werte" |
| Text on the Übersicht slide | "Was kann wie und wann sollte gemessen werden?", "Beurteilung der Werte" |

Chapter names are taken from the navigation menu. Slide names come from the heading text on the slide, with the `data.js` title as a fallback.

### 3.3 Learning objectives

The learning objectives slide lists five objectives. None of them is linked to content in the export. By content they map as follows:

| # | Objective (shortened) | Content | Quiz |
|---|---|---|---|
| 1 | Herkunft der Ketonkörper aus dem Lipidstoffwechsel | Ch. 1 explanation slide; Ch. 2 Beteiligte, Entstehung | 1, 7, 9 |
| 2 | Mechanismen der Entstehung benennen | Ch. 1 situations and explanation; Ch. 2 Entstehung, was passiert mit ihnen | 6, 7, 9 |
| 3 | Diagnostik veranlassen und Befunde interpretieren | Ch. 3 wann messen; Ch. 4 Bewertung; Ch. 5 Weitere Diagnostik | 2, 3, 8, 10 |
| 4 | Unterschied Ketonkörper im Blut und im Urin | Ch. 3 Ketonkörper, Acetoacetat oder ß-OHB; Ch. 4 Bewertung | 5 |
| 5 | Anlassbezogene Behandlung entwickeln | Ch. 5 Hungerketose, diabetische Ketoazidose, SGLT2-Inhibitoren; Ch. 6 behandeln, persönlicher Plan | 4 |

Ch. 6 is not named by any objective. It outlines a patient education course on ketoacidosis (agenda items rather than explained content) and is the only chapter without a quiz question.

### 3.4 Recurring concepts

Several concepts run through multiple chapters. They connect the chapters by meaning and are the main candidates for nodes and relations in the knowledge graph.

| Concept | Where it appears |
|---|---|
| **Situations that cause ketosis**: fasting in pregnancy, prolonged fasting, severe illness in type 1 diabetes, SGLT2 inhibitors in type 2 diabetes, insulin deficiency | Introduced in Ch. 1 → when to measure per group in Ch. 3 → measures per situation in Ch. 5 → risk factors in Ch. 6 |
| **The three ketone bodies**: acetoacetate, ß-hydroxybutyrate (ß-OHB), acetone | Formation and fate in Ch. 2 → share and measurement site (urine, serum, breath) in Ch. 3 → assessment scales in Ch. 4 |
| **Mechanism**: glucose deficiency → less oxaloacetate → acetyl-CoA cannot enter the citric acid cycle → ketone bodies | Short form in Ch. 1 → full form in Ch. 2 → reversed as the principle of breakdown and treatment in Ch. 2 and Ch. 5 |
| **SGLT2 inhibitors** | Situation in Ch. 1 → urine test not representative, measure from about 200 mg/dl in Ch. 3 → "Cave" for a negative urine result in Ch. 4 → own measures slide in Ch. 5 → risk factor and euglycaemic ketoacidosis in Ch. 6 |
| **Severity grades** (thresholds for serum and urine) | Defined in Ch. 4 → above 3 mmol/l a medical emergency for the hospital; treatment in Ch. 5; mentioned in Ch. 6 |
| **Pregnancy** | Situation in Ch. 1 → morning measurement in Ch. 3 → Hungerketose in Ch. 5 |

### 3.5 Explicit references in the text

| From | Text | To |
|---|---|---|
| Ch. 1, explanation slide | "Wie Ketonkörper entstehen, sehen Sie im nächsten Kapitel" | Ch. 2 |
| Ch. 3, Ketonkörper, urine pop-up | "Achtung unter Therapie mit SGLT2-Hemmern! (siehe nächstes Chart)" | Ch. 3, Acetoacetat oder ß-OHB |
| Ch. 5, Weitere Diagnostik, pop-up | Pathogenesis "wie sie in diesem E-Learning-Modul dargestellt ist" | Ch. 2 |
| Ch. 5, diabetische Ketoazidose | The measures also count as treatment of ketosis | Ch. 5 in general |
| Ch. 5, Hungerketose | "siehe auch E-Learning-Modul „Stoffwechsel in der Schwangerschaft“" | Another module (not delivered) |
| Ch. 3, Ketonkörper, pop-up | Quote with source: ADA Position Statement, Diabetes Care 2004 | External literature |
| Learning objectives slide | Author information and notes via "Informationen" | Scene 2 |

### 3.6 Questions and the content they test

The module contains one knowledge check and one quiz. The export defines the correct answers but not which content a question tests. The mapping below is derived from the question texts.

- **Knowledge check** (Ch. 1, "In welchen Situationen können Ketonkörper auftreten?"): multiple response, tracked, not part of the quiz. The following slide explains the answers.
- **Quiz** (scene 9): 10 questions, 10 points each, pass mark 70 %. Types: multiple response (1, 3, 4, 6, 10), drag-and-drop matching (2, 5, 8, 9), sequence (7).

| Question | Topic | Tested content |
|---|---|---|
| 1 | Which terms denote ketone bodies? | Ch. 2 Entstehung; Ch. 3 Ketonkörper |
| 2 | Match patient cases to findings | Ch. 1 situations; Ch. 4 Bewertung |
| 3 | Data needed to judge the severity of a derailment | Ch. 4 Bewertung |
| 4 | Urgent measures in ketoacidosis | Ch. 5 diabetische Ketoazidose |
| 5 | Properties of acetoacetate vs ß-OHB | Ch. 3 Acetoacetat oder ß-OHB; Ch. 4 Bewertung |
| 6 | When can ketone bodies form? | Ch. 1 |
| 7 | Order the steps leading to fasting ketosis | Ch. 1 explanation slide; Ch. 2 Entstehung |
| 8 | Lactate vs ß-OHB in metabolic acidosis | Ch. 5 Weitere Diagnostik |
| 9 | Place the substances in the metabolic diagram | Ch. 2 Entstehung (same diagram) |
| 10 | When should ketone bodies be measured? | Ch. 3 wann messen; Ch. 5 Hungerketose |

Questions per chapter (a question can test more than one): Ch. 1: 3, Ch. 2: 3, Ch. 3: 3, Ch. 4: 3, Ch. 5: 3, Ch. 6: 0.

### 3.7 Unreachable and duplicated content

Some content is in the export but cannot be reached by a learner, or exists more than once:

| Content | Finding | Handling |
|---|---|---|
| Scene 11 "Hungerketose" | Older variant of the Ch. 5 Hungerketose slide with partly different wording; no slide links to it, only a second "Maßnahmen" entry in the menu | Exclude |
| 3 pop-up layers in Ch. 6 (Risikofaktoren, behandeln, persönlicher Plan) | Never shown by any trigger; their texts are copies of the Ch. 5 pregnancy and SGLT2 pop-ups | Exclude |
| Scene 10 "Abschluss" | Closing text with the author's e-mail address | Exclude the address |

The extraction should therefore follow the triggers rather than take every layer in a slide file.
