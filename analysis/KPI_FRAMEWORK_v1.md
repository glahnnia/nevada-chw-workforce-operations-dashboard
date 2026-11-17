# CHW Workforce Operations Dashboard — KPI Framework (v1.0)

**Status:** Proposed calculations for a fictional/synthetic dataset. No numerical results are claimed.

## Principles
- All rates show numerator, denominator, reporting period, and applicable filters.
- Enrollment measures use **enrollment records**; workforce reach measures use **distinct learners**.
- Cohort outcome rates exclude cohorts still in progress unless explicitly labeled provisional.
- Follow-up measures use only people with eligible observed follow-up; nonresponses are not treated as failures. Display follow-up coverage.
- Certification and employment are not assumed to follow from class completion.

| ID | KPI | Calculation | Unit / denominator | Recommended visualization / note |
|---|---|---|---|---|
| K01 | Total enrollments | COUNT(enrollment_id) | Enrollments in selected period | Scorecard; can include repeat learners |
| K02 | Unique learners | COUNT_DISTINCT(learner_id) across eligible enrollments | People | Scorecard; distinct across cohorts |
| K03 | Enrollment by region | COUNT(enrollment_id) grouped by region | Enrollments | Bar chart; Unknown explicit |
| K04 | Cohort fill rate | COUNT(enrollments for cohort) / seat_capacity × 100 | Cohort seats; cohort-specific | Bar chart; overcapacity can exceed 100% |
| K05 | Completion rate | COUNT(eligible enrollments with Completed status) / COUNT(completion_eligible enrollments) × 100 | Completion-eligible enrollments | KPI + cohort comparison; exclusion policy documented |
| K06 | Withdrawal rate | COUNT(eligible enrollments with Withdrawn status) / COUNT(completion_eligible enrollments) × 100 | Completion-eligible enrollments | Trend; not the inverse of completion rate if other statuses exist |
| K07 | Average module progress | AVG(modules_completed / modules_required) × 100 | Enrollments with modules_required > 0 | Cohort bar; labeled progress, not completion |
| K08 | Median days to completion | MEDIAN(completion_date - enrollment_date) | Completed enrollments with valid dates | Summary by cohort; calendar days |
| K09 | Certification follow-up coverage | COUNT_DISTINCT(completers with certification observation in selected follow-up window) / COUNT_DISTINCT(completers eligible for window) × 100 | Eligible completed learners | Display alongside any certification outcome |
| K10 | Observed certification attainment | COUNT_DISTINCT(observed eligible completers reporting/recorded Certified) / COUNT_DISTINCT(eligible completers with certification follow-up) × 100 | Observed eligible completers | State source type: self-reported or verified; not full-population attainment |
| K11 | Employment follow-up coverage | COUNT_DISTINCT(completers observed at follow-up) / COUNT_DISTINCT(completers eligible for follow-up) × 100 | Eligible completed learners | Use a defined follow-up window, e.g. 3 or 6 months |
| K12 | Observed CHW employment rate | COUNT_DISTINCT(observed completers Employed in CHW role) / COUNT_DISTINCT(completers with known employment status at same follow-up window) × 100 | Completers with known status | Show missing/Unknown separately; do not call placement rate |
| K13 | Observed CHW retention rate | COUNT_DISTINCT(CHW-employed learners at baseline and follow-up) / COUNT_DISTINCT(CHW-employed learners at baseline with known follow-up) × 100 | Baseline CHW-employed learners with observed follow-up | Requires at least two comparable observations; distinguish employment retention from same-employer retention |
| K14 | Completion trend | K05 calculated per cohort end month or quarter | Eligible enrollments by end period | Line chart; time axis uses cohort end date |

## Recommended initial dashboard pages
1. **Executive Overview:** K01, K02, K05, K06 and trend K14; filters for cohort, time, region, language.
2. **Training Operations:** K03, K04, K07, K08 with cohort comparisons.
3. **Workforce Pathways (optional):** K09–K13 with prominent follow-up coverage, observation window and data-source labels.

## Analysis and quality notes
- The same learner can appear in multiple enrollments; cohort-level completion is based on enrollments, while post-training outcomes are based on unique people and defined qualifying completion events.
- For workforce measures, define the learner's **qualifying completion** (suggested default: most recent completion before the follow-up window) before linking observations; do not duplicate a follow-up row across several enrollments.
- Certification records may contain multiple milestones; for attainment, use latest valid milestone as of reporting cutoff, or an ever-certified flag with an explicit methodology, not a raw count of rows.
- Observed employment is **not** causally attributable to the training. A placement metric would require a documented placement definition and attribution rules.
- Cohort status snapshots need an as-of date; current status alone is not enough to recreate historical month-end views.
- Display sample sizes and avoid interpreting tiny subgroup differences.

## Proposed synthetic testing scenarios
- A learner enrolling in two cohorts (distinct-person logic).
- A cohort still in progress (completion eligibility).
- A person who completes training but does not seek certification.
- A person certified but whose employment is unknown.
- A completed learner employed in a non-CHW role.
- Missed 6-month follow-up (coverage versus outcomes).
- Overcapacity cohort and late withdrawal.

## Phase 2 handoff
After approving metric definitions: generate a documented synthetic dataset, run relational/logic validation, calculate KPI baselines independently, then implement the dashboard in Looker Studio (formerly Google Data Studio).
