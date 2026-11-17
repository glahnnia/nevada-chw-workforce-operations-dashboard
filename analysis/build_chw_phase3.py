from pathlib import Path
from collections import Counter,defaultdict
from datetime import date,timedelta
import csv,json,statistics,zipfile,hashlib
ROOT=Path('/mnt/data/CHW Workforce Operations Dashboard')
DATA=ROOT/'data'; OUT=ROOT/'analysis'; DOC=ROOT/'documentation'; DASH=ROOT/'dashboard'
SNAP=date(2026,11,16)
def load(name):
 with (DATA/name).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def save(path,rows,fields=None):
 path.parent.mkdir(parents=True,exist_ok=True)
 fields=fields or (list(rows[0]) if rows else [])
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def dt(s):return date.fromisoformat(s) if s else None
def pct(n,d):return round(100*n/d,2) if d else None
def mean(values):return round(statistics.mean(values),2) if values else None
def median(values):return round(statistics.median(values),2) if values else None
learners=load('learners.csv');cohorts=load('cohorts.csv');enrollments=load('enrollments.csv');certs=load('certification_followup.csv');jobs=load('employment_followup.csv')
L={r['learner_id']:r for r in learners}; C={r['cohort_id']:r for r in cohorts}
for e in enrollments:
 e['cohort']=C[e['cohort_id']];e['learner']=L[e['learner_id']]
 e['eligible']=e['completion_eligible'].lower()=='true'
 e['progress']=int(e['modules_completed'])/int(e['modules_required'])*100 if int(e['modules_required']) else None
 e['duration']=(dt(e['completion_date'])-dt(e['enrollment_date'])).days if e['completion_date'] else None
 e['cohort_end']=dt(e['cohort']['cohort_end_date'])
 e['year']=e['cohort']['cohort_start_date'][:4]
 e['quarter']=f"{e['cohort_end'].year}-Q{(e['cohort_end'].month-1)//3+1}"

def base_metrics(rows):
 eligible=[e for e in rows if e['eligible']]
 completed=[e for e in eligible if e['enrollment_status']=='Completed']
 withdrawn=[e for e in eligible if e['enrollment_status']=='Withdrawn']
 valid=[e['progress'] for e in rows if e['progress'] is not None]
 return {'enrollments':len(rows),'unique_learners':len({e['learner_id'] for e in rows}), 'completion_eligible_enrollments':len(eligible),'completed_enrollments':len(completed),'withdrawn_enrollments':len(withdrawn),'completion_rate_pct':pct(len(completed),len(eligible)),'withdrawal_rate_pct':pct(len(withdrawn),len(eligible)),'average_module_progress_pct':mean(valid),'median_days_to_completion':median([e['duration'] for e in completed if e['duration'] is not None])}
summary=base_metrics(enrollments)
by_cohort=[]
for c in sorted(cohorts,key=lambda x:x['cohort_start_date']):
 rows=[e for e in enrollments if e['cohort_id']==c['cohort_id']]
 m=base_metrics(rows)
 by_cohort.append({'cohort_id':c['cohort_id'],'cohort_label':c['cohort_label'],'cohort_start_date':c['cohort_start_date'],'cohort_end_date':c['cohort_end_date'],'cohort_end_month':c['cohort_end_date'][:7], 'year':c['cohort_start_date'][:4], 'training_language':c['training_language'],'delivery_mode':c['delivery_mode'],'seat_capacity':int(c['seat_capacity']),'cohort_fill_rate_pct':pct(len(rows),int(c['seat_capacity'])),'cohort_complete_as_of_snapshot':str(dt(c['cohort_end_date'])<=SNAP).lower(),**m})
by_year=[]
for year in sorted({e['year'] for e in enrollments}):
 rows=[e for e in enrollments if e['year']==year]
 by_year.append({'year':year,**base_metrics(rows)})
by_region=[]
for region in sorted({e['learner']['region'] for e in enrollments}):
 rows=[e for e in enrollments if e['learner']['region']==region]
 by_region.append({'region':region,**base_metrics(rows)})
by_language=[]
for lang in ['English','Spanish']:
 rows=[e for e in enrollments if e['cohort']['training_language']==lang]
 by_language.append({'training_language':lang,**base_metrics(rows)})
by_quarter=[]
for q in sorted({e['quarter'] for e in enrollments}):
 rows=[e for e in enrollments if e['quarter']==q]
 by_quarter.append({'cohort_end_quarter':q,**base_metrics(rows)})
