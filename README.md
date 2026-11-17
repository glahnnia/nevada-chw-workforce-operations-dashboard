# Nevada CHW Workforce Operations Dashboard

### Public Health Informatics | Workforce Analytics | Python | Google Data Studio

![Nevada CHW Workforce Operations Dashboard](assets/dashboard-preview.png)

**Project Overview**

The Nevada CHW Workforce Operations Dashboard is a public health informatics demonstration project designed to explore how standardized data collection, workforce analytics, and interactive reporting can support Community Health Worker (CHW) training programs across Nevada.

Developed using Python and Google Data Studio (formerly Looker Studio), the project integrates synthetic training enrollment records, learner progression indicators, completion outcomes, and geographic information into an interactive workforce reporting dashboard.

The project demonstrates a potential framework for strengthening statewide CHW workforce monitoring, supporting evidence-informed program planning, and identifying opportunities to improve training access and outcomes.

## Project Objectives

The dashboard was developed to demonstrate how public health organizations and workforce development programs could:

- Monitor CHW training enrollment and participation trends.
- Track unique learners and training cohort activity.
- Evaluate training completion rates across reporting periods.
- Compare training performance by language and geographic region.
- Visualize county-level workforce training participation across Nevada.
- Support standardized reporting and data-informed workforce planning.

## Dashboard Features

### 1. Workforce Enrollment and Participation

Interactive KPI scorecards summarize total enrollments, unique learners, and training cohorts, providing an overview of training participation.

### 2. Annual Enrollment Trends

A column chart displays changes in CHW training enrollment across 2024–2026, demonstrating how longitudinal reporting can support program monitoring and capacity planning.

### 3. Training Completion Performance

Annual completion-rate indicators and visualizations provide insight into training outcomes and potential changes in program performance over time.

### 4. Training Performance by Language

A comparative visualization examines completion rates for English- and Spanish-language CHW training, illustrating how disaggregated data can support program evaluation.

### 5. Regional Training Performance

Regional comparisons examine CHW training outcomes across Southern Nevada, Northern Nevada, Rural/Frontier communities, and records with unspecified geographic classification.

### 6. Nevada County Workforce Reach

An interactive geographic visualization displays enrollment distribution across Nevada counties using county-level geographic identifiers.

The map supports geographic exploration through county-specific hover information and enrollment counts, demonstrating how spatial analysis can complement traditional workforce reporting.

## Technical Approach

### Python: Data Preparation and Analysis

Python was used to prepare and analyze synthetic workforce datasets, including:

- Data processing and transformation
- Enrollment and learner-level aggregation
- Training completion and progression calculations
- Cohort-level performance summaries
- Annual, language, and regional KPI reporting
- County-level geographic data preparation
- Generation of structured CSV outputs for dashboard integration

### Google Data Studio: Visualization and Reporting

Google Data Studio was used to develop the interactive reporting interface, including:

- KPI scorecards
- Annual enrollment and completion charts
- Language and regional comparisons
- Geographic enrollment mapping
- Interactive data exploration
- Dashboard layout and visual presentation

### GitHub: Project Documentation and Reproducibility

GitHub serves as the repository for the project's analysis scripts, synthetic data, supporting documentation, and dashboard development resources.

## Repository Structure

```text
nevada-chw-workforce-operations-dashboard/
│
├── analysis/
│   └── Python analysis and KPI outputs
│
├── dashboard/
│   └── Dashboard development resources
│
├── data/
│   └── Synthetic CHW workforce datasets
│
├── documentation/
│   └── Project methodology and supporting documentation
│
├── .gitignore
│
└── README.md
```

## Data Sources and Methodology

This project uses synthetic CHW workforce data designed to demonstrate realistic training operations and reporting requirements.

The reporting period covers 2024–2026 and includes training enrollment, learner participation, cohort information, completion performance, and geographic classifications.

Python-generated summary datasets support the dashboard's visualizations. County-level geographic identifiers enable the display of enrollment distribution across Nevada.

**Data Disclaimer:** All learner records and reported outcomes are synthetic. They do not represent actual Nevada CHW training enrollment or completion statistics.

## Potential Applications

Nevada does not currently have a comprehensive, centralized statewide CHW workforce reporting system. This project explores how a standardized reporting framework could support future workforce data infrastructure.

Potential applications include:

- Statewide CHW training and certification pathway monitoring
- Workforce development reporting and program evaluation
- Geographic identification of training access disparities
- Language-access and training-equity assessments
- Grant performance monitoring
- Strategic workforce planning and resource allocation
- Collaboration among CHW training providers, employers, and public health organizations

With appropriate data governance, privacy protections, and standardized reporting practices, a similar framework could be adapted to real-world workforce information.

## Future Development Opportunities

Potential enhancements include:

- Integration with standardized statewide CHW workforce datasets
- Automated data validation and reporting workflows
- Expanded county-level workforce analytics
- Training progression and retention indicators
- Workforce certification and employment outcome reporting
- Historical comparisons and longitudinal workforce evaluation
- Improved interoperability between training organizations and reporting systems

## Project Significance

This project demonstrates the intersection of public health informatics, workforce development, geographic analysis, and applied data analytics.

Beyond the technical development of an interactive dashboard, it illustrates how structured reporting systems could strengthen organizational decision-making and provide greater visibility into CHW workforce training activities across Nevada.

The framework is intended as a foundation for exploring more coordinated, accessible, and evidence-informed approaches to public health workforce reporting.

---

**Project Type:** Public Health Informatics Portfolio Project  
**Technologies:** Python, CSV, Google Data Studio, GitHub  
**Geographic Focus:** Nevada, United States  
**Reporting Period:** 2024–2026  
**Data Classification:** Synthetic / Demonstration Data

**Developed by Glahnnia "Renee" Rates, MSHS, CCHW II**  
Public Health Informatics | Workforce Development | Data Analytics
