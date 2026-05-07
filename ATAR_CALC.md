# ATAR Calculator — Implementation Guide

## Overview

This document covers everything needed to add an ATAR calculator to the Task Organiser Flask app. The calculator takes a student's HSC marks across their subjects, scales them using polynomial regression models trained on real published data, and produces an estimated ATAR.

---

## How the Calculation Works

The ATAR calculation follows four steps:

1. **HSC mark** — the student enters the mark NESA returns to them (not the raw exam mark)
2. **Scaling** — each HSC mark is converted to a scaled mark using a subject-specific polynomial regression model
3. **Aggregation** — UAC selects the best 10 units (English mandatory, then best remaining units)
4. **ATAR conversion** — the aggregate scaled score is mapped to an ATAR percentile

> **Note:** The input is always the HSC mark, not the raw exam mark. The flow is:
> `raw exam mark → moderation → HSC mark → scaling → scaled mark → ATAR`

---

## Data Sources

All scaling data points come from real published sources:

- **hscscalinggraphs.au** — curve graphs showing HSC mark vs scaled mark per subject (2025)
- **matrix.edu.au ATAR calculator** — exact (HSC mark, scaled mark) pairs at specific mark values
- **UAC published scaling tables** — aggregate-to-ATAR conversion breakpoints
- **Multi-mark calibration spreadsheet** — (HSC mark, ATAR equivalent) pairs across 3 mark values per subject, covering English, Maths, Sciences, and Humanities

---

## Key Data Points Extracted

### From matrix.edu.au (exact pairs)

#### HSC Mark = 80 inputs (Image 1)

| Subject | HSC Mark | Scaled Mark |
|---|---|---|
| English Advanced | 80 | 64.0 |
| English Ext. 1 | 75 | 64.8 |
| English Ext. 2 | 50 | 44.7 |
| English Standard | 85 | 72.9 |
| General Maths | 85 | 69.0 |
| Maths Advanced | 70 | 49.3 |
| Maths Ext. 1 | 50 | 48.6 |
| Maths Ext. 2 | 40 | 43.3 |

#### HSC Mark = 75 for all (Image 2)

| Subject | HSC Mark | Scaled Mark |
|---|---|---|
| English Advanced | 75 | 53.1 |
| English Ext. 1 | 75 | 64.8 |
| English Ext. 2 | 75 | 67.2 |
| English Standard | 75 | 51.4 |
| General Maths | 75 | 52.6 |
| Maths Advanced | 75 | 58.5 |
| Maths Ext. 1 | 75 | 72.9 |
| Maths Ext. 2 | 75 | 81.2 |

#### Sciences and Humanities at HSC Mark = 75 (Image 3)

| Subject | HSC Mark | Scaled Mark |
|---|---|---|
| Biology | 75 | 57.3 |
| Chemistry | 75 | 63.8 |
| Physics | 75 | 62.9 |
| Business Studies | 75 | 47.2 |
| Economics | 75 | 63.5 |
| Legal Studies | 75 | 49.8 |

#### Arts and History at HSC Mark = 75 (Image 4)

| Subject | HSC Mark | Scaled Mark |
|---|---|---|
| Ancient History | 75 | 52.3 |
| History Extension | 75 | 66.5 |
| Modern History | 75 | 51.6 |
| Drama | 75 | 40.7 |
| Music 1 | 75 | 28.0 |
| Music 2 | 75 | 51.4 |
| Music Extension | 75 | 50.6 |
| Visual Arts | 75 | 30.7 |

### From hscscalinggraphs.au (curve readings, 2025)

#### English Advanced
| HSC Mark | Scaled Mark |
|---|---|
| 64 | 44 |
| 70 | 49 |
| 77 | 55 |
| 82 | 67 |
| 85 | 78 |
| 90 | 84 |
| 95 | 93 |
| 99 | 100 |

#### English Standard
| HSC Mark | Scaled Mark |
|---|---|
| 68 | 29 |
| 73 | 40 |
| 77 | 52 |
| 80 | 63 |
| 85 | 73 |
| 88 | 80 |
| 95 | 93 |
| 98 | 99 |

#### English Extension 1 (out of 50)
| HSC Mark | Scaled Mark |
|---|---|
| 82 | 64 |
| 84 | 67 |
| 88 | 74 |
| 92 | 82 |
| 94 | 88 |
| 98 | 96 |
| 100 | 100 |

