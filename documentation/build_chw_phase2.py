import csv, random, json, zipfile, shutil, statistics
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

R=random.Random(20261116)
ASOF=date(2026,11,16)
root=Path('/mnt/data/CHW Workforce Operations Dashboard')
data=root/'data'; docs=root/'documentation'; analysis=root/'analysis'
for p in (data,docs,analysis):p.mkdir(parents=True,exist_ok=True)

COUNTIES={
'Clark':'Southern Nevada','Washoe':'Northern Nevada','Carson City':'Northern Nevada',
'Douglas':'Northern Nevada','Storey':'Northern Nevada',
'Churchill':'Rural/Frontier','Elko':'Rural/Frontier','Esmeralda':'Rural/Frontier',
'Eureka':'Rural/Frontier','Humboldt':'Rural/Frontier','Lander':'Rural/Frontier',
'Lincoln':'Rural/Frontier','Lyon':'Rural/Frontier','Mineral':'Rural/Frontier',
'Nye':'Rural/Frontier','Pershing':'Rural/Frontier','White Pine':'Rural/Frontier'}
county_names=list(COUNTIES)+['Unknown']
county_weights=[45,25,4,3,1,2,3,1,1,2,1,1,3,1,3,1,2,1]

def fmt(d):return d.isoformat() if d else ''
def weighted(keys,weights):return R.choices(keys,weights=weights,k=1)[0]
def output(name,headers,rows):
    with (data/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=headers);w.writeheader();w.writerows(rows)

def date_add_months(d,months):
    y=(d.year*12+d.month-1+months)//12;m=(d.year*12+d.month-1+months)%12+1
    import calendar
    return date(y,m,min(d.day,calendar.monthrange(y,m)[1]))

# Fictional seasons: 12 cohorts/year, each with distinct capacity and language.
cohorts=[]
for year in (2024,2025,2026):
    for season,mon in [('Winter',1),('Spring',4),('Summer',7),('Fall',10)]:
        for track,lang in [('A','English'),('B','English'),('S','Spanish')]:
            start=date(year,mon,10 if track=='A' else 12 if track=='B' else 15)
            end=start+timedelta(days=55 if track!='S' else 62)
            mode=weighted(['Virtual','Hybrid','In-person'],[75,20,5])
            cap=R.randint(78,105) if lang=='English' else R.randint(57,80)
            cohorts.append(dict(cohort_id=f'C{year}{mon:02d}{track}',cohort_label=f'{year} {season} {track}',cohort_start_date=fmt(start),cohort_end_date=fmt(end),training_language=lang,delivery_mode=mode,seat_capacity=cap))

# Target 2450 fictional individuals plus 125 repeat-class registrations.
N=2450
learners=[]
for i in range(1,N+1):
    county=weighted(county_names,county_weights)
    lang=weighted(['English','Spanish','Other','Unknown'],[79,18,2,1])
    learners.append(dict(learner_id=f'L{i:05d}',county=county,region=COUNTIES.get(county,'Unknown'),preferred_training_language=lang,registration_date=''))

# Assign people to first cohort with enough coverage through 2026.
first_assign=[R.choice(cohorts) for _ in learners]
# repeats ensure first cohort earlier than second.
repeat_ids=R.sample(range(N),125)
assignments=[(i,c) for i,c in enumerate(first_assign)]
for i in repeat_ids:
    first=first_assign[i]
    later=[c for c in cohorts if c['cohort_start_date']>first['cohort_end_date']]
    if later: assignments.append((i,R.choice(later)))
# Explicit overcapacity achieved in a few cohorts via additional assignments that remain unique learner/cohort.
for target in [cohorts[4],cohorts[22]]:
    current=sum(c['cohort_id']==target['cohort_id'] for _,c in assignments)
    desired=int(target['seat_capacity'])*11//10+2
    pool=[i for i in range(N) if all(not (j==i and c['cohort_id']==target['cohort_id']) for j,c in assignments) and first_assign[i]['cohort_start_date']>=target['cohort_start_date']]
    R.shuffle(pool)
    for i in pool[:max(0,desired-current)]:
        # For this illustrative scenario, allow unique person multiple enrollments but only one per cohort.
        assignments.append((i,target))