# Qualifying completion: most recent completed enrollment (by completion date, enrollment ID tie-break)
completed_by_learner=defaultdict(list)
for e in enrollments:
 if e['enrollment_status']=='Completed' and e['completion_date'] and dt(e['completion_date'])<=SNAP:
  completed_by_learner[e['learner_id']].append(e)
qualifying={k:max(v,key=lambda e:(e['completion_date'],e['enrollment_id'])) for k,v in completed_by_learner.items()}
# Only learners whose most recent completion is at least N calendar months before snapshot are followup eligible.
def add_months(d,n):
 y=d.year+(d.month-1+n)//12;m=(d.month-1+n)%12+1
 import calendar
 return date(y,m,min(d.day,calendar.monthrange(y,m)[1]))
cert_by_learner=defaultdict(list)
for r in certs:
 if dt(r['milestone_date'])<=SNAP:cert_by_learner[r['learner_id']].append(r)
job_by_learner=defaultdict(list)
for r in jobs:
 if dt(r['observation_date'])<=SNAP:job_by_learner[r['learner_id']].append(r)
# Certification observation after qualifying completion and on/before snapshot; coverage based on at least 3-month opportunity.
cert_eligible={k:e for k,e in qualifying.items() if add_months(dt(e['completion_date']),3)<=SNAP}
cert_obs={}
for k,e in cert_eligible.items():
 rows=[r for r in cert_by_learner[k] if dt(r['milestone_date'])>=dt(e['completion_date'])]
 if rows:cert_obs[k]=max(rows,key=lambda r:(r['milestone_date'],r['certification_record_id']))
certified=[r for r in cert_obs.values() if r['milestone']=='Certified']
# Independent 3/6 month follow-up, only matching months_after_completion counts (never guess from nearest observation)
follow={}
for months in [3,6]:
 eligible={k:e for k,e in qualifying.items() if add_months(dt(e['completion_date']),months)<=SNAP}
 observed={}
 for k,e in eligible.items():
  rows=[r for r in job_by_learner[k] if int(r['months_after_completion'])==months and dt(r['observation_date'])>=dt(e['completion_date'])]
  if rows:observed[k]=max(rows,key=lambda r:(r['observation_date'],r['employment_record_id']))
 known={k:r for k,r in observed.items() if r['employment_status']!='Unknown'}
 chw={k:r for k,r in known.items() if r['employment_status']=='Employed in CHW role'}
 follow[months]={'eligible':eligible,'observed':observed,'known':known,'chw':chw}
retention_baseline=follow[3]['chw']
# K13: 3-month CHW-employed + 6-month eligibility + KNOWN 6-month status; not same-employer retention.
retention_eligible={k:r for k,r in retention_baseline.items() if k in follow[6]['eligible']}
retention_known={k:r for k,r in retention_eligible.items() if k in follow[6]['known']}
retained={k:r for k,r in retention_known.items() if k in follow[6]['chw']}
# Separate eligible cohort outcome rates from in-progress records.
kpis=[
 ('K01','Total enrollments',summary['enrollments'],'enrollments',summary['enrollments'],'All enrollment records'),
 ('K02','Unique learners',summary['unique_learners'],'people',summary['enrollments'],'Distinct people across all enrollments'),
 ('K03','Enrollment by region',summary['enrollments'],'enrollments',summary['enrollments'],'Disaggregated in kpi_by_region.csv; Unknown retained'),
 ('K04','Cohort fill rate',None,'percent',None,'Cohort-specific metric in kpi_by_cohort.csv; do not average cohort rates without weights'),
 ('K05','Completion rate',summary['completion_rate_pct'],'percent',summary['completion_eligible_enrollments'],'Completed / completion-eligible enrollments'),
 ('K06','Withdrawal rate',summary['withdrawal_rate_pct'],'percent',summary['completion_eligible_enrollments'],'Withdrawn / completion-eligible enrollments'),
 ('K07','Average module progress',summary['average_module_progress_pct'],'percent',summary['enrollments'],'Mean modules_completed / modules_required across all valid enrollments'),
 ('K08','Median days to completion',summary['median_days_to_completion'],'days',summary['completed_enrollments'],'Calendar days from enrollment to completion'),
 ('K09','Certification follow-up coverage',pct(len(cert_obs),len(cert_eligible)),'percent',len(cert_eligible),'Latest completion >=3 months ago; any valid post-completion milestone'),
 ('K10','Observed certification attainment',pct(len(certified),len(cert_obs)),'percent',len(cert_obs),'Latest post-qualifying-completion milestone is Certified; synthetic scenario source'),
 ('K11','Employment follow-up coverage (3 months)',pct(len(follow[3]['observed']),len(follow[3]['eligible'])),'percent',len(follow[3]['eligible']),'3-month observation / 3-month eligible completers'),
 ('K12','Observed CHW employment rate (3 months)',pct(len(follow[3]['chw']),len(follow[3]['known'])),'percent',len(follow[3]['known']),'Known-status observations at 3 months only, not placement'),
 ('K13','Observed CHW retention 3-to-6 months',pct(len(retained),len(retention_known)),'percent',len(retention_known),'3-month CHW employed & 6-month observed known; employment retention, not same-employer'),
 ('K14','Completion trend',None,'percent',None,'Quarterly rate in kpi_by_end_quarter.csv; eligibility-filtered')]