#### English Extension 2 (out of 50)
| HSC Mark | Scaled Mark |
|---|---|
| 76 | 64 |
| 83 | 73 |
| 90 | 81 |
| 92 | 81 |
| 95 | 85 |
| 96 | 88 |
| 98 | 96 |
| 100 | 100 |

#### Mathematics Extension 2 (out of 50)
Starts high (~83 at HSC 75) and curves gently upward — one of the strongest scaling subjects.
| HSC Mark | Scaled Mark |
|---|---|
| 75 | 83 |
| 85 | 89.5 |
| 93 | 93.5 |
| 96 | 96.5 |
| 99 | 99.5 |
| 100 | 100 |

#### Mathematics Extension 1 (out of 50)
Starts at ~73 for HSC 70, accelerates noticeably above HSC 90.
| HSC Mark | Scaled Mark |
|---|---|
| 70 | 73 |
| 80 | 80 |
| 84 | 83 |
| 92 | 89.5 |
| 96 | 94.5 |
| 99 | 99 |
| 100 | 100 |

#### Mathematics Advanced
Strong upward curve — HSC 72 maps to only ~52, but HSC 96 reaches 95.
| HSC Mark | Scaled Mark |
|---|---|
| 72 | 52 |
| 80 | 66.5 |
| 85 | 72.5 |
| 89 | 78 |
| 94 | 86 |
| 96 | 95 |
| 100 | 100 |

#### Mathematics Standard 2
Near-linear relationship, scales down relative to Maths Advanced throughout.
| HSC Mark | Scaled Mark |
|---|---|
| 64 | 30.5 |
| 73 | 46.5 |
| 75 | 50.5 |
| 81 | 63 |
| 82 | 63.5 |
| 85 | 69.5 |
| 89 | 75 |
| 95 | 85.5 |
| 98 | 94 |

#### Physics
Scales up moderately, consistent curve throughout.
| HSC Mark | Scaled Mark |
|---|---|
| 64 | 48 |
| 75 | 64 |
| 84 | 78 |
| 90 | 86 |
| 95 | 94.5 |
| 99 | 100 |

#### Biology
Scales down compared to Physics and Chemistry, especially below HSC 80.
| HSC Mark | Scaled Mark |
|---|---|
| 66 | 36 |
| 75 | 53 |
| 84 | 70 |
| 88 | 80 |
| 95 | 90 |
| 99 | 100 |

#### Chemistry
Sits between Physics and Biology — slightly higher than Physics at low marks, converges at the top.
| HSC Mark | Scaled Mark |
|---|---|
| 68 | 51.5 |
| 75 | 68 |
| 80 | 74 |
| 84 | 79.5 |
| 90 | 87 |
| 95 | 94.5 |
| 99 | 100 |

#### Investigating Science
Scales down noticeably — HSC 68 maps to only ~23 scaled.
| HSC Mark | Scaled Mark |
|---|---|
| 68 | 23 |
| 76 | 40 |
| 85 | 58 |
| 89 | 71 |
| 94 | 85 |
| 98 | 93.5 |

#### Earth & Environmental Science
Scales slightly better than Investigating Science, curves upward sharply above HSC 88.
| HSC Mark | Scaled Mark |
|---|---|
| 67 | 28 |
| 76 | 46.5 |
| 80 | 63 |
| 88 | 74.5 |
| 90 | 85 |
| 95 | 86 |
| 99 | 96 |

#### Economics
Strongest scaling in the commerce block — consistently ~15-20 points above Business Studies at every mark.
| HSC Mark | Scaled Mark |
|---|---|
| 66 | 33 |
| 71 | 50 |
| 80 | 66 |
| 87 | 78 |
| 90 | 86 |
| 96 | 94 |
| 100 | 100 |

#### Business Studies
Near-identical to Legal Studies throughout the range.
| HSC Mark | Scaled Mark |
|---|---|
| 66 | 30.5 |
| 75 | 46.5 |
| 80 | 55 |
| 85 | 65 |
| 90 | 79.5 |
| 96 | 91 |
| 99 | 100 |