assignments.sort(key=lambda t:(t[1]['cohort_start_date'],t[0]))
enrollments=[]; completion_by_learner=defaultdict(list)
for k,(i,c) in enumerate(assignments,1):
    lid=learners[i]['learner_id']
    start=date.fromisoformat(c['cohort_start_date']);end=date.fromisoformat(c['cohort_end_date'])
    enroll=start-timedelta(days=R.randint(4,50))
    first_act=start+timedelta(days=R.randint(0,13))
    eligible=end<=ASOF
    complete=withdraw=None
    if not eligible:
        status=weighted(['In Progress','Not Started','Withdrawn'],[78,9,13])
    else:
        status=weighted(['Completed','Withdrawn','Enrolled','Not Started'],[76,17,4,3])
    if status=='Completed':
        complete=end-timedelta(days=R.randint(0,12));completed=8
    elif status=='Withdrawn':
        withdraw=min(ASOF,end)-timedelta(days=R.randint(0,35));withdraw=max(first_act,withdraw);completed=R.randint(0,6)
    elif status=='In Progress': completed=R.randint(1,7)
    else:completed=0
    if status in ('Not Started','Enrolled'):activity=''
    else:activity=fmt(min(first_act,complete or withdraw or ASOF))
    if status=='Completed':completion_by_learner[lid].append(complete)
    enrollments.append(dict(enrollment_id=f'E{k:05d}',learner_id=lid,cohort_id=c['cohort_id'],enrollment_date=fmt(enroll),enrollment_status=status,first_activity_date=activity,completion_date=fmt(complete),withdrawal_date=fmt(withdraw),modules_required=8,modules_completed=completed,completion_eligible=str(eligible).lower()))
    if not learners[i]['registration_date'] or fmt(enroll)<learners[i]['registration_date']:learners[i]['registration_date']=fmt(enroll)

certifications=[]; employment=[]
for lid,dates in completion_by_learner.items():
    anchor=max(dates) # most recent eligible completion, as specified in KPI framework
    age=(ASOF-anchor).days
    if age>=30 and R.random()<0.72:
        level=weighted(['CHW I','CHW II'],[87,13])
        milestone_dt=anchor+timedelta(days=R.randint(15,min(80,age)))
        outcome=weighted(['Planning to Apply','Applied','Certified','Not Certified','Unknown'],[18,22,43,9,8])
        if outcome in ('Certified','Applied') and age>=65 and R.random()<0.45:
            cert_date=anchor+timedelta(days=R.randint(15,min(50,age)))
            certifications.append(dict(certification_record_id=f'CF{len(certifications)+1:05d}',learner_id=lid,certification_level=level,milestone='Applied',milestone_date=fmt(cert_date),verification_source='Synthetic scenario'))
            if outcome=='Certified':milestone_dt=max(milestone_dt,cert_date+timedelta(days=R.randint(1,10)))
        certifications.append(dict(certification_record_id=f'CF{len(certifications)+1:05d}',learner_id=lid,certification_level=level,milestone=outcome,milestone_date=fmt(min(milestone_dt,ASOF)),verification_source='Synthetic scenario'))
    prior_status=None;prior_start=None
    for months in (3,6):
        observation=date_add_months(anchor,months)
        if observation>ASOF:continue
        if R.random()> (0.76 if months==3 else 0.61):continue
        if prior_status=='Employed in CHW role':
            status=weighted(['Employed in CHW role','Employed in other role','Unemployed seeking work','Not seeking work','Unknown'],[77,12,6,2,3])
        else:
            status=weighted(['Employed in CHW role','Employed in other role','Unemployed seeking work','Not seeking work','Unknown'],[47 if months==3 else 53,25,17 if months==3 else 12,5,6 if months==3 else 5])
        sector=weighted(['Healthcare','Community nonprofit','Government','Other'],[47,32,15,6]) if status=='Employed in CHW role' else weighted(['Healthcare','Community nonprofit','Government','Other'],[28,16,13,43]) if status=='Employed in other role' else 'Unknown'
        start_date=(anchor+timedelta(days=R.randint(10,max(11,(observation-anchor).days)))) if status.startswith('Employed') else None
        if status=='Employed in CHW role' and prior_status==status and prior_start:start_date=prior_start
        employment.append(dict(employment_record_id=f'EF{len(employment)+1:05d}',learner_id=lid,observation_date=fmt(observation),months_after_completion=months,employment_status=status,employer_sector=sector,employment_start_date=fmt(start_date),verification_source='Synthetic scenario'))
        prior_status=status;prior_start=start_date

# CSV files and validations.
headers={
'learners.csv':['learner_id','county','region','preferred_training_language','registration_date'],
'cohorts.csv':['cohort_id','cohort_label','cohort_start_date','cohort_end_date','training_language','delivery_mode','seat_capacity'],
'enrollments.csv':['enrollment_id','learner_id','cohort_id','enrollment_date','enrollment_status','first_activity_date','completion_date','withdrawal_date','modules_required','modules_completed','completion_eligible'],
'certification_followup.csv':['certification_record_id','learner_id','certification_level','milestone','milestone_date','verification_source'],
'employment_followup.csv':['employment_record_id','learner_id','observation_date','months_after_completion','employment_status','employer_sector','employment_start_date','verification_source']}
tables={'learners.csv':learners,'cohorts.csv':cohorts,'enrollments.csv':enrollments,'certification_followup.csv':certifications,'employment_followup.csv':employment}
for name,rows in tables.items():output(name,headers[name],rows)

