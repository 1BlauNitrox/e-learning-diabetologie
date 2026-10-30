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

The detailed outline of chapters, topics and pop-ups is in [Content structure](#3-content-structure).

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

The content is organised in a fixed hierarchy (3.1, 3.2), which the export encodes. On top of it, learning objectives, recurring concepts, references and questions link content across chapters (3.3–3.6). The export does not encode these links; they were derived by reading the texts.

### 3.1 Outline

The content has four levels:

| Level | Source in the export | Count |
|---|---|---|
| Module | The whole export | 1 |
| Chapter | Scene; name from the navigation menu | 6 |
| Topic | Content slide; name from the tab on the chapter's *Kapitelstart* slide, otherwise from the slide heading | 18 |
| Pop-up | Slide layer shown by a button; name from the button text, otherwise from the layer content (in *italics*) | 29 |

Slide titles in `data.js` are not used as names, because many are generic or repeated (e.g. "Kapitelstart" 7×).

| No. | Chapter / topic | Pop-ups | Slide |
|---|---|---|---|
| **1** | **Wann treten Ketonkörper auf?** | | |
| 1.1 | Wann treten Ketonkörper auf? (knowledge check) | – | `5ovCLr88si4` |
| 1.2 | Was haben alle dargestellten richtigen Antworten gemeinsam? | 5 numbered buttons on a graphic: *Hungerzustand*, *Schwangerschaft*, *schwere Erkrankung bei Typ-1-Diabetes*, *Insulinmangel*, *SGLT2-Inhibitor* | `6HFIfXmkdKL` |
| **2** | **Wie entstehen Ketonkörper?** | | |
| 2.1 | Die Beteiligten am Prozess | Acetyl-CoA, Oxalacetat, Essigsäure? | `64OtgD2lzP2` |
| 2.2 | Entstehung von Ketonkörpern | Lipidstoffwechsel unter Normalbedingungen, Lipidstoffwechsel bei „Glukosemangel“ | `6oCsLqeGpqD` |
| 2.3 | Ketonkörper – was passiert damit? | Nutzung, Ausscheidung, Abbau | `6r0GXjwKtoG` |
| **3** | **Was wird wie und wann sollte gemessen werden?** | | |
| 3.1 | Verschiedene Ketonkörper | Buttons on a graphic: *ß-Hydroxybutyrat*, *Acetoacetat*, *Aceton*; Was soll gemessen werden? | `6eJKu1hLqGg` |
| 3.2 | Verschiedene Nachweisorte (Acetoacetat oder ß-OHB?) | *Störmöglichkeiten bei der Messung von Acetoacetat* | `6WUflbGCQE6` |
| 3.3 | Wann sollten Ketone gemessen werden? | Schwangerschaft, Typ1-Diabetes, Typ2-Diabetes | `6jJoqfZlha1` |
| **4** | **Beurteilung der erhobenen Werte** | | |
| 4.1 | Bewertung der Ketonkörpermessung | *Acetoacetat (Urin)*, *ß-Hydroxybutyrat (Serum)* | `5cxhcjlTRsl` |
| **5** | **Maßnahmen** | | |
| 5.1 | Weitere Diagnostik | *Azidose bei Ketose*, *Laktatazidose* | `6TJqN3miGya` |
| 5.2 | Hungerketose | Indikation zur Messung in der Schwangerschaft, Behandlung eines positiven Nachweises, Schaden Ketonkörper in der Schwangerschaft? | `69WCCUPGrf8` |
| 5.3 | Diabetische Ketoazidose | – | `65FhOzjnfyC` |
| 5.4 | Ketose unter Therapie mit SGLT2-Inhibitoren | *Maßnahmen bei Verdacht* | `6RoGrExUjsT` |
| **6** | **Patientenschulung zum Thema Ketoazidose** | | |
| 6.1 | Kursübersicht | – | `5yPBrxMp2OF` |
| 6.2 | Ketoazidose verstehen | – | `61MshZFG2hx` |
| 6.3 | Risikofaktoren kennen, Ketoazidose erkennen | – | `5wCsNDPjQg7` |
| 6.4 | Ketoazidose behandeln | – | `5h1vmZbo2CA` |
| 6.5 | Der persönliche Plan | – | `5ybdvscaQS3` |

Chapters 1–5 explain medical content in text. Chapter 6 differs: it presents a patient education course. Its slide text holds only agenda items (e.g. "Übersäuerung des Blutes", "Insulin spritzen"), while the explanations are in 16 images of the course slides (see [5.3](#53-findings)).

Outside the hierarchy, the module has:

- **Frame:** title slide, learning objectives, *Übersicht* (scene 1); Impressum and *Hinweise zum Lernen* (scene 2); *Abschluss* (scene 10).
- **Questions:** the knowledge check in topic 1.1 and the quiz with 10 questions (scene 9), see [3.6](#36-questions).
- **Navigation slides:** one *Kapitelstart* per chapter, with only navigation hints and, in chapters 2, 3, 5 and 6, the tabs to the topics.

Together with the excluded scene 11 (see [3.7](#37-unreachable-and-duplicated-content)) this accounts for all 44 slides.

### 3.2 Navigation

- The *Übersicht* slide is a hub. It links to the *Kapitelstart* slide of every chapter, the quiz and the *Abschluss*. Every chapter returns to it at the end.
- Within a chapter, the topics are reached in order or through the tabs on the *Kapitelstart* slide.
- Scene 2 is not linked from any slide. It is opened by the player button "Informationen". A second player button leads to the *Übersicht*.
- Besides the 29 content pop-ups, the module has 27 feedback layers (knowledge check and quiz) and 4 excluded layers (see [3.7](#37-unreachable-and-duplicated-content)), 60 layers in total.

### 3.3 Learning objectives

The learning objectives slide lists five objectives. The export does not link them to content. By content they map as follows:

| # | Objective (shortened) | Topics | Quiz |
|---|---|---|---|
| 1 | Herkunft der Ketonkörper aus dem Lipidstoffwechsel | 1.2, 2.1, 2.2 | 1, 7, 9 |
| 2 | Mechanismen der Entstehung benennen | 1.1, 1.2, 2.2, 2.3 | 6, 7, 9 |
| 3 | Diagnostik veranlassen und Befunde interpretieren | 3.3, 4.1, 5.1 | 2, 3, 8, 10 |
| 4 | Unterschied Ketonkörper im Blut und im Urin | 3.1, 3.2, 4.1 | 5 |
| 5 | Anlassbezogene Behandlung entwickeln | 5.2, 5.3, 5.4, 6.4, 6.5 | 4 |

No objective names patient education. Chapter 6 is covered only by objective 5, through its treatment topics.

### 3.4 Recurring concepts

Several concepts run through multiple chapters and connect them by meaning:

| Concept | Topics |
|---|---|
| **Situations that cause ketosis**: fasting in pregnancy, prolonged fasting, severe illness in type 1 diabetes, SGLT2 inhibitors in type 2 diabetes, insulin deficiency | Introduced in 1.1, 1.2 → when to measure in 3.3 → measures in 5.2, 5.3, 5.4 → risk factors in 6.3 |
| **The three ketone bodies**: acetoacetate, ß-hydroxybutyrate (ß-OHB), acetone | Formation and fate in 2.2, 2.3 → share and measurement site (urine, serum, breath) in 3.1, 3.2 → assessment scales in 4.1 |
| **Mechanism**: glucose deficiency → less oxaloacetate → acetyl-CoA cannot enter the citric acid cycle → ketone bodies | Short form in 1.2 → full form in 2.1, 2.2 → reversed as the principle of breakdown in 2.3 and of treatment in 5.3 |
| **SGLT2 inhibitors** | Situation in 1.2 → urine test not representative in 3.1, 3.2; measure from about 200 mg/dl in 3.3 → caution with a negative urine result in 4.1 → measures in 5.4 → patient education in 6.2–6.4 |
| **Severity grades** (thresholds for serum and urine) | Defined in 4.1 → further diagnostics in 5.1 → patient education in 6.2 |
| **Pregnancy** | Situation in 1.2 → morning measurement in 3.3 → *Hungerketose* in 5.2 |

### 3.5 Explicit references

| From | Text | To |
|---|---|---|
| 1.2 | "Wie Ketonkörper entstehen, sehen Sie im nächsten Kapitel" | Chapter 2 |
| 3.1, pop-up *Acetoacetat* | "Achtung unter Therapie mit SGLT2-Hemmern! (siehe nächstes Chart)" | 3.2 |
| 5.1, pop-up *Azidose bei Ketose* | Pathogenesis "wie sie in diesem E-Learning-Modul dargestellt ist" | Chapter 2 |
| 5.2 | "siehe auch E-Learning-Modul „Stoffwechsel in der Schwangerschaft“" | Another module (not delivered) |
| 3.1, pop-up *Was soll gemessen werden?* | Quote with source: ADA Position Statement, Diabetes Care 2004 | External literature |
| Learning objectives slide | Author information and notes via "Informationen" | Scene 2 |

### 3.6 Questions

- **Knowledge check** (1.1, "In welchen Situationen können Ketonkörper auftreten?"): multiple response, tracked, not part of the quiz. Topic 1.2 explains the answers.
- **Quiz** (scene 9): 10 questions, 10 points each, pass mark 70 %. Types: multiple response (1, 3, 4, 6, 10), drag-and-drop matching (2, 5, 8, 9), sequence (7).

The export defines the correct answers but not which content a question tests. By content:

| Question | Topic of the question | Tested topics |
|---|---|---|
| 1 | Which terms denote ketone bodies? | 2.2, 3.1 |
| 2 | Match patient cases to findings | 1.2, 4.1 |
| 3 | Data needed to judge the severity of a derailment | 4.1 |
| 4 | Urgent measures in ketoacidosis | 5.3 |
| 5 | Properties of acetoacetate vs ß-OHB | 3.2, 4.1 |
| 6 | When can ketone bodies form? | 1.1, 1.2 |
| 7 | Order the steps leading to fasting ketosis | 1.2, 2.2 |
| 8 | Lactate vs ß-OHB in metabolic acidosis | 5.1 |
| 9 | Place the substances in the metabolic diagram | 2.2 (same diagram) |
| 10 | When should ketone bodies be measured? | 3.3, 5.2 |

Chapters 1–5 are tested by three questions each, chapter 6 by none. 8 of the 18 topics are not tested by any question: 2.1, 2.3, 5.4 and all of chapter 6.

### 3.7 Unreachable and duplicated content

| Content | Finding | Handling |
|---|---|---|
| Scene 11 *Hungerketose* | Older variant of topic 5.2 with partly different wording and 1 pop-up; no slide links to it, only a second "Maßnahmen" entry in the menu | Exclude |
| 3 layers in 6.3, 6.4, 6.5 | Never shown by any trigger; their texts are copies of pop-ups in 5.2 and 5.4 | Exclude |
| *Abschluss* | Closing text with the author's e-mail address | Exclude the address |

The extraction should therefore follow the triggers rather than take every layer in a slide file.

### 3.8 Conclusion

- **The hierarchy can be read from the export.** Chapters, topics and pop-ups with their names follow from the menu, the *Kapitelstart* tabs and the triggers. Every text can be traced to a slide ID and a layer ID.
- **The topic is the central unit.** Learning objectives, concepts and questions all map to topics, so topics are the natural anchor for content, provenance and question generation.
- **The cross-links have to be created by us.** Objectives, recurring concepts and question-to-topic links are not in the export. The mappings in 3.3–3.6 can serve as a first reference to check the pipeline against.
- **Recurring concepts are the main candidates for content nodes** in the knowledge graph, and the hierarchy for structural nodes.

How these findings are modelled is decided in the canonical document model (#14) and the knowledge graph schema (#6).

## 4. Technical format

This section describes the primary source as far as the extraction needs it. Paths are relative to `Ketonkörper/`.

### 4.1 Files

Every file in `html5/data/js/` is a JavaScript call with a JSON payload:

```js
window.globalProvideData('slide', '{"title":"Ketonkörper – was passiert mit ihnen?", ...}');
```

The payload is a JavaScript string literal (UTF-8 with BOM). It has to be unescaped as a string literal before it can be parsed as JSON; parsing it directly fails on escapes such as `\'`.

| File | Type | Content | Use |
|---|---|---|---|
| `html5/data/js/data.js` | `data` | Scenes and slide order, `slideMap` (links and image IDs per slide), `quizzes`, question definitions (`interactions`), `assetLib` (image files), player events | Structure, questions |
| `html5/data/js/<slide-id>.js` | `slide` | Layers, objects, texts and triggers of one slide | Content |
| `story_content/frame.xml` | XML | Navigation menu as nested `slidelink` elements with `displaytext` and `slideid` | Chapter names |
| `html5/data/js/paths.js` | `paths` | Rendered vector shapes, including every text as positioned glyph runs | Ignore: all its text is also in the slide files |
| `html5/data/js/frame.js` | `frame` | Player layout and UI strings | Ignore |

**IDs.** Scenes, slides, layers and objects have random 11-character IDs. References use paths such as `_player.<scene-id>.<slide-id>` for slides and `_parent.<layer-id>` for layers. Scene, slide, layer and object IDs stayed the same in the republished Review 360 version, so they are usable as provenance. Some internal IDs (answer IDs, text library IDs) changed.

### 4.2 Slides, layers and objects

```
slide
└─ slideLayers[]                 first = base layer, others = pop-ups and feedback
   └─ objects[]                  nested through objgroup, stategroup, scrollarea, shufflegroup
      ├─ textLib[].vartext.blocks[].spans[].text      text: block = paragraph, span = formatting run
      ├─ data.vectorData.altText                      accessibility text
      ├─ data.imagedata.assetId                       image → assetLib[assetId].url
      └─ events[].actions[]                           triggers
```

- **Objects** across all slides: 1,080 `vectorshape` (text boxes, shapes, buttons, images), 118 `stategroup` (buttons with states), 12 `objgroup`, 8 `scrollarea`, 7 `shufflegroup` (quiz answers). Objects carry their position and size.
- **Text** is taken from `vartext`. `altText` mostly repeats the visible text. For images it holds a description or a file name (e.g. `Chemical_structural_formula_of_acetic_acid.svg`).
- **Order:** objects are stored in layering order, which is not always the reading order. The positions allow sorting top to bottom.

Text quirks the extraction has to handle:

| Quirk | Example | Handling |
|---|---|---|
| `^%^` encodes `%` (22 occurrences) | `Acetoacetat (Anteil etwa 20^%^)` | Replace with `%` |
| Line breaks as `\n` and `\r`, layout with tabs | `Bis 0,6 mmol/l\t\tNormalbefund` | Normalize; tabs mark table-like rows |
| Button labels with an instruction | `Nutzung - Hier klicken -` | Strip the instruction |
| Boilerplate on many slides | `Diabetologie online lernen \| Ketonkörper`, `Weiter`, `Zum Schließen klicken`, `Alle Bilder © articulate` | Drop |

### 4.3 Triggers

A pop-up is opened by an event on a button object:

```json
"events": [{"kind": "onrelease", "actions": [
  {"kind": "show_slidelayer", "objRef": {"type": "string", "value": "_parent.6QSSoACHHWX"}}]}]
```

- The button is either a `vectorshape` with a text label or a `stategroup` without a label (e.g. numbered buttons on a graphic, see 3.1).
- Quiz feedback layers are shown by the action group `ActGrpOnSubmitButtonClick`, depending on the answer status.
- A layer that no `show_slidelayer` action references is never shown (see [3.7](#37-unreachable-and-duplicated-content)).
- Jumps between slides are `gotoplay` actions. `slideMap.linksTo` in `data.js` summarizes them per slide.
- The player buttons "Informationen" and "Übersicht" are defined in the `events` of `data.js`.

### 4.4 Questions

Questions are defined in `data.js` under `scenes[].slides[].interactions[]`; the question text itself is on the slide. Quiz settings (pass mark 70 %, partial scoring, list of question slides) are in `quizzes[]`.

| Field | Content |
|---|---|
| `type` | `multipleresponse`, `matching` or `sequence` |
| `choices[]` | Answer options with `id` and `lmstext` |
| `answers[]` | One `correct` and one `incorrect` answer with `points`; the correct one defines the solution in `evaluate.statements` |

How the solution is encoded depends on the type:

- **Multiple response:** the statements list the choices that must be selected.
- **Matching:** each statement pairs a choice (drag item) with a `statementid` (drop target). The target is an object in the slide file whose ID follows the `statement_` prefix, and its text is the matched item. Drag items carry an LMS prefix such as `Text-feld 3 - Nachweis im Urin`, which is stripped. In question 9 the targets are unlabelled boxes in a diagram ("Rechteck 1–4"), so the solution only makes sense with the image.
- **Sequence:** the order of the statements is the correct order of the choices.

Most feedback layers are generic ("Richtig", "Falsch"). Questions 8 and 9 add an explanation or show the solution.

### 4.5 Navigation menu

`story_content/frame.xml` holds the menu under `nav_data/outline/links`. Each `slidelink` has a `displaytext` (with `&#xD;` line breaks) and a `slideid` in the form `_player.<scene-id>.<slide-id>`; nesting gives the menu levels.

### 4.6 Implications for the extraction

- Read `data.js`, the slide files and `frame.xml`. `paths.js` and `frame.js` add no content.
- Take text from `vartext`, and `altText` only for images.
- Follow the triggers: content pop-ups are layers referenced by `show_slidelayer`; unreferenced layers are skipped.
- Clean the quirks in 4.2 and drop boilerplate.
- Keep slide ID, layer ID and object ID with every text as provenance.
- Resolve matching solutions through the drop-target objects on the slide.

## 5. Media

This section records which media exist and where they appear. Their content and how we use them are decided later.

The module has **no video and no audio** (`meta.xml`: `totalvideo="0"`, `totalaudio="0"`). It has 54 images: 49 raster files in `mobile/`, 4 SVG files (stored as `story_content/*.js`) and 1 player background pattern. Every image is listed in `assetLib` and placed on a slide through `imagelib[].assetId` (see [4.2](#42-slides-layers-and-objects)); its `altText` is mostly the original file name (e.g. `hunger Foto 1.jpg`). Besides these, `story_content/` holds the module thumbnail and the icon for the handout download.

### 5.1 Types

| Type | Count | Contains text |
|---|---|---|
| Slides of a patient education course ("KetoAWARE") | 16 | Yes: headings, bullet lists, tables |
| Screenshots of the module itself (solutions, closing slide) | 4 | Yes |
| Photos (situations, devices, clinic) | 13 | Partly: product labels on the meter and test strip photos |
| Chemical structural formulas | 6 | Formulas only |
| Schematic drawings (organs, fat cells, light bulb) | 8 | No |
| Diagram (SVG) | 1 | Not checked |
| Text placeholders (`txt__default_*`) | 5 | No: empty frames used as drop zones and layout |
| Player background pattern | 1 | No |

### 5.2 Positions

| Position | Layer | Images |
|---|---|---|
| Title slide | base | 3 structural formulas (ß-OHB, acetoacetate, acetone) |
| Übersicht | base | Player background pattern (3×) |
| Impressum | base | Portrait photo of the author |
| Hinweise zum Lernen | base | 1 text placeholder |
| 1.1 | base | 6 photos, one per answer option of the knowledge check |
| 1.1 | feedback "Das sind die richtigen Antworten" | 1 screenshot of the solved knowledge check |
| 2.1 | pop-ups Acetyl-CoA, Oxalacetat, Essigsäure? | 1 structural formula each (SVG) |
| 2.2 | base | 2 drawings (liver, fat cells) as part of the metabolism diagram |
| 2.3 | pop-up Nutzung | 2 drawings (muscle, brain) |
| 3.1 | base | 1 diagram (SVG) |
| 3.1 | pop-ups *ß-Hydroxybutyrat*, *Acetoacetat*, *Aceton* | 1 drawing (blood drop, kidney, lungs) and 1 structural formula each |
| 3.2 | base | 2 photos (blood ketone meter, urine test strips) |
| 5.1 | base | 1 photo (laboratory) |
| 5.3 | base | 2 photos (intensive care) |
| 5.4 | base | 1 drawing (light bulb) |
| 6.1 | base | 2 course slides |
| 6.2 | base | 4 course slides |
| 6.3 | base | 4 course slides |
| 6.4 | base | 5 course slides |
| 6.5 | base | 1 course slide |
| Quiz question 5 | solution layer | 1 screenshot of the solution |
| Quiz question 9 | base | 2 drawings (liver, fat cells; reused from 2.2) and 4 text placeholders as drop zones |
| Quiz question 9 | layer "Hier gehts zur richtigen Antwort" | 1 screenshot of the solution |
| Abschluss | base | 1 photo (laptop) and 1 screenshot of topic 2.2 |

### 5.3 Findings

- **Chapter 6 exists mainly as images.** Its 16 course slides carry the actual content of the patient education chapter. The slide text only holds the headings and agenda items (see [3.1](#31-outline)). Without the images, chapter 6 is almost empty.
- **Some content depends on images.** The metabolism diagram in 2.2 and quiz question 9 combine drawings with text boxes. The solutions of the knowledge check and of quiz questions 5 and 9 are shown as screenshots; the same solutions are also defined as data in `data.js` (see [4.4](#44-questions)).
- **Images are reused.** The structural formulas appear on the title slide and in 3.1, and the liver and fat cell drawings appear in 2.2 and quiz question 9.
- **The photos illustrate** and do not add information, apart from the product labels in 3.2.