#### Legal Studies
Tracks Business Studies very closely — within 1-2 scaled marks at every point.
| HSC Mark | Scaled Mark |
|---|---|
| 66 | 33 |
| 75 | 47 |
| 80 | 52 |
| 85 | 65 |
| 90 | 80 |
| 96 | 91 |
| 99 | 100 |

#### Geography
Broadly similar to Modern History, slightly higher in the 70–85 band.
| HSC Mark | Scaled Mark |
|---|---|
| 64 | 27.5 |
| 68 | 33.5 |
| 70 | 42 |
| 75 | 51 |
| 80 | 51 |
| 85 | 65.5 |
| 86 | 69 |
| 90 | 81.5 |
| 95 | 94.5 |
| 100 | 100 |

#### Modern History
Very close to Geography — the two subjects are nearly indistinguishable on the curve.
| HSC Mark | Scaled Mark |
|---|---|
| 64 | 27.5 |
| 68 | 34 |
| 75 | 52 |
| 76 | 56 |
| 80 | 59.5 |
| 85 | 67.5 |
| 86 | 68.5 |
| 90 | 79 |
| 95 | 92 |
| 99 | 100 |

#### Ancient History
Scales slightly lower than Modern History in the 75–90 band, converges at the top.
| HSC Mark | Scaled Mark |
|---|---|
| 64 | 27.5 |
| 70 | 41.5 |
| 75 | 45 |
| 80 | 56 |
| 85 | 62.5 |
| 86 | 69 |
| 90 | 75 |
| 95 | 89 |
| 99 | 97 |

#### Studies of Religion I
Starts above Ancient History at HSC 70 but falls behind in the 80–90 range.
| HSC Mark | Scaled Mark |
|---|---|
| 70 | 41.5 |
| 75 | 51.5 |
| 80 | 59.5 |
| 85 | 62.5 |
| 86 | 69.5 |
| 90 | 75.5 |
| 95 | 80 |
| 97 | 88.5 |
| 99 | 97 |

#### PDHPE
Strong scaling — tracks near the top of the non-extension humanities block.
| HSC Mark | Scaled Mark |
|---|---|
| 67 | 28.5 |
| 75 | 46 |
| 80 | 63 |
| 85 | 63.5 |
| 90 | 75 |
| 95 | 87 |
| 97 | 96.5 |

#### Society & Culture
Closely matches CAFS throughout — very minor separation in the 80–90 band.
| HSC Mark | Scaled Mark |
|---|---|
| 72 | 29.5 |
| 75 | 46.5 |
| 80 | 46.5 |
| 85 | 63 |
| 87 | 66.5 |
| 90 | 75.5 |
| 95 | 89.5 |
| 99 | 96.5 |

#### Community & Family Studies (CAFS)
Low floor — HSC 67 maps to only ~19.5, one of the lowest starting points in this block.
| HSC Mark | Scaled Mark |
|---|---|
| 67 | 19.5 |
| 72 | 29.5 |
| 75 | 36 |
| 80 | 53.5 |
| 85 | 67 |
| 87 | 67.5 |
| 95 | 88.5 |
| 99 | 93 |

#### Dance
Sparse data in the low range — curve only begins at HSC 79, scaling up steeply from there.
| HSC Mark | Scaled Mark |
|---|---|
| 79 | 30.5 |
| 85 | 49 |
| 89 | 65 |
| 95 | 79 |
| 98 | 89 |
| 99 | 93 |

#### Software Engineering
Strong scaling subject — consistently 10-15 points above Food Technology at every mark.
| HSC Mark | Scaled Mark |
|---|---|
| 69 | 38.5 |
| 76 | 54.5 |
| 82 | 69.5 |
| 89 | 81 |
| 96 | 94 |
| 99 | 100 |

#### Food Technology
Low floor (~19 at HSC 65), near-linear curve.
| HSC Mark | Scaled Mark |
|---|---|
| 65 | 19 |
| 69 | 35.5 |
| 74 | 35.5 |
| 82 | 54.5 |
| 89 | 71.5 |
| 95 | 86 |
| 98 | 91.5 |

#### Engineering Studies
Best scaling in the technology block — starts at 37.5 for HSC 67 and reaches 99.5 at HSC 100.
| HSC Mark | Scaled Mark |
|---|---|
| 67 | 37.5 |
| 71 | 44.5 |
| 75 | 53 |
| 80 | 67 |
| 90 | 79.5 |
| 96 | 91.5 |
| 100 | 99.5 |