kpi_rows=[]
for code,name,val,unit,den,notes in kpis:
 numerator={ 'K05':summary['completed_enrollments'],'K06':summary['withdrawn_enrollments'],'K09':len(cert_obs),'K10':len(certified),'K11':len(follow[3]['observed']),'K12':len(follow[3]['chw']),'K13':len(retained)}.get(code,'')
 kpi_rows.append({'kpi_id':code,'kpi_name':name,'value':val if val is not None else '', 'unit':unit,'numerator':numerator,'denominator':den if den is not None else '', 'as_of_date':SNAP.isoformat(),'methodology_note':notes})
# Follow-up coverage tables with fixed observation windows.
follow_rows=[]
for months in [3,6]:
 d=follow[months]
 follow_rows.append({'followup_month':months,'eligible_unique_completers':len(d['eligible']),'observed_unique_completers':len(d['observed']),'followup_coverage_pct':pct(len(d['observed']),len(d['eligible'])),'known_status_observations':len(d['known']),'unknown_status_observations':len(d['observed'])-len(d['known']),'employed_in_chw_role':len(d['chw']),'observed_chw_employment_rate_pct':pct(len(d['chw']),len(d['known']))})
# raw de-identified metrics join export for Looker Studio; one record per enrollment and no replicated follow-up.
dashboard_detail=[]
for e in enrollments:
 row={'enrollment_id':e['enrollment_id'],'learner_id':e['learner_id'],'cohort_id':e['cohort_id'],'cohort_label':e['cohort']['cohort_label'],'cohort_start_date':e['cohort']['cohort_start_date'],'cohort_end_date':e['cohort']['cohort_end_date'],'cohort_end_quarter':e['quarter'],'cohort_year':e['year'],'training_language':e['cohort']['training_language'],'delivery_mode':e['cohort']['delivery_mode'],'region':e['learner']['region'],'county':e['learner']['county'],'seat_capacity':e['cohort']['seat_capacity'],'enrollment_date':e['enrollment_date'],'enrollment_status':e['enrollment_status'],'completion_eligible':str(e['eligible']).lower(),'modules_required':e['modules_required'],'modules_completed':e['modules_completed'],'module_progress_pct':e['progress'],'completion_date':e['completion_date'],'days_to_completion':e['duration'] if e['duration'] is not None else ''}
 dashboard_detail.append(row)
