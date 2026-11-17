# CHW Workforce Operations Dashboard — Synthetic Data Dictionary (v1.0)

**Status:** Proposed schema; no records have been generated. All future records will be fictional and clearly labeled synthetic.

## Purpose and grain
A relational synthetic dataset representing CHW training operations and optional post-training follow-up. `learners` has one row per fictional person; `cohorts` has one row per class cohort; `enrollments` has one row per person-cohort registration; `certification_followup` has one row per learner's reported certification milestone; `employment_followup` has one row per learner per follow-up observation. This design accommodates people who enroll more than once and prevents double-counting.

## 1. learners.csv — one row per fictional learner
| Field | Type | Allowed values / meaning | Required? |
|---|---|---|---|
| learner_id | string | Unique opaque ID, e.g. L0001 | Yes |
| county | string | Nevada county, or Unknown; location at enrollment | Yes |
| region | string | Northern Nevada, Southern Nevada, Rural/Frontier, Unknown; based on documented project mapping | Yes |
| preferred_training_language | enum | English, Spanish, Other, Unknown | Yes |
| registration_date | date | YYYY-MM-DD; earliest registration in dataset | Yes |

## 2. cohorts.csv — one row per class cohort
| Field | Type | Allowed values / meaning | Required? |
|---|---|---|---|
| cohort_id | string | Unique cohort ID | Yes |
| cohort_label | string | e.g. 2026 Spring A | Yes |
| cohort_start_date | date | YYYY-MM-DD | Yes |
| cohort_end_date | date | YYYY-MM-DD; planned end date | Yes |
| training_language | enum | English, Spanish | Yes |
| delivery_mode | enum | Virtual, In-person, Hybrid | Yes |
| seat_capacity | integer | Positive planned cohort capacity | Yes |

## 3. enrollments.csv — one row per learner per cohort registration
| Field | Type | Allowed values / meaning | Required? |
|---|---|---|---|
| enrollment_id | string | Unique enrollment ID | Yes |
| learner_id | string | Foreign key -> learners.learner_id | Yes |
| cohort_id | string | Foreign key -> cohorts.cohort_id | Yes |
| enrollment_date | date | YYYY-MM-DD | Yes |
| enrollment_status | enum | Enrolled, In Progress, Completed, Withdrawn, Not Started | Yes |
| first_activity_date | date | Date of first class activity; blank if none | No |
| completion_date | date | Date requirements fulfilled; only for Completed | No |
| withdrawal_date | date | Date learner withdrew; only for Withdrawn | No |
| modules_required | integer | Required modules for that enrollment | Yes |
| modules_completed | integer | Completed modules; 0 through modules_required | Yes |
| completion_eligible | boolean | Whether enrollment has reached sufficient observation time to be evaluated for completion | Yes |

## 4. certification_followup.csv — zero or more milestones per learner
| Field | Type | Allowed values / meaning | Required? |
|---|---|---|---|
| certification_record_id | string | Unique follow-up ID | Yes |
| learner_id | string | Foreign key -> learners | Yes |
| certification_level | enum | CHW I, CHW II | Yes |
| milestone | enum | Planning to Apply, Applied, Certified, Not Certified, Unknown | Yes |
| milestone_date | date | Date of milestone or observation | Yes |
| verification_source | enum | Self-reported, Verified record, Synthetic scenario | Yes |

## 5. employment_followup.csv — zero or more follow-up observations per learner
| Field | Type | Allowed values / meaning | Required? |
|---|---|---|---|
| employment_record_id | string | Unique observation ID | Yes |
| learner_id | string | Foreign key -> learners | Yes |
| observation_date | date | Date status was recorded | Yes |
| months_after_completion | integer | Relative to learner's qualifying completed enrollment; nonnegative | Yes |
| employment_status | enum | Employed in CHW role, Employed in other role, Unemployed seeking work, Not seeking work, Unknown | Yes |
| employer_sector | enum | Healthcare, Community nonprofit, Government, Other, Unknown | No |
| employment_start_date | date | Start date for reported role, if known | No |
| verification_source | enum | Self-reported, Verified record, Synthetic scenario | Yes |

## Relationships, privacy, and validation
- One learner may have multiple enrollments, certification milestones, and employment observations.
- `enrollment_id`, not `learner_id`, is the default count unit for class operations. Distinct `learner_id` counts are labeled **unique learners**.
- Each learner/cohort pair should be unique in the initial implementation; changes to this rule require a documented reenrollment policy.
- Cohort end >= start; completed modules <= required modules; completion/withdrawal dates align with corresponding status; no future follow-up for a historical dashboard snapshot.
- Separate **Unknown** from **No/Not certified/Unemployed**. No follow-up record does not mean a negative outcome.
- Geographic and language data are descriptive, never proxies for personal or protected identities.
- No real names, emails, phone numbers, birthdates, or student records. Synthetic records must not be presented as actual NVCHWA results.

## Decisions to confirm before generating data
1. Synthetic cohort years and number of cohorts.
2. Whether cohort language and delivery mode should reflect illustrative Nevada operations or a fully hypothetical training program.
3. Whether certification and employment follow-up will be included in dashboard v1 or displayed as an optional exploratory page.
