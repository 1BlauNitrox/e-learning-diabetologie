# 0003 – Data Analysis

> **Data storage:** The university Dropbox is the single source of truth for the raw data. Every team member keeps a local copy in `data/raw/`, which is git-ignored, so scripts and docs use the same relative paths for everyone and nothing is published.

## 1. Overview

We received one module of the website *Diabetologie online lernen*: **Ketonkörper**, in German, 44 slides, published on 2026-09-08 with Articulate Storyline 3. The delivery also contains a PDF handout and links to two modules on Articulate Review 360. The first design and implementation of the pipeline uses only this module. All paths below are relative to `data/raw/2026 E-Learning Diabetologie/`.

### Delivered files

| Source | Size | Content |
|---|---|---|
| `Ketonkörper/` | 26 MB, 120 files | Storyline HTML5 export of the module (files see [4.1](#41-files), outline see [3.1](#31-outline)) |
| `Handout-Ketonkörper.pdf` | 4.2 MB, 12 pages | Printed with "Microsoft Print to PDF": 23 images and almost no extractable text |
| `Ketonkörper _ Review 360.webloc` | Link | Review 360 page of the same module |
| `Blutzuckermessung in Klinik und Praxis _ Review 360.webloc` | Link | Review 360 page of a second module; we have no export of it |
| `wetransfer_e-learning_2026-09-08_1658.zip` | 26 MB | Byte-for-byte identical to `Ketonkörper/` |
| `Ketonkörper/story_content/external_files/Handout-Ketonkörper.pdf` | 4.2 MB | Identical to `Handout-Ketonkörper.pdf` (same MD5); offered as a download inside the module |

## 2. Source selection

| Source | Complete | Machine-readable | Decision |
|---|---|---|---|
| Storyline export: `data.js` and the 44 slide files | Yes: all text including pop-up layers, the structure and the quiz | Yes: JSON wrapped in JavaScript | **Primary source** |
| `mobile/` images | Not a slide source: images used inside slides | No | Existence and position recorded, see [Media](#5-media) |
| PDF handout | No: screenshots of 23 of the 44 slides; no quiz, Impressum or patient education | No: text only via OCR | Not used |
| Review 360, Ketonkörper | Same content as the export, newer publish | Yes | Not used, see below |
| Review 360, Blutzuckermessung | Same template and format | Yes | Out of scope |

- **Duplicates:** The zip file and the handout inside the export are identical copies and are not used.
- **Export over handout:** Terms that appear in the handout images, including those in pop-up layers (e.g. "Penicillamin", "osmotische Diurese", "accelerated starvation", "ADA Position"), are all present as text in the export. The handout adds no content.
- **Version:** The Review 360 page of Ketonkörper is a newer publish (2026-09-15, project ID `6RKvklppYka`) than our export (2026-09-08, `63XwQxu12fb`). A comparison of all slide files, `data.js` and `paths.js` shows the same slides, texts, quiz, navigation and image references. The only differences are the version label on the title slide (`V07/2026` in the export, `V09/2026` on Review 360), the quiz resume dialog in player scene 0 (only in the export) and some internal IDs (answers, text library) regenerated on publishing, see [4.1](#41-files). Image files were not compared byte by byte. **We use the local export.**
- **Other modules:** Blutzuckermessung uses the same Storyline template (`DiabetesDE_Template_360u22_20190111`) and export format. A pipeline built on this format should therefore carry over to further modules. Nothing was downloaded from Review 360.

## 3. Content structure

The content is organised in a fixed hierarchy (3.1, 3.2), which the export encodes. On top of it, learning objectives, recurring concepts, references and questions link content across chapters (3.3–3.6). The export does not encode these links; they were derived by reading the texts.

### 3.1 Outline

`data.js` defines 12 scenes. Scene 0 is a system scene for player dialogs ("Fortsetzen", "Warnung"). The other 11 scenes contain the 44 slides:

| Scene | Slides | Role |
|---|---|---|
| 1 | 3 | Frame: title slide, learning objectives, *Übersicht* |
| 2 | 2 | Frame: Impressum, *Hinweise zum Lernen* |
| 3 | 3 | Chapter 1 |
| 4 | 4 | Chapter 2 |
| 5 | 4 | Chapter 3 |
| 6 | 2 | Chapter 4 |
| 7 | 5 | Chapter 5 |
| 8 | 6 | Chapter 6 |
| 9 | 13 | Quiz: 10 questions and a result slide, see [3.6](#36-questions) |
| 10 | 1 | Frame: *Abschluss* |
| 11 | 1 | Excluded, see [3.7](#37-unreachable-and-duplicated-content) |

Each chapter scene starts with a *Kapitelstart* slide that holds only navigation hints and, in chapters 2, 3, 5 and 6, the tabs to the topics. Its other slides are the topics below.

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

Chapters 1–5 explain medical content in text. Chapter 6 differs: it presents a patient education course. Its slide text holds only agenda items (e.g. "Übersäuerung des Blutes", "Insulin spritzen"), while its content is in 16 images (see [5.3](#53-findings)).

### 3.2 Navigation

- The *Übersicht* slide is a hub. It links to the *Kapitelstart* slide of every chapter, the quiz and the *Abschluss*. Every chapter returns to it at the end.
- Within a chapter, the topics are reached in order or through the tabs on the *Kapitelstart* slide.
- Scene 2 is not linked from any slide. It is opened by the player button "Informationen". A second player button leads to the *Übersicht*.
- Besides the 29 content pop-ups, the module has 27 feedback layers (knowledge check and quiz) and 4 excluded layers ([3.7](#37-unreachable-and-duplicated-content)), 60 layers in total.

### 3.3 Learning objectives

The learning objectives slide lists five objectives. By content they map as follows:

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
| Learning objectives slide | "Informationen zum Autor und Hinweise zur Arbeit in diesem Modul finden Sie, wenn Sie rechts oben bei “Informationen” klicken." | Scene 2 |

### 3.6 Questions

- **Knowledge check** (1.1, "In welchen Situationen können Ketonkörper auftreten?"): multiple response, tracked, not part of the quiz. Topic 1.2 explains the answers.
- **Quiz** (scene 9): 10 questions, 10 points each, pass mark 70 %. Types: multiple response (1, 3, 4, 6, 10), drag-and-drop matching (2, 5, 8, 9), sequence (7).

By content, the quiz questions test these topics:

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
| Scene 11 *Hungerketose* (1 slide, 1 pop-up layer) | Older variant of topic 5.2 with partly different wording; no slide links to it, only a second "Maßnahmen" entry in the menu | Exclude |
| 3 hidden layers in 6.3, 6.4, 6.5 | Never shown by any trigger; their texts are copies of pop-ups in 5.2 and 5.4 | Exclude |
| *Abschluss* | Closing text with the author's e-mail address | Exclude the address |

The pop-up layer of scene 11 and the 3 hidden layers are the 4 excluded layers counted in [3.2](#32-navigation).

### 3.8 Implications for the knowledge graph

- **The topic is the central unit.** Learning objectives, concepts and questions all map to topics, so topics are the natural anchor for content, provenance and question generation.
- **The mappings in 3.3–3.6 are a first reference** to check the pipeline against.
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
| `html5/data/js/data.js` | `data` | Scenes and slide order, `slideMap` (links and image IDs per slide), `quizzes`, question definitions (`interactions`), `assetLib` (image files), variables, player events | Structure, questions |
| `html5/data/js/<slide-id>.js` (44 files) | `slide` | Layers, objects, texts and triggers of one slide. File names are random IDs, resolved through `data.js`. | Content |
| `story_content/frame.xml` | XML | Player configuration, including the navigation menu (25 entries) under `nav_data/outline/links`: nested `slidelink` elements with `displaytext` (line breaks as `&#xD;`) and `slideid` (`_player.<scene-id>.<slide-id>`); nesting gives the menu levels | Chapter names |
| `html5/data/js/paths.js` | `paths` | Rendered vector shapes, including every text as positioned glyph runs | Ignore: all its text is also in the slide files |
| `html5/data/js/frame.js` | `frame` | Player layout and UI strings | Ignore |
| `mobile/` (49 images) | Raster images | Images shown on the slides | See [Media](#5-media) |
| `meta.xml` | XML | Title, author, publish date, slide count, Storyline version | Provenance |
| `story.html` | HTML | Entry point for viewing the module in a browser | Manual verification |
| `html5/lib/`, `html5/data/css/`, `analytics-frame.html`, `story_content/*.js` | | Storyline player runtime, styles, fonts, tracking, SVG images | Ignore, except the SVG images (see [Media](#5-media)) |

`meta.xml` refers to `mobile/data.json`, `mobile/data.gz` and `story_content/data.swf`. None of these files exist in the export.

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
- **Text** is taken from `vartext`. Besides `textLib`, it occurs in `data.textdata` and `data.itemlist` (drop-down items). `altText` mostly repeats the visible text. For images it holds a description or a file name (e.g. `Chemical_structural_formula_of_acetic_acid.svg`).
- **Order:** objects are stored in layering order, which is not always the reading order. Positions of nested objects are relative to their parent; the absolute positions allow sorting into rows from top to bottom and, within a row, from left to right.

Text quirks the extraction has to handle:

| Quirk | Example | Handling |
|---|---|---|
| `^%^` encodes `%` (22 occurrences) | `Acetoacetat (Anteil etwa 20^%^)` | Replace with `%` |
| Line breaks as `\n` and `\r`, layout with tabs | `Bis 0,6 mmol/l\t\tNormalbefund` | Normalize; tabs mark table-like rows |
| Button labels with an instruction | `Nutzung - Hier klicken -` | Strip the instruction |
| Boilerplate on many slides | `Diabetologie online lernen \| Ketonkörper` (also with `l` instead of `\|` and other suffixes such as `\| Quiz`), `Weiter`, `Zum Schließen klicken`, `Alle Bilder © articulate`, `Beide Bilder © articulate` | Drop |
| Player variables filled in at runtime | `%_player.5X8JOp5iKWb.$Score%` on the quiz result slide | Drop |
| Each drop-down of quiz question 7 lists all items | 5 drop-downs × 5 items | Keep each text once per layer |

### 4.3 Triggers

A pop-up is opened by an event on a button object:

```json
"events": [{"kind": "onrelease", "actions": [
  {"kind": "show_slidelayer", "objRef": {"type": "string", "value": "_parent.6QSSoACHHWX"}}]}]
```

- The button is either a `vectorshape` with a text label or a `stategroup` without a label (e.g. numbered buttons on a graphic, see 3.1).
- Feedback layers of the knowledge check and the quiz are shown by `show_slidelayer` actions in the `answers[].actions` of the question in `data.js`, depending on the answer status. Solution layers are opened by a button on a feedback layer, and the result layers of the quiz by slide events.
- A layer that no `show_slidelayer` action references, neither in the slide file nor in `data.js`, is never shown (see [3.7](#37-unreachable-and-duplicated-content)).
- Jumps between slides are `gotoplay` actions. `slideMap.linksTo` in `data.js` summarizes them per slide.
- The player buttons "Informationen" and "Übersicht" are defined in the `events` of `data.js`.

### 4.4 Questions

Questions are defined in `data.js` under `scenes[].slides[].interactions[]`. The question text itself is on the slide and is not marked as such: it is the base-layer text that is not an answer item. Quiz settings (pass mark, scoring, list of question slides) are in `quizzes[]`; their values are in [3.6](#36-questions).

| Field | Content |
|---|---|
| `type` | `multipleresponse`, `matching` or `sequence` |
| `choices[]` | Answer options with `id` and `lmstext` |
| `statements[]` | Matching and sequence only: drop targets or positions with `id` and `lmstext` |
| `answers[]` | One `correct` and one `incorrect` answer with `points`; the correct one defines the solution in `evaluate.statements` |

How the solution is encoded depends on the type:

- **Multiple response:** the statements list the choices that must be selected.
- **Matching:** each statement pairs a choice (drag item) with a `statementid` (drop target). Choices and targets are objects in the slide file whose IDs follow the `choice_` and `statement_` prefixes. Their `lmstext` carries an LMS prefix such as `Text-feld 3 - Nachweis im Urin` and loses line breaks, so the text of the slide object is preferred. In question 9 the targets are unlabelled boxes in a diagram ("Rechteck 1–4"), so the solution only makes sense with the image.
- **Sequence:** the order of the statements is the correct order of the choices. The slide objects are drop-downs that each list all items, so the choice texts are taken from `lmstext`.

Most feedback layers are generic ("Richtig", "Falsch"). Question 8 adds an explanation; the knowledge check and questions 5 and 9 show the solution as a screenshot.

### 4.5 Implications for the extraction

- Read `data.js`, the slide files and `frame.xml`. `paths.js` and `frame.js` add no content.
- Take text from `vartext`, and `altText` only for images.
- Follow the triggers: content pop-ups are layers referenced by `show_slidelayer`; unreferenced layers are skipped.
- Skip scenes that no `gotoplay` action leads to.
- Clean the quirks in 4.2 and drop boilerplate.
- Keep slide ID, layer ID and object ID with every text as provenance.
- Resolve matching solutions through the drop-target objects on the slide.

### 4.6 Extraction prototype

`prototype/extract.py` implements 4.5 for one module with the Python standard library. It writes one JSON file with the scenes, slides and their layers (base, pop-up, feedback) with texts in reading order, the questions with choices, solution and question text, and the excluded scenes and layers. Every text keeps its slide, layer and object ID. The output contains the source content, so it goes to the git-ignored `data/extracted/`.

```
python prototype/extract.py "data/raw/2026 E-Learning Diabetologie/Ketonkörper" data/extracted/ketonkoerper.json
python -m unittest discover -s prototype
```

The tests check the cleaning rules and, if the raw data is present, the result for Ketonkörper. Results on Ketonkörper:

- **Structure:** 43 slides in 10 scenes, 29 pop-ups and 27 feedback layers. Scene 11 and the 3 hidden layers are excluded by the rules in 4.5, without a module-specific list. This matches the counts in [3.1](#31-outline) and [3.2](#32-navigation).
- **Questions:** the knowledge check and the 10 quiz questions with their types, correct answers, pairs and order, as in [3.6](#36-questions).
- **Text:** 355 texts after cleaning; no `^%^`, boilerplate or e-mail address remains, umlauts are intact.

Limitations:

- **Reading order** is right for text slides, pop-ups and quiz slides. On slides that place labels on a graphic (title slide, 2.1, 2.2, quiz question 9) the labels are read row by row, which does not follow the graphic. On 3.2 some lines appear twice, once as a block and once as separate text boxes.
- **Names** of chapters and topics are taken only from the menu; topic and pop-up names as in [3.1](#31-outline) are not derived yet.
- **Question text** contains all base-layer text that is not an answer item, e.g. instructions and the diagram labels of question 9.
- **Quiz question 9** has no target labels; its pairs have `null` targets.
- **Images** are not processed, so chapter 6 is limited to its headings and agenda items (see [5.3](#53-findings)).

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
| Quiz question 9 | base | 2 drawings (liver, fat cells) and 4 text placeholders as drop zones |
| Quiz question 9 | layer "Hier gehts zur richtigen Antwort" | 1 screenshot of the solution |
| Abschluss | base | 1 photo (laptop) and 1 screenshot of topic 2.2 |

### 5.3 Findings

- **Chapter 6 exists mainly as images.** Its 16 course slides carry the actual content of the patient education chapter. The slide text only holds the headings and agenda items (see [3.1](#31-outline)). Without the images, chapter 6 is almost empty.
- **Some content depends on images.** The metabolism diagram in 2.2 and quiz question 9 combine drawings with text boxes. The solutions of the knowledge check and of quiz questions 5 and 9 are shown as screenshots; the same solutions are also defined as data in `data.js` (see [4.4](#44-questions)).
- **Images are reused.** The structural formulas appear on the title slide and in 3.1, and the liver and fat cell drawings appear in 2.2 and quiz question 9.
- **The photos illustrate** and do not add information, apart from the product labels in 3.2.

## 6. Data quality and open questions

### 6.1 Data quality

- **Complete and machine-readable:** All text, the structure, the quiz with its correct answers and the navigation can be read from the export (sections [3](#3-content-structure) and [4](#4-technical-format)).
- **Manual mappings:** The mappings in 3.3–3.6 have not been reviewed by a domain expert.
- **Encoding and markup:** The payloads are escaped JavaScript strings with a BOM ([4.1](#41-files)), and the texts contain encoded characters, mixed line breaks, button instructions and boilerplate ([4.2](#42-slides-layers-and-objects)).
- **Content in images:** see [5.3](#53-findings).
- **Unreachable, duplicated and personal content:** see [3.7](#37-unreachable-and-duplicated-content).
- **Single module:** All findings are based on Ketonkörper. That other modules follow the same structure is likely (same template) but not verified.

### 6.2 Open questions

| Question | Status |
|---|---|
| May we use the content of the modules in the project? | Yes |
| May the raw data be published in the public repository? | Open; until then it is not committed |
| Can further modules be obtained through Review 360? | Open |
| Do we transcribe the 16 course slides of chapter 6, and if so, how? | Open; decided later |
| How are images used in general (ignored, referenced, described)? | Open; decided later |
