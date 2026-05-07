# ATAR Calculation Guide

## Overview

The HSC Study Planner uses a sophisticated ATAR prediction system based on Polynomial Regression and official UAC scaling data. This document explains how the ATAR calculation works.

## How ATAR Prediction Works

### 1. Raw Marks Input
You input your raw HSC marks for each subject (0-100 scale).

### 2. Subject Scaling
Each subject is scaled using UAC (Universities Admissions Centre) scaling data:

- **Raw marks** are converted to **scaled marks** using Polynomial Regression
- Scaling accounts for subject difficulty and student performance
- Higher-scaling subjects (like Mathematics Extension 2) get more benefit
- Lower-scaling subjects may see marks compressed

### 3. Polynomial Regression Model
The system uses a degree-2 Polynomial Regression because:
- UAC scaling curves are non-linear
- High-performing students in difficult subjects get disproportionate benefits
- Linear models can't capture this complexity accurately

### 4. Aggregate Calculation
NSW ATAR rules are followed:
- **Best 10 units** are counted (minimum 2 units of English)
- Subjects are ranked by scaled mark
- Top 10 units contribute to the aggregate

### 5. ATAR Conversion
The aggregate (0-500) is converted to ATAR (0-99.95):
- Uses linear approximation of UAC conversion tables
- Higher aggregates = higher ATAR
- Capped at 99.95

## Example Calculation

### Input:
- Mathematics Extension 2: 85/100 (4 units)
- Mathematics Extension 1: 80/100 (2 units)
- Physics: 75/100 (2 units)
- Chemistry: 78/100 (2 units)
- English Advanced: 82/100 (2 units)

### Process:
1. **Scale marks** using Polynomial Regression:
   - MX2: 85 → 92 (scaled)
   - MX1: 80 → 88 (scaled)
   - Physics: 75 → 79 (scaled)
   - Chemistry: 78 → 82 (scaled)
   - English: 82 → 85 (scaled)

2. **Select best 10 units**:
   - MX2 (4u): 92 × 4 = 368
   - MX1 (2u): 88 × 2 = 176
   - English (2u): 85 × 2 = 170
   - Chemistry (2u): 82 × 2 = 164
   - **Total aggregate**: 878/1000

3. **Convert to ATAR**:
   - 878/1000 ≈ 87.8 ATAR

## Key Factors

### Subject Scaling Impact
- **Mathematics Extension 2**: Highest scaling, benefits top performers
- **Sciences**: Moderate to high scaling
- **Humanities**: Generally lower scaling
- **English**: Moderate scaling, required for ATAR

### Performance Distribution
- **Top band (90+)**: Significant scaling benefits in difficult subjects
- **Middle band (70-89)**: Moderate scaling effects
- **Lower band (<70)**: Minimal scaling benefits

## Accuracy Notes

### Strengths:
- Uses real UAC scaling data
- Polynomial Regression captures non-linear effects
- Follows official NSW ATAR rules

### Limitations:
- Based on historical data (may change yearly)
- Individual school scaling not considered
- Approximate ATAR conversion (official tables vary yearly)

## How to Use

1. **Add Subjects**: Enter all your HSC subjects
2. **Input Marks**: Add your current or predicted marks
3. **View Prediction**: See estimated ATAR and subject contributions
4. **Track Progress**: Update marks as you complete assessments

## Tips for Maximizing ATAR

1. **Focus on English** - Required and counts toward aggregate
2. **Consider subject scaling** when choosing subjects
3. **Aim for top bands** in high-scaling subjects
4. **Maintain consistency** across all subjects

---

*Note: This is an estimation tool. Official ATAR calculations use yearly UAC data and may vary.*