errors=[]
def check(x,msg):
    if not x:errors.append(msg)
L={x['learner_id'] for x in learners};C={x['cohort_id']:x for x in cohorts}
check(len(L)==len(learners),'Nonunique learner ID')
check(len(C)==len(cohorts),'Nonunique cohort ID')
check(len({x['enrollment_id'] for x in enrollments})==len(enrollments),'Nonunique enrollment ID')
check(len({(x['learner_id'],x['cohort_id']) for x in enrollments})==len(enrollments),'Repeated learner/cohort pair')
check(all(x['learner_id'] in L and x['cohort_id'] in C for x in enrollments),'Orphan enrollment')
check(all(x['learner_id'] in L for x in certifications+employment),'Orphan followup')
check(all(0<=x['modules_completed']<=x['modules_required'] for x in enrollments),'Module bounds')
check(all(bool(x['completion_date'])==(x['enrollment_status']=='Completed') for x in enrollments),'Completion dates/status')
check(all(bool(x['withdrawal_date'])==(x['enrollment_status']=='Withdrawn') for x in enrollments),'Withdrawal dates/status')
check(all(x['completion_eligible']==str(date.fromisoformat(C[x['cohort_id']]['cohort_end_date'])<=ASOF).lower() for x in enrollments),'Eligibility consistency')
check(all(x['enrollment_status']!='Completed' or (x['completion_date']>=x['enrollment_date'] and x['completion_date']<=fmt(ASOF)) for x in enrollments),'Completion chronology')
check(all(x['enrollment_status']!='Withdrawn' or (x['withdrawal_date']>=x['enrollment_date'] and x['withdrawal_date']<=fmt(ASOF)) for x in enrollments),'Withdrawal chronology')
check(all(date.fromisoformat(x['observation_date'])<=ASOF and x['learner_id'] in completion_by_learner and x['observation_date']==fmt(date_add_months(max(completion_by_learner[x['learner_id']]),x['months_after_completion'])) for x in employment),'Follow-up dates/windows')
check(all(x['milestone_date']<=fmt(ASOF) for x in certifications),'Certification future dates')
check(all(x['employment_start_date']=='' or x['employment_start_date']<=x['observation_date'] for x in employment),'Employment future start dates')
check(all(x['county'] in county_names and x['region']==COUNTIES.get(x['county'],'Unknown') for x in learners),'Region mapping')
check(all(x['registration_date'] for x in learners),'Learner missing registration date')
check(len({x['certification_record_id'] for x in certifications})==len(certifications),'Certification ID collision')
check(len({x['employment_record_id'] for x in employment})==len(employment),'Employment ID collision')
check(len({(x['learner_id'],x['months_after_completion']) for x in employment})==len(employment),'Duplicate employment observation')

eligible=[x for x in enrollments if x['completion_eligible']=='true']
completed=[x for x in eligible if x['enrollment_status']=='Completed']
withdrawn=[x for x in eligible if x['enrollment_status']=='Withdrawn']
cohort_enrollment=Counter(x['cohort_id'] for x in enrollments)
overcapacity=[c['cohort_id'] for c in cohorts if cohort_enrollment[c['cohort_id']]>c['seat_capacity']]
summary={
 'snapshot_date':fmt(ASOF),'synthetic_only':True,'seed':20261116,'file_row_counts':{k:len(v) for k,v in tables.items()},
 'eligible_enrollments':len(eligible),'completed_eligible_enrollments':len(completed),
 'completion_rate_pct':round(100*len(completed)/len(eligible),2),
 'withdrawal_rate_pct':round(100*len(withdrawn)/len(eligible),2),
 'unique_learners':len(L),'repeat_enrollment_learners':sum(n>1 for n in Counter(x['learner_id'] for x in enrollments).values()),
 'cohorts_over_capacity':overcapacity,'yearly_enrollments':dict(sorted(Counter(C[x['cohort_id']]['cohort_start_date'][:4] for x in enrollments).items())),
 'validation_checks':'PASS' if not errors else 'FAIL','errors':errors}
(docs/'PHASE_2_VALIDATION_REPORT.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
(docs/'PHASE_2_METHODOLOGY.md').write_text('''# Phase 2 — Synthetic Dataset Methodology

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
''',encoding='utf-8')
# ship script in documentation for reproduction
shutil.copyfile(__file__,docs/'build_chw_phase2.py')
zip_path=Path('/mnt/data/CHW_Workforce_Operations_Dashboard_Phase2.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(root.rglob('*')):
  if f.is_file():z.write(f,arcname=f.relative_to(root.parent))
print(json.dumps(summary,indent=2))
print('zip',zip_path,zip_path.stat().st_size)
