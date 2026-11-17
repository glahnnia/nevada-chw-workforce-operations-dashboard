# Phase 2 — Synthetic Dataset Methodology

**All records are entirely fictional.** They are simulated for portfolio demonstration and do not describe actual NVCHWA trainees, certification records, employment or outcomes.

- **Snapshot:** 2026-11-16 (no observations later than this date).
- **Reproducibility:** generated using Python standard-library `random.Random(20261116)`; run the accompanying `build_chw_phase2.py` from the package's parent folder or adapt the `root` path.
- **Population:** 2,450 fictional learners, 36 fictional cohorts covering 2024–2026, multiple enrollments per person permitted, unique learner/cohort pair.
- **Geography:** synthetic distribution across 17 Nevada counties plus Unknown; counties grouped into Northern Nevada, Southern Nevada, Rural/Frontier. This mapping is a project convention rather than a statewide official definition.
- **Training:** annual Winter/Spring/Summer/Fall cohorts, two illustrative English groups and one Spanish group per season; simulated capacities and delivery modes. These are **not actual NVCHWA cohort schedules**.
- **Status:** cohort end date on/before snapshot determines completion eligibility. Completed, Withdrawn, Enrolled, Not Started, and In Progress are intentionally distinct. All rows have eight required modules; progress may be incomplete despite eligibility.
- **Follow-up:** optional certification observations and 3-/6-month employment observations occur only for learners with completion dates; qualifying completion for workforce analysis is the latest completion date. No record means missing follow-up, not an adverse outcome. Synthetic scenario is explicitly marked in both follow-up tables.
- **Employment start date:** simulated reported start date for employed statuses; unknown otherwise. Repeated CHW employment statuses simulate possible retention but are not same-employer retention.
- **Analysis caution:** certification and employment are not necessarily caused by CHW training. Synthetic rates must never be presented as empirical findings or benchmark performance.

The validation report reports row counts, completion and withdrawal rate baselines, and referential-integrity/date checks. The data dictionary and KPI framework in Phase 1 remain the definitions of record.
