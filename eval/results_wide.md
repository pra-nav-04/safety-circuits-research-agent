# Eval results

Scorer prompt: **wide**. Mean of 3 scoring runs; CI = bootstrap over papers (1000 resamples). Small n: wide intervals.

## DEV (owner-reviewed, used to choose settings): n=46 (16 positive), scoring errors: 0

| variant | precision (95% CI) | recall (95% CI) | F1 (95% CI) |
|---|---|---|---|
| no validation | 0.42 (0.26-0.58) | 1.00 (1.00-1.00) | 0.59 (0.41-0.74) |
| quotes, exact | 0.41 (0.22-0.60) | 0.58 (0.33-0.83) | 0.48 (0.27-0.65) |
| quotes, fuzzy | 0.44 (0.26-0.64) | 0.71 (0.50-0.93) | 0.54 (0.35-0.70) |
| fuzzy + strength>=4 | 0.50 (0.30-0.71) | 0.69 (0.46-0.92) | 0.58 (0.37-0.74) |
| fuzzy + strength>=5 | 1.00 (0.00-1.00) | 0.19 (0.00-0.40) | 0.32 (0.00-0.57) |

AI first-draft vs owner final labels on DEV: Cohen's kappa = 0.70

## TEST (fresh pool, blind owner labels, never tuned on): n=60 (23 positive), scoring errors: 0

| variant | precision (95% CI) | recall (95% CI) | F1 (95% CI) |
|---|---|---|---|
| no validation | 0.48 (0.33-0.61) | 0.93 (0.80-1.00) | 0.63 (0.48-0.75) |
| quotes, exact | 0.63 (0.42-0.81) | 0.64 (0.43-0.83) | 0.63 (0.44-0.78) |
| quotes, fuzzy | 0.61 (0.41-0.81) | 0.64 (0.43-0.83) | 0.62 (0.44-0.77) |
| fuzzy + strength>=4 | 0.62 (0.39-0.83) | 0.54 (0.33-0.76) | 0.57 (0.39-0.74) |
| fuzzy + strength>=5 | 0.33 (0.00-1.00) | 0.01 (0.00-0.08) | 0.03 (0.00-0.15) |

