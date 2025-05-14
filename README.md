# PV-BESS
Integrated Solar PV and Energy Storage Architecture for Sites in Muscat, Oman
Project Overview
This repository hosts a cutting-edge technical framework and decision-making support tool for evaluating Battery Energy Storage System (BESS) integration at two sites in Muscat, Oman:

Load Site (Jindal Steel Facility): Integrates grid power, on-site solar photovoltaic (PV) generation, and a BESS to optimize energy costs through tariff arbitrage, peak shaving, and solar self-consumption for a commercial/industrial facility.
Solar PV Generator Site (Shinas Solar Plant): A utility-scale solar farm designed for grid export, compliant with Oman's transmission network requirements.

The architectures are tailored to Oman's regulatory environment, including the Oman Grid Code, Oman Electrical Standards (OES), and the 2025 Cost-Reflective Tariff (CRT) structure. The project aligns with Oman’s Vision 2040 and net-zero 2050 goals, aiming to set a global benchmark for sustainable, intelligent energy systems.
The core deliverable is a consultant-grade report and dashboard suite built in Python, leveraging libraries like Pandas, NumPy, SciPy, Streamlit, and Matplotlib for dynamic visualization and advanced analytics. The suite evaluates BESS technologies (Lithium Iron Phosphate [LFP], Sodium-Sulfur [NAS], and emerging options like solid-state and flow batteries), optimizes dispatch strategies, and provides technical, financial, and operational insights. Futuristic features include AI-driven optimization, blockchain for energy trading, and quantum-ready frameworks, positioning the project for scalability and innovation by 2030.
Objectives

Develop compliant, efficient electrical and control architectures for both sites.
Optimize energy costs at Jindal Steel using solar PV and BESS, targeting near-100% renewable utilization.
Maximize grid export and renewable energy integration at Shinas Solar Plant.
Deliver a professional report and interactive dashboard suite with predictive analytics, financial metrics, and risk analysis.
Ensure safety, reliability, and compliance with Omani regulations (APSR, OETC) and international standards (e.g., IEEE 1547, IEEE 2030.5, NFPA 855).
Future-proof the framework with AI, blockchain, and quantum computing for global scalability and sustainability.

Repository Structure
├── data/                     # Input data for analysis
│   ├── tariffs/              # CRT tariff data (CSV/JSON)
│   ├── loads/                # Jindal Steel load profiles (CSV)
│   ├── pv/                   # Shinas Solar Plant generation data (CSV)
│   ├── weather/              # Solar irradiance and temperature data (CSV)
│   └── sample/               # Example datasets
├── src/                      # Source code for the decision-making tool
│   ├── bess_model/           # Python modules for BESS simulation and optimization
│   ├── streamlit/            # Streamlit scripts for dashboards and UI
│   ├── ai_forecasting/       # ML models for load, PV, and tariff prediction
│   ├── blockchain/           # Smart contracts for energy trading
│   └── utils/                # Helper scripts for data processing
├── docs/                     # Documentation and reports
│   ├── architecture_design.md # System architecture details
│   ├── regulatory_framework.md # Oman regulations and tariffs
│   ├── tool_guide.md         # Decision-making tool usage guide
│   └── bess_report.pdf       # Consultant-grade BESS evaluation report
├── tests/                    # Test scripts and validation datasets
├── requirements.txt          # Python dependencies
├── LICENSE                   # License file
└── README.md                 # This file

Inputs Considered for Calculations
Technical Inputs

High-Resolution Load Profiles: Jindal Steel facility (12+ months, 15-minute or sub-minute intervals via IoT sensors).
PV Generation Data: Shinas Solar Plant (synchronized with load, ~1900-2000 kWh/kWp/year).
Grid Tariff Structures: 2025 CRT, including time-of-use (ToU), wheeling charges (5 OMR/MWh for direct sales), TUoS, and DUoS.
Battery Parameters:
LFP: 6,000-12,000 cycles, 85-92% RTE, temperature-sensitive, $165-$275/kWh.
NAS: 4,500 cycles, >80% RTE, <1% annual degradation, $150-$200/kWh.
Emerging Options: Solid-state (>300 Wh/kg, 20,000 cycles), flow batteries (70-80% RTE, long-duration).
Metrics: C-rate, energy density, cycle life, safety, environmental impact.


Site Constraints: Space, grid connection capacity (11kV/33kV for Jindal, 132kV+ for Shinas), budget, regulatory limits.
Weather Data: Solar irradiance and temperature from Oman’s meteorological service or NASA POWER database.

Financial Inputs

Capital Expenditure (CapEx): BESS, PV systems, installation, commissioning, IoT/SCADA infrastructure.
Operational Expenditure (OpEx): Maintenance, auxiliary power (e.g., HVAC for LFP, thermal management for NAS), cybersecurity.
Other Costs: Grid connection fees, end-of-life recycling, tax incentives (e.g., 10-year exemptions in free zones), depreciation schedules.
Future Costs: Projected declines in solid-state/flow battery CapEx by 2030.