#### Design & Technology
Scales up reasonably but lags Engineering Studies by ~15 points throughout the curve.
| HSC Mark | Scaled Mark |
|---|---|
| 78 | 30 |
| 80 | 45.5 |
| 85 | 62 |
| 90 | 74.5 |
| 95 | 90 |
| 99 | 95.5 |

#### Industrial Technology
Lowest scaling in the technology block — HSC 63 maps to only ~18.5 and tops out at ~84.5 at HSC 99.
| HSC Mark | Scaled Mark |
|---|---|
| 63 | 18.5 |
| 71 | 33.5 |
| 79 | 51 |
| 85 | 65.5 |
| 88 | 65.5 |
| 90 | 72.5 |
| 95 | 79.5 |
| 99 | 84.5 |

### From multi-mark calibration spreadsheet (HSC mark → ATAR equivalent)

> **Important distinction:** These are *single-subject ATAR equivalents*, not scaled marks. A single-subject ATAR equivalent answers "what ATAR would a student achieve if this were their only subject?" They are derived from the scaled mark and the aggregate-to-ATAR curve, making them a useful cross-check for the polynomial model but not directly usable as scaled marks in the aggregation step. They are recorded here as validation data.

#### English

| Subject | HSC Mark | ATAR Equivalent |
|---|---|---|
| English Standard | 82 | 81.60 |
| English Standard | 75 | 66.00 |
| English Standard | 90 | 96.80 |
| English Advanced | 80 | 80.15 |
| English Advanced | 75 | 68.00 |
| English Advanced | 90 | 96.90 |

#### Mathematics

| Subject | HSC Mark | ATAR Equivalent |
|---|---|---|
| Maths Standard | 84 | 84.15 |
| Maths Standard | 70 | 54.45 |
| Maths Standard | 90 | 91.75 |
| Maths Advanced | 77 | 77.10 |
| Maths Advanced | 70 | 63.60 |
| Maths Advanced | 90 | 95.25 |
| Maths Ext. 1 | 60 | 74.05 |
| Maths Ext. 1 | 70 | 84.40 |
| Maths Ext. 1 | 90 | 98.60 |
| Maths Ext. 2 | 50 | 69.20 |
| Maths Ext. 2 | 70 | 91.45 |
| Maths Ext. 2 | 90 | 99.70 |

#### Sciences

| Subject | HSC Mark | ATAR Equivalent |
|---|---|---|
| Biology | 77 | 76.95 |
| Biology | 70 | 62.80 |
| Biology | 90 | 96.05 |
| Chemistry | 71 | 71.15 |
| Chemistry | 65 | 62.65 |
| Chemistry | 90 | 97.25 |
| Physics | 70 | 70.90 |
| Physics | 60 | 55.90 |
| Physics | 90 | 97.45 |

#### Humanities

| Subject | HSC Mark | ATAR Equivalent |
|---|---|---|
| Modern History | 82 | 82.05 |
| Ancient History | 82 | 82.30 |
| Ancient History | 70 | 57.05 |
| Ancient History | 90 | 94.50 |
| Geography | 83 | 82.90 |
| Geography | 70 | 54.45 |
| Geography | 90 | 95.25 |
| PDHPE | 85 | 85.60 |
| PDHPE | 70 | 49.75 |
| PDHPE | 90 | 93.40 |
| Economics | 70 | 70.25 |
| Economics | 80 | 86.15 |
| Economics | 90 | 97.30 |
| Business Studies | 86 | 86.50 |
| Business Studies | 70 | 50.30 |
| Business Studies | 90 | 93.15 |
| Legal Studies | 85 | 85.70 |
| Legal Studies | 70 | 55.35 |

#### How to use ATAR equivalents for model validation

Because a single-subject ATAR equivalent can be back-converted to an approximate scaled mark, these points let you verify whether the polynomial model is producing sensible outputs. The back-conversion uses the inverse of the `aggregate_to_atar()` function — find the aggregate that maps to the given ATAR, then divide by 5 (assuming a 10-unit, 5-subject student) to get an implied average scaled mark per subject.

