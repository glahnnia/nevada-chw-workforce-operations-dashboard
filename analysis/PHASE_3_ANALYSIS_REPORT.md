# Phase 3 — KPI Analysis Report

**Snapshot:** 2026-11-16  
**Data classification:** Entirely synthetic; no actual NVCHWA outcomes or benchmark comparisons.

## Executive summary
- **2,616** training enrollments across **2,450** distinct learners and **36** cohorts.
- **1,809 / 2,372** completion-eligible enrollments completed (**76.26%**).
- **392 / 2,372** completion-eligible enrollments withdrew (**16.53%**).
- Average progress across all enrollments: **78.99%**; median completed enrollment duration: **79 calendar days**.

## Enrollment trend (by cohort start year)

| Year | Enrollments | Distinct learners within year | Eligible | Completed | Completion rate |
|---|---:|---:|---:|---:|---:|
| 2024 | 836 | 820 | 836 | 631 | 75.48% |
| 2025 | 867 | 858 | 867 | 665 | 76.7% |
| 2026 | 913 | 874 | 669 | 513 | 76.68% |

**Note:** Annual distinct learner totals cannot be added to obtain the overall distinct learner count because some people appear in more than one year.

## Regional distribution

| Region | Enrollments | Eligible | Completion rate |
|---|---:|---:|---:|
| Northern Nevada | 894 | 818 | 74.08% |
| Rural/Frontier | 546 | 494 | 77.53% |
| Southern Nevada | 1154 | 1042 | 77.64% |
| Unknown | 22 | 18 | 61.11% |

## Training language

| Class language | Enrollments | Eligible | Completion rate |
|---|---:|---:|---:|
| English | 1802 | 1638 | 76.74% |
| Spanish | 814 | 734 | 75.2% |

## Workforce pathway observations (not training-attributable)

- Certification K09: **1111 / 1590** eligible completers observed (**69.87%** coverage, using a 3-month eligibility threshold).
- Certification K10: **466 / 1111** observed completers had latest milestone *Certified* (**41.94%**). This is not an ever-certified measure.
- Employment 3-month coverage: **1190 / 1590** (**74.84%**); CHW employment among known statuses: **562 / 1122** (**50.09%**), Unknown: **68**.
- Employment 6-month coverage: **872 / 1405** (**62.06%**); CHW employment among known statuses: **540 / 835** (**64.67%**), Unknown: **37**.
- Employment status retention K13: **236 / 302** (**78.15%**) of 3-month CHW-employed completers with known 6-month status remained CHW-employed. Baseline with 6-month opportunity: 500.

## Dashboard handoff

- `dashboard/looker_enrollment_detail.csv`: one enrollment per row; use COUNT_DISTINCT(`learner_id`) for learner counts; DO NOT sum `seat_capacity` on this detail table (it is repeated per enrollment).
- `analysis/kpi_by_cohort.csv`: one cohort per row including correct capacity and fill rate.
- `analysis/kpi_by_end_quarter.csv`: quarterly completion trend (by cohort planned end quarter).
- `analysis/kpi_followup_windows.csv`: use this table for observed employment rates/coverage; do not join follow-up tables directly to enrollment detail because repeated enrollments could duplicate outcomes.
- `analysis/kpi_summary.csv`: global scorecard values with denominator and methods.

## Limits and interpretation

1. Synthetic records cannot establish actual workforce outcomes, causal effects, or statewide trends.
2. Completion eligibility requires cohort planned end on/before snapshot; training progress includes active cohorts.
3. Certification is latest recorded milestone after most recent completion, not cumulative ever-certified status.
4. Follow-up is observation-based; rates exclude unobserved people, and employment Unknown is not Unemployed.
5. For retention, an employment status at both dates is not proof of the same employer or continuous employment.
6. Cohort composition can change observed subgroup rates. Do not infer explanations from simulated differences.
7. Seven cohorts may be over planned seat capacity; exceeding 100% fill is intentional and valid.

## Next phase
Build Looker Studio pages: Executive Overview, Training Operations, and exploratory Workforce Pathways. Use page-level notes stating **Synthetic data — demonstration only**.
