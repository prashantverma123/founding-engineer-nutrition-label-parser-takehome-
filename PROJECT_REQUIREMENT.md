# 🏷️ Product Label Nutrition Parser — Take-Home Assignment

We expect this to take **4–6 hours**. Please don't spend more than that.

---

## Before you start

Most take-home assignments hand you a spec and ask you to implement it. This one doesn't.

We care less about whether your parser handles every edge case and more about **how you think through a problem that has no clean answer**. The nutrition label domain is intentionally messy, inconsistent, and under-defined — the same way real product work is.

Read the brief. Then decide what to build, what to skip, and why.

---

## Overview

Consumer health and nutrition products publish nutrition or supplement facts on product labels — but these labels vary significantly in layout, formatting, naming conventions, and units.

Your task: **build a system that takes a folder of product label images and produces a structured, normalised dataset of nutritional information.**

A sample image folder is provided. No other setup or scaffolding is given — that's intentional.

---

## Input

```
sample_images/
├── product_01.jpg
├── product_02.jpg
└── ...
```

Images may contain nutrition facts panels, supplement facts tables, ingredient lists, and serving size information. They intentionally vary in layout, naming conventions, units, and text structure.

---

## Output

Produce a structured dataset. CSV or Excel is fine. Save it to `output/nutrition_data.csv`.

Example output schema:

| `product_image` | `nutrient_name_raw` | `nutrient_name_standard` | `amount` | `unit` |
|---|---|---|---|---|
| product_01.jpg | Protein | `protein` | 24 | g |
| product_01.jpg | Ascorbic Acid | `vitamin_c` | 60 | mg |
| product_02.jpg | Calcium | `calcium` | 200 | mg |

You can extend this schema if you think there's a good reason to. You can simplify it if you think parts are wrong. Just explain why.

---

## Standardisation

Labels use inconsistent names and units for the same nutrients. Your system should normalise them.

### Nutrient naming examples

| Label text | Standard name |
|---|---|
| Vitamin C | `vitamin_c` |
| Ascorbic Acid | `vitamin_c` |
| Thiamine Mononitrate | `vitamin_b1` |
| Pyridoxine HCL | `vitamin_b6` |

### Unit normalisation examples

| Input | Standard unit |
|---|---|
| milligrams | `mg` |
| grams | `g` |
| mcg | `µg` |
| IU | `IU` |

These are illustrative, not exhaustive. How far you take normalisation — and where you draw the line — is your call.

---

## What we're looking for

We will not be running your code against a hidden test suite. We'll be reading it.

| Criteria | What we're actually evaluating |
|---|---|
| Problem decomposition | Did you identify the hard parts early? What did you solve vs. defer, and why? |
| System design | Is the architecture clear? Would it hold up at 10× the image volume? |
| Judgment under ambiguity | There are at least five places where the right answer isn't obvious. What did you do at each? |
| Code quality | Does the code reflect clear thinking? Is it easy to modify? |

A senior engineer who makes three well-reasoned tradeoffs and documents them clearly will score higher than one who attempts to handle every case without acknowledging the mess.

---

## Deliverables

A GitHub repository containing:

```
README.md
src/
sample_output/
```

Your README is as important as your code. It should cover:

- **What you built** — your approach and key decisions
- **What you decided not to build** — and why
- **The hardest part** — what was genuinely ambiguous and how you resolved it
- **What you'd do next** with more time

There are no constraints on language, tools, models, or frameworks. Use whatever you think is right.

---

## Submission

1. Fork this repository
2. Add your solution
3. Share your forked repo link with us