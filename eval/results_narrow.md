# Eval results

Mean of 3 scoring runs; CI = bootstrap over papers (1000 resamples). Small n: wide intervals.

## DEV (owner-reviewed, used to choose settings): n=46 (16 positive), scoring errors: 0

| variant | precision (95% CI) | recall (95% CI) | F1 (95% CI) |
|---|---|---|---|
| no validation | 0.60 (0.40-0.81) | 0.85 (0.65-1.00) | 0.71 (0.52-0.86) |
| quotes, exact | 0.55 (0.25-0.83) | 0.44 (0.19-0.70) | 0.48 (0.21-0.70) |
| quotes, fuzzy | 0.61 (0.36-0.88) | 0.56 (0.29-0.82) | 0.58 (0.33-0.78) |
| fuzzy + strength>=4 | 0.69 (0.40-0.94) | 0.54 (0.29-0.80) | 0.60 (0.35-0.80) |
| fuzzy + strength>=5 | 0.93 (0.00-1.00) | 0.21 (0.00-0.43) | 0.33 (0.00-0.59) |

AI first-draft vs owner final labels on DEV: Cohen's kappa = 0.70

## TEST (fresh pool, blind owner labels, never tuned on): n=60 (23 positive), scoring errors: 0

| variant | precision (95% CI) | recall (95% CI) | F1 (95% CI) |
|---|---|---|---|
| no validation | 0.66 (0.45-0.86) | 0.61 (0.40-0.81) | 0.63 (0.45-0.79) |
| quotes, exact | 0.64 (0.35-0.88) | 0.41 (0.20-0.63) | 0.50 (0.26-0.68) |
| quotes, fuzzy | 0.62 (0.36-0.87) | 0.45 (0.24-0.68) | 0.52 (0.30-0.71) |
| fuzzy + strength>=4 | 0.62 (0.33-0.89) | 0.33 (0.14-0.57) | 0.43 (0.21-0.65) |
| fuzzy + strength>=5 | 0.44 (0.00-1.00) | 0.06 (0.00-0.17) | 0.10 (0.00-0.27) |