Reference Data

Benchmarks: Performance and financial data from GCC and India BESS projects (cycle life, LCOS, IRR).
Standards: IEC, APSR regulations, OETC grid connection guidelines, NFPA 855.
Climate Data: IPCC AR6 projections for extreme heat/sandstorms in Muscat.

Calculation Formulas and Methodologies
Key Formulas

Annual Energy Shifted (MWh):[\text{Total MWh shifted} = \sum_{\text{all cycles}} (\text{Energy charged} - \text{Losses})]
Peak Demand Reduction (%):[\text{Peak Reduction (%)} = \frac{\text{Peak Load}{\text{before}} - \text{Peak Load}{\text{after}}}{\text{Peak Load}_{\text{before}}} \times 100]
Battery Degradation:[\text{Remaining Capacity} = \text{Initial Capacity} \times (1 - \text{Degradation Rate})^{\text{cycles}}]
Net Present Value (NPV):[NPV = \sum_{t=0}^{n} \frac{(R_t - C_t)}{(1 + r)^t}]Where ( R_t ) = revenue, ( C_t ) = cost, ( r ) = discount rate.
Levelized Cost of Storage (LCOS):[LCOS = \frac{\text{Total Lifetime Costs}}{\text{Total Lifetime Energy Delivered}}]

Advanced Methodologies

AI-Driven Optimization: Reinforcement learning for real-time BESS dispatch, maximizing arbitrage and peak shaving.
Digital Twin Simulation: Models energy flows, battery degradation, and grid interactions for both sites.
Quantum-Ready Framework: Prepares for quantum computing to solve high-dimensional optimization by 2030.
Scenario Modeling: Simulates solar charging, grid charging, peak discharge, and arbitrage with >95% forecasting accuracy.
Sensitivity Analysis: Tests degradation, tariff changes, load variations, and climate risks (e.g., 50°C+ temperatures).
Multi-Criteria Decision Analysis: Ranks scenarios based on technical, financial, and ESG KPIs.

Futuristic Features and Vision
Advanced Technologies

Sub-Minute IoT Data: Smart meters and 5G-enabled sensors capture transient events, enabling precise BESS dispatch and ancillary service participation (e.g., fast frequency response).
AI Forecasting: LSTM/Transformer models predict load, PV generation, and tariffs, integrated with cloud platforms (e.g., AWS SageMaker).
Digital Twins: Real-time simulation of Jindal Steel and Shinas Solar Plant using Siemens MindSphere, supporting proactive maintenance and scenario planning.
Blockchain Trading: Ethereum-based smart contracts for peer-to-peer energy trading, compliant with Oman’s direct sales policy.
Quantum Computing: Quantum annealing for hyper-optimized dispatch and scenario analysis, using Qiskit/Cirq by 2030.
Next-Gen Batteries: Models solid-state (>300 Wh/kg) and flow batteries for future deployments, reducing LCOS and footprint.

Sustainability and Resilience

Battery Recycling: Closed-loop system with Li-Cycle or Redwood Materials, tracked via blockchain for ESG compliance.
Carbon Tracking: Lifecycle assessment (LCA) via SimaPro, visualizing tCO₂e reductions in dashboards.
Agrivoltaics: Co-locates PV with agriculture at Shinas, enhancing land productivity and community benefits.
Climate Adaptation: Robust thermal management (e.g., liquid cooling) and climate modeling (IPCC AR6) for extreme heat/sandstorms.
Cybersecurity: NIST 800-53 standards, encrypted IoT/SCADA, and regular penetration testing.

Scalability and Global Reach

Modular Code: Reusable Python modules for load forecasting, BESS dispatch, and financial modeling, hosted on Kubernetes.
Open-Source Components: Non-proprietary modules (e.g., tariff parser) released on GitHub to foster global collaboration.
Multi-Use Cases: Supports microgrids, EV charging, and residential systems, tested in Oman pilots.

Vision for 2030

AI-Powered Ecosystem: Autonomous energy management, optimizing every kWh across Oman’s smart grid.
Decentralized Hub: Jindal Steel and Shinas as virtual power plant nodes, trading with EV hubs and communities.
Carbon-Negative: Combines BESS with carbon capture, unlocking carbon credit revenues.
AR/VR Control: Immersive interfaces for operators, visualizing performance via HoloLens.
Circular Economy: Zero-waste battery lifecycle, with second-life applications (e.g., EV charging).

Dashboard and Reporting Requirements
Technical & Operational Dashboards

Load vs. Generation Profile: Stacked bars for load, solar, BESS, and grid flows, with tariff overlays (inspired by Image 1).
Battery Health: State of health (SOH), cycle count, resistance, temperature, voltage spread per string (inspired by Image 4).
Scenario Comparison: Table of KPIs (energy shifted, peak reduction, RTE, grid dependency).

Financial Dashboards