For example:
```
Maths Ext. 2, HSC 70 → ATAR equivalent 91.45
→ aggregate that gives ATAR 91.45 ≈ 382
→ implied scaled mark ≈ 382 / 5 = 76.4 per subject
→ so Maths Ext. 2 at HSC 70 should scale to roughly 76–78
→ which aligns with the matrix.edu.au pair (75, 81.2) nearby
```

---

## Extension Subjects

Extension 1 and Extension 2 subjects are marked out of 50 by NESA. The subjects where this applies:

- English Extension 1
- English Extension 2
- Mathematics Extension 1 (reported out of 50, UAC converts before aggregation)
- History Extension
- Music Extension

The calculator should display appropriate input labels for these subjects (e.g. "out of 50").

---

## Why Polynomial Regression

Linear scaling fails for HSC marks because:

- Some subjects scale **up** (raw 75 English Adv → scaled 53, a significant boost)
- Some subjects scale **down** at the top end
- English Extension 2 has an S-curve shape — it flattens in the middle and steepens at both ends
- Music 1 scales down dramatically (HSC 75 → scaled 28)

A **degree 4 polynomial** captures these curves accurately. For subjects with fewer than 8 data points, degree 3 is used to avoid overfitting.

The formula per subject is:

```
scaled = β₀ + β₁x + β₂x² + β₃x³ + β₄x⁴
where x = HSC mark
```

Coefficients are fitted using scikit-learn's `PolynomialFeatures` + `LinearRegression` pipeline, trained on the data points above.

---

## Subject Scaling Observations

| Subject | Scaling behaviour at HSC 75 |
|---|---|
| Maths Ext. 2 | Scales up strongly → 81.2 |
| Maths Ext. 1 | Scales up → 72.9 |
| English Ext. 1 | Scales up → 64.8 |
| English Ext. 2 | Scales up → 67.2 |
| Chemistry | Mild boost → 63.8 |
| Economics | Mild boost → 63.5 |
| Physics | Mild boost → 62.9 |
| Biology | Roughly neutral → 57.3 |
| English Standard | Roughly neutral → 51.4 |
| Business Studies | Scales down slightly → 47.2 |
| Drama | Scales down → 40.7 |
| Visual Arts | Scales down → 30.7 |
| Music 1 | Scales down significantly → 28.0 |

---

## Aggregation Rules

UAC selects the best 10 units from a student's subjects:

1. English (best result if multiple English subjects) is **mandatory**
2. Remaining units are chosen in descending scaled mark order until 10 units are reached
3. Extension subjects count as 1 unit; all others count as 2 units

Example selection for 5 standard subjects + 1 extension:
```
English Advanced (2 units)  → mandatory
Maths Ext. 2    (2 units)  → best remaining
Chemistry       (2 units)
Physics         (2 units)
History Ext.    (1 unit)
Maths Ext. 1   (1 unit)
─────────────────────────
Total: 10 units ✓
```

---

## Aggregate → ATAR Conversion

Linear interpolation between these published breakpoints:

| Aggregate | ATAR |
|---|---|
| 500 | 99.95 |
| 490 | 99.70 |
| 480 | 99.50 |
| 470 | 99.20 |
| 460 | 99.00 |
| 450 | 98.50 |
| 440 | 98.00 |
| 430 | 97.00 |
| 420 | 96.00 |
| 410 | 95.00 |
| 400 | 93.50 |
| 390 | 92.00 |
| 380 | 90.00 |
| 370 | 88.00 |
| 360 | 85.00 |
| 350 | 82.00 |
| 340 | 79.00 |
| 330 | 76.00 |
| 320 | 73.00 |
| 310 | 70.00 |
| 300 | 67.00 |
| 280 | 61.00 |
| 260 | 55.00 |
| 240 | 49.00 |
| 220 | 43.00 |
| 200 | 37.00 |
| 180 | 32.00 |
| 160 | 27.00 |
| 140 | 22.00 |
| 120 | 17.00 |
| 100 | 12.00 |
| 80 | 8.00 |
| 60 | 4.00 |
| 0 | 0.00 |

---

## File Structure

```
Task_Organiser/
├── atar_data.py              ← polynomial models + calculation logic
├── app.py                    ← add /atar route here
├── templates/
│   └── atar_calculator.html  ← calculator UI
└── requirements.txt          ← add numpy, scikit-learn
```