save(OUT/'kpi_summary.csv',kpi_rows)
save(OUT/'kpi_by_cohort.csv',by_cohort)
save(OUT/'kpi_by_year.csv',by_year)
save(OUT/'kpi_by_region.csv',by_region)
save(OUT/'kpi_by_language.csv',by_language)
save(OUT/'kpi_by_end_quarter.csv',by_quarter)
save(OUT/'kpi_followup_windows.csv',follow_rows)
save(DASH/'looker_enrollment_detail.csv',dashboard_detail)
validation=[]
def check(name,ok,detail):validation.append({'check':name,'result':'PASS' if ok else 'FAIL','details':detail})
check('Unique primary keys',all(len({r[k] for r in rows})==len(rows) for rows,k in [(learners,'learner_id'),(cohorts,'cohort_id'),(enrollments,'enrollment_id'),(certs,'certification_record_id'),(jobs,'employment_record_id')]),'No duplicate row identifiers')
check('Foreign keys',all(e['learner_id'] in L and e['cohort_id'] in C for e in enrollments) and all(r['learner_id'] in L for r in certs+jobs),'All linked keys exist')
check('Enrollment counts reconcile',sum(r['enrollments'] for r in by_year)==len(enrollments) and sum(r['enrollments'] for r in by_region)==len(enrollments) and sum(r['enrollments'] for r in by_cohort)==len(enrollments),'Year, region, cohort all reconcile')
check('Eligibility aligns to snapshot',all(e['eligible']==(e['cohort_end']<=SNAP) for e in enrollments),'End date <= reporting snapshot')
check('Completed dates valid',all((not e['completion_date'] or (e['enrollment_status']=='Completed' and dt(e['enrollment_date'])<=dt(e['completion_date'])<=SNAP)) for e in enrollments),'Date range and status')
check('Completion rate baseline',summary['completion_rate_pct']==76.26,'Matches Phase 2 report')
check('Enrolled/unique baseline',summary['enrollments']==2616 and summary['unique_learners']==2450,'Matches Phase 2 report')
check('Followup distinct eligible persons',all(set(d['observed']).issubset(d['eligible']) and set(d['known']).issubset(d['observed']) for d in follow.values()),'No noneligible people used in rates')
check('No future records',all(dt(r['milestone_date'])<=SNAP for r in certs) and all(dt(r['observation_date'])<=SNAP for r in jobs),'All follow-ups are historical')
check('Cohort fill from raw counts',all(r['cohort_fill_rate_pct']==pct(r['enrollments'],r['seat_capacity']) for r in by_cohort),'Seat denominators consistent')
report={'snapshot_date':str(SNAP),'synthetic_only':True,'checks':validation,'all_passed':all(c['result']=='PASS' for c in validation),'baselines':summary,'cert_followup':{'eligible':len(cert_eligible),'observed':len(cert_obs),'certified_latest':len(certified)},'employment_followup':follow_rows,'retention':{'baseline_3month_chw_employed_6month_eligible':len(retention_eligible),'known_6month_status':len(retention_known),'retained_chw':len(retained)}, 'notes':['No observed outcome is proof of training attribution','Certification uses the latest observed milestone; not ever-certified','Retention measures CHW employment at 3 and 6 months, not employer continuity','2026 in-progress cohorts are in enrollment and progress but excluded from completion denominators']}
(DOC/'PHASE_3_VALIDATION_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
# notebook designed to run from project root, standard-library only, same definitions and outputs using accompanying script
notebook_cells=[]
def md(t):notebook_cells.append({'cell_type':'markdown','metadata':{},'source':t.splitlines(True)})
def code(t):notebook_cells.append({'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':t.splitlines(True)})
md('# CHW Workforce Operations Dashboard — Phase 3 Analysis\n\n**All data are synthetic** (not NVCHWA administrative records). Snapshot: **2026-11-16**.\n\nRun this notebook from the `analysis/` directory. Uses only Python standard library. The full phase-3 calculator is in `build_chw_phase3.py` under `analysis/`.')
code('from pathlib import Path\nimport csv, json, statistics\nROOT = Path.cwd().parent if Path.cwd().name == "analysis" else Path.cwd()\nDATA = ROOT / "data"\nANALYSIS = ROOT / "analysis"\ndef read_csv(path):\n    with path.open(newline="", encoding="utf-8-sig") as f:\n        return list(csv.DictReader(f))\nlearners = read_csv(DATA / "learners.csv")\ncohorts = read_csv(DATA / "cohorts.csv")\nenrollments = read_csv(DATA / "enrollments.csv")\ncertification = read_csv(DATA / "certification_followup.csv")\nemployment = read_csv(DATA / "employment_followup.csv")\nprint({"learners":len(learners),"cohorts":len(cohorts),"enrollments":len(enrollments),"certification":len(certification),"employment":len(employment)})\n')
md('## 1. Core KPIs\n\nCompletion and withdrawal denominators include only cohorts whose planned end date is on or before the snapshot. Enrollment and progress include all registrations, including still-active cohorts.')
code('summary = read_csv(ANALYSIS / "kpi_summary.csv")\nfor r in summary:\n    print(f"{r[\'kpi_id\']}: {r[\'kpi_name\']} = {r[\'value\'] or \'see breakdown\'} {r[\'unit\']}")\n')
md('## 2. Calculate a core metric independently\n\nThis cell calculates K05 directly from enrollment records; it should agree with the published KPI table.')
code('eligible = [r for r in enrollments if r["completion_eligible"].lower() == "true"]\ncompleted = [r for r in eligible if r["enrollment_status"] == "Completed"]\ncompletion_pct = round(100 * len(completed) / len(eligible), 2)\nprint("Completion rate:", completion_pct, "%", "(", len(completed), "/", len(eligible), ")")\nassert str(completion_pct) == next(r["value"] for r in summary if r["kpi_id"] == "K05")\n')
md('## 3. Group comparisons\n\nThese precomputed tables use the exact same definitions as the KPI summary. Regional and language differences are descriptive patterns in simulated data.')
code('for filename in ("kpi_by_year.csv", "kpi_by_region.csv", "kpi_by_language.csv"):\n    print("\\n", filename)\n    for r in read_csv(ANALYSIS / filename):\n        label = r.get("year", r.get("region", r.get("training_language")))\n        print(label, "enrollments:", r["enrollments"], "completion:", r["completion_rate_pct"], "%")\n')
md('## 4. Follow-up outcomes and selection\n\nOnly 3- or 6-month eligible completers are in each coverage denominator. Unknown employment status is **not** treated as unemployment; observed CHW employment rates exclude Unknown. Certification uses the latest valid post-completion milestone after the most recent completion, and does not represent the share of all completers certified.')
code('for r in read_csv(ANALYSIS / "kpi_followup_windows.csv"):\n    print(f"{r[\'followup_month\']}-month: {r[\'observed_unique_completers\']}/{r[\'eligible_unique_completers\']} observed; coverage {r[\'followup_coverage_pct\']}%; known employment {r[\'known_status_observations\']}; observed CHW employment {r[\'observed_chw_employment_rate_pct\']}%")\n')
md('## 5. Check validation and build dashboard exports\n\n`build_chw_phase3.py` is a fully reproducible standard-library calculator. Run it when updating Phase 2 CSVs, then rerun this notebook.')
code('report = json.loads((ROOT / "documentation" / "PHASE_3_VALIDATION_REPORT.json").read_text())\nassert report["all_passed"]\nprint("Validation checks:", len(report["checks"]), "passed")\nprint("Dashboard enrollment rows:", len(read_csv(ROOT / "dashboard" / "looker_enrollment_detail.csv")))\n')
md('## 6. Interpretation and limitations\n\n- All figures are **fabricated demonstration values**, never Nevada CHW benchmark statistics.\n- A learner with repeat enrollment counts once for K02, but multiple times for K01.\n- Follow-up data are limited to those with qualifying training completion and observed records.\n- Differences between groups and employment outcomes are **not causal evidence**.\n- Cohort fill rate can exceed 100% by design; do not cap at 100%.\n- Quarterly completion trends group enrollments by their cohort planned end quarter, not by individual completion date.\n- CHW retention is persistence of CHW employment status from 3 to 6 months, not same-employer tenure.\n')
nb={'cells':notebook_cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},'nbformat':4,'nbformat_minor':5}
(OUT/'CHW_Workforce_KPI_Analysis.ipynb').write_text(json.dumps(nb,indent=1),encoding='utf-8')
# create readable report with numerator / denominator details
kmap={r['kpi_id']:r for r in kpi_rows}
lines=['# Phase 3 — KPI Analysis Report','',f'**Snapshot:** {SNAP.isoformat()}  ','**Data classification:** Entirely synthetic; no actual NVCHWA outcomes or benchmark comparisons.','', '## Executive summary',f"- **{summary['enrollments']:,}** training enrollments across **{summary['unique_learners']:,}** distinct learners and **{len(cohorts)}** cohorts.",f"- **{summary['completed_enrollments']:,} / {summary['completion_eligible_enrollments']:,}** completion-eligible enrollments completed (**{summary['completion_rate_pct']}%**).",f"- **{summary['withdrawn_enrollments']:,} / {summary['completion_eligible_enrollments']:,}** completion-eligible enrollments withdrew (**{summary['withdrawal_rate_pct']}%**).",f"- Average progress across all enrollments: **{summary['average_module_progress_pct']}%**; median completed enrollment duration: **{summary['median_days_to_completion']} calendar days**.",'','## Enrollment trend (by cohort start year)','', '| Year | Enrollments | Distinct learners within year | Eligible | Completed | Completion rate |','|---|---:|---:|---:|---:|---:|']
for r in by_year:lines.append(f"| {r['year']} | {r['enrollments']} | {r['unique_learners']} | {r['completion_eligible_enrollments']} | {r['completed_enrollments']} | {r['completion_rate_pct']}% |")
lines+=['','**Note:** Annual distinct learner totals cannot be added to obtain the overall distinct learner count because some people appear in more than one year.','', '## Regional distribution','','| Region | Enrollments | Eligible | Completion rate |','|---|---:|---:|---:|']
for r in by_region:lines.append(f"| {r['region']} | {r['enrollments']} | {r['completion_eligible_enrollments']} | {r['completion_rate_pct']}% |")
lines+=['','## Training language','','| Class language | Enrollments | Eligible | Completion rate |','|---|---:|---:|---:|']
for r in by_language:lines.append(f"| {r['training_language']} | {r['enrollments']} | {r['completion_eligible_enrollments']} | {r['completion_rate_pct']}% |")
lines+=['','## Workforce pathway observations (not training-attributable)','',f"- Certification K09: **{len(cert_obs)} / {len(cert_eligible)}** eligible completers observed (**{kmap['K09']['value']}%** coverage, using a 3-month eligibility threshold).",f"- Certification K10: **{len(certified)} / {len(cert_obs)}** observed completers had latest milestone *Certified* (**{kmap['K10']['value']}%**). This is not an ever-certified measure."]
for r in follow_rows: lines.append(f"- Employment {r['followup_month']}-month coverage: **{r['observed_unique_completers']} / {r['eligible_unique_completers']}** (**{r['followup_coverage_pct']}%**); CHW employment among known statuses: **{r['employed_in_chw_role']} / {r['known_status_observations']}** (**{r['observed_chw_employment_rate_pct']}%**), Unknown: **{r['unknown_status_observations']}**.")
lines.append(f"- Employment status retention K13: **{len(retained)} / {len(retention_known)}** (**{kmap['K13']['value']}%**) of 3-month CHW-employed completers with known 6-month status remained CHW-employed. Baseline with 6-month opportunity: {len(retention_eligible)}.")
lines+=['','## Dashboard handoff','', '- `dashboard/looker_enrollment_detail.csv`: one enrollment per row; use COUNT_DISTINCT(`learner_id`) for learner counts; DO NOT sum `seat_capacity` on this detail table (it is repeated per enrollment).','- `analysis/kpi_by_cohort.csv`: one cohort per row including correct capacity and fill rate.','- `analysis/kpi_by_end_quarter.csv`: quarterly completion trend (by cohort planned end quarter).','- `analysis/kpi_followup_windows.csv`: use this table for observed employment rates/coverage; do not join follow-up tables directly to enrollment detail because repeated enrollments could duplicate outcomes.','- `analysis/kpi_summary.csv`: global scorecard values with denominator and methods.','','## Limits and interpretation','','1. Synthetic records cannot establish actual workforce outcomes, causal effects, or statewide trends.','2. Completion eligibility requires cohort planned end on/before snapshot; training progress includes active cohorts.','3. Certification is latest recorded milestone after most recent completion, not cumulative ever-certified status.','4. Follow-up is observation-based; rates exclude unobserved people, and employment Unknown is not Unemployed.','5. For retention, an employment status at both dates is not proof of the same employer or continuous employment.','6. Cohort composition can change observed subgroup rates. Do not infer explanations from simulated differences.','7. Seven cohorts may be over planned seat capacity; exceeding 100% fill is intentional and valid.','', '## Next phase','Build Looker Studio pages: Executive Overview, Training Operations, and exploratory Workforce Pathways. Use page-level notes stating **Synthetic data — demonstration only**.']
(OUT/'PHASE_3_ANALYSIS_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
# script copied for reproducibility next to notebook
from shutil import copyfile
copyfile(Path(__file__),OUT/'build_chw_phase3.py')
zip_path=Path('/mnt/data/CHW_Workforce_Operations_Dashboard_Phase3.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in ROOT.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(ROOT.parent))
print(json.dumps({'zip':str(zip_path),'summary':summary,'followup':follow_rows,'cert':{'eligible':len(cert_eligible),'observed':len(cert_obs),'certified':len(certified)},'retention':{'known':len(retention_known),'retained':len(retained)},'checks_passed':report['all_passed']},indent=2))