Cost Breakdown: Pie/bar charts for CapEx, OpEx, maintenance, grid fees (inspired by Image 3).
Revenue Streams: Savings from arbitrage, peak shaving, grid services, tax incentives.
Metrics: NPV, IRR, payback period, LCOS, TCO, visualized as trend lines.

Risk & Sensitivity Dashboards

Risk Register: Probability-impact matrix for technical, market, operational, and geopolitical risks.
Sensitivity Analysis: Tornado/spider charts for NPV/IRR sensitivity to CapEx, tariffs, and degradation.

Interactive Features

Dynamic Inputs: Editable fields for battery size, tariffs, degradation, and costs, updating visuals in real time.
Enterprise Visualization: Power BI/Tableau integration for polished, drill-down dashboards.
AR Interface: Unity-based AR app for immersive system monitoring (future phase).
LLM Reporting: Auto-generated narrative reports via OpenAI API, tailored to executives or technicians.

Professional Report Structure
Executive Summary

Project background, objectives, key findings, and recommendations.

Introduction

Overview of Jindal Steel and Shinas Solar Plant, rationale, and scope.

Methodology

Data sources, AI models, digital twin setup, and quantum-ready framework.

Site & Technology Evaluation

Scoring matrices for LFP, NAS, solid-state, and flow batteries; site constraints.

Scenario Analysis

Energy flow modeling, technical performance, and financial outcomes.
Single-line diagrams and flow charts.

Financial Analysis

Cost/revenue projections, NPV, IRR, LCOS, TCO.
Sensitivity and risk analysis.

Decision Matrix & Recommendations

Weighted scoring for scenarios (e.g., LFP for Jindal due to cycling needs).
Rationale for preferred technology and site strategy.

Implementation Roadmap

2025-2026: IoT deployment, AI forecasting, pilot BESS (1 MW/2 MWh).
2027-2028: Full-scale rollout, blockchain trading, AR interface.
2029-2030: Quantum optimization, carbon-negative operations, global expansion.

Annexures

Raw data, weather sources, regulatory references, simulation outputs.

Installation
Prerequisites

Python 3.8+: For tool and Streamlit execution.
Git: For cloning the repository.
Optional: AWS SageMaker (AI training), Power BI/Tableau (dashboards), Qiskit (quantum readiness).

Setup

Clone the Repository:
git clone https://github.com/<your-username>/solar-pv-bess-oman.git
cd solar-pv-bess-oman


Create a Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt

Includes pandas, numpy, streamlit, matplotlib, scipy, numpy-financial, tensorflow, openai.

Prepare Data Inputs:

Tariffs: data/tariffs/ (CSV/JSON).
Load Profiles: data/loads/ (CSV, Jindal Steel).
PV Generation: data/pv/ (CSV, Shinas Solar Plant).
Weather: data/weather/ (CSV).
Sample datasets: data/sample/.



Usage
Running the Dashboard Suite

Launch Streamlit Interface:
streamlit run src/streamlit/app.py


Access at http://localhost:8501.
Upload data, modify assumptions (e.g., battery size, tariffs), and view dashboards.
Export PDF reports or Power BI/Tableau files.


Run Simulations:

Execute standalone simulations:python src/bess_model/simulate.py --config data/config.yaml


Configure in data/config.yaml (CapEx, tariffs, etc.).
Outputs in data/outputs/ (CSV/JSON).



Key Features

AI Optimization: Real-time dispatch using reinforcement learning.
Digital Twin: Simulates system dynamics with >95% accuracy.
Blockchain Trading: P2P energy transactions (pilot phase).
Interactive Dashboards: Energy flows, financials, risks, with AR preview.
Quantum Readiness: Modular code for future quantum optimization.

Critical Decision-Making Requirements

Objective Prioritization: Cost reduction, peak management, or sustainability.
Assumption Approval: Discount rates, project lifetime, risk tolerance.
Scenario Selection: Based on weighted scores and stakeholder input.

Compliance and Standards

Oman Grid Code (v3.0): Fault ride-through, reactive power, SCADA.
Oman Electrical Standards (OES): Equipment and installation.
International Standards: IEEE 1547, IEEE 2030.5, NFPA 855, IEC.
Cybersecurity: NIST 800-53, encrypted IoT/SCADA.

Contributing
Contributions are welcome. To contribute:

Fork the repository.
Create a feature branch (git checkout -b feature/<feature-name>).
Commit changes (git commit -m "Add <feature>").
Push to the branch (git push origin feature/<feature-name>).
Open a pull request, adhering to Code of Conduct and Contribution Guidelines.

License
Licensed under the MIT License. See LICENSE.
Contact

Email: your-email@example.com
GitHub Issues: Create an issue in this repository.

Acknowledgments

APSR, OETC, NEDC for regulatory and technical guidance.
Oman’s Vision 2040 and renewable energy initiatives.
GCC and India BESS projects for benchmarks.
NASA POWER and IPCC AR6 for climate data.