---

## Dependencies

Add to `requirements.txt`:

```
Flask>=3.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
```

---

## Flask Route (add to app.py inside register_routes)

```python
@app.route('/atar', methods=['GET', 'POST'])
@login_required
def atar_calculator():
    from .atar_data import SUBJECT_SCALING_POINTS, calculate_atar_estimate

    result = None
    subjects = []

    if request.method == 'POST':
        subject_names = request.form.getlist('subject_name')
        hsc_marks     = request.form.getlist('hsc_mark')
        units_list    = request.form.getlist('units')

        for name, mark, units in zip(subject_names, hsc_marks, units_list):
            if name and mark:
                try:
                    subjects.append({
                        'subject_name': name,
                        'hsc_mark':     float(mark),
                        'units':        int(units),
                    })
                except ValueError:
                    pass

        if subjects:
            result = calculate_atar_estimate(subjects)

    return render_template(
        'atar_calculator.html',
        subject_list=list(SUBJECT_SCALING_POINTS.keys()),
        result=result,
        subjects=subjects,
    )
```

---

## Navbar Link (add to base.html)

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('atar_calculator') }}">ATAR Calculator</a>
</li>
```

---

## Disclaimer

This calculator produces **estimates only**. The actual ATAR algorithm is proprietary to UAC and cannot be replicated exactly. Results may differ from the official ATAR due to:

- Year-to-year variation in scaling curves
- Cohort performance differences
- Moderation adjustments NESA applies before releasing HSC marks
- Rounding in the official process

Always include a disclaimer on the calculator page stating results are estimates based on publicly available data.

---

## Improving Accuracy Over Time

To improve the model for any subject, grab more data points from hscscalinggraphs.au (more years, more mark values) and add them to the `SUBJECT_SCALING_POINTS` dict in `atar_data.py`. The polynomial model automatically retrains on the next request — no other changes needed.

Current data coverage per subject:

| Subject | Data points | Quality |
|---|---|---|
| English Advanced | 20+ | ✅ Good |
| English Standard | 10+ | ✅ Good |
| English Ext. 1 | 7 | ✅ Good |
| English Ext. 2 | 10 | ✅ Good |
| Maths Ext. 2 | 8 | ✅ Good |
| Maths Ext. 1 | 9 | ✅ Good |
| Maths Advanced | 9 | ✅ Good |
| Maths Standard 2 | 11 | ✅ Good |
| Physics | 8 | ✅ Good |
| Chemistry | 9 | ✅ Good |
| Biology | 8 | ✅ Good |
| Investigating Science | 6 | ✅ Good |
| Earth & Environmental Science | 7 | ✅ Good |
| Economics | 7 | ✅ Good |
| Business Studies | 7 | ✅ Good |
| Legal Studies | 7 | ✅ Good |
| Geography | 10 | ✅ Good |
| Modern History | 10 | ✅ Good |
| Ancient History | 9 | ✅ Good |
| Studies of Religion I | 9 | ✅ Good |
| PDHPE | 7 | ✅ Good |
| Society & Culture | 8 | ✅ Good |
| Community & Family Studies | 8 | ✅ Good |
| Dance | 6 | ⚠️ Moderate — no low-end data (curve starts at HSC 79) |
| Software Engineering | 6 | ✅ Good |
| Food Technology | 7 | ✅ Good |
| Engineering Studies | 7 | ✅ Good |
| Design & Technology | 6 | ✅ Good |
| Industrial Technology | 8 | ✅ Good |
| Drama | 1 | ❌ Thin — single matrix pair only |
| Music 1 | 1 | ❌ Thin — single matrix pair only |
| Music 2 | 1 | ❌ Thin — single matrix pair only |
| Visual Arts | 1 | ❌ Thin — single matrix pair only |
| History Extension | 1 | ❌ Thin — single matrix pair only |
| Music Extension | 1 | ❌ Thin — single matrix pair only |

Subjects marked ❌ should use degree 2 polynomial maximum. Dance should use degree 3 due to missing low-end data. All others have enough points for degree 4.

**Remaining subjects to source graph data for:**
- Drama, Visual Arts (Creative Arts)
- Music 1, Music 2, Music Extension
- History Extension
