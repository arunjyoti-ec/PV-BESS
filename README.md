# PV-BESS: Integrated Solar PV and Energy Storage Architecture for Oman

![CI](https://github.com/arunjyoti-ec/PV-BESS/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/github/license/arunjyoti-ec/PV-BESS)
![Last Commit](https://img.shields.io/github/last-commit/arunjyoti-ec/PV-BESS)
[![codecov](https://codecov.io/gh/arunjyoti-ec/PV-BESS/branch/main/graph/badge.svg)](https://codecov.io/gh/arunjyoti-ec/PV-BESS)

## Table of Contents
- [Overview](#overview)
- [Objectives](#objectives)
- [Repository Structure](#repository-structure)
- [Key Features](#key-features)
- [Demo](#demo)
- [Installation](#installation)
- [Usage](#usage)
- [Regulatory Standards](#regulatory-standards)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

---

## Project Status
🚧 **Under Development** — Core simulation modules and dashboards are in active development. Contributions and feedback are welcome!

---

## Overview
This repository provides a technical framework and decision-support tool for evaluating the integration of Battery Energy Storage Systems (BESS) with solar photovoltaic (PV) generation at two sites in Muscat, Oman:

1. **Load Site (Industrial Load Facility):** Combines grid power, on-site solar PV, and BESS for energy cost optimization via tariff arbitrage, peak shaving, and solar self-consumption.
2. **Solar PV Generator Site (Solar PV Plant):** A utility-scale solar farm designed for grid export, aligned with Oman's transmission network requirements.

The project adheres to Oman's regulatory environment (Oman Grid Code, Oman Electrical Standards, 2025 Cost-Reflective Tariff) and incorporates international standards like IEEE 1547, NFPA 855, and others.

| Feature | Industrial Load Facility | Solar PV Plant (Generator Site) |
|---|---|---|
| Role | Demand management | Grid export |
| Key Strategy | Tariff arbitrage & peak shaving | Maximize export revenue |
| Scale | Commercial / Industrial | Utility-scale |

---

## Objectives
- **Architecture Design:** Develop compliant and efficient electrical and control architectures for both sites.
- **Cost Optimization:** Target near-100% renewable utilization at the Industrial Load Facility and maximize grid export at the Solar PV Plant.
- **Advanced Analytics:** Deliver professional reports and interactive dashboards with predictive analytics, financial metrics, and risk analysis.
- **Regulatory Compliance:** Ensure system safety, reliability, and adherence to both Omani and international standards.
- **Future Scalability:** Integrate emerging technologies (AI, blockchain, quantum computing) for global scalability and sustainability.

---

## Repository Structure

> **Note:** Codebase is under active development. The directory structure below reflects the planned architecture.

```
├── data/                      Input data for analysis
│   ├── tariffs/               CRT tariff data (CSV/JSON)
│   ├── loads/                 Industrial load profiles (CSV)
│   ├── pv/                    Solar PV Plant generation data (CSV)
│   ├── weather/               Solar irradiance and temperature data (CSV)
│   └── sample/                Example datasets
├── src/                       Source code for the decision-making tool
│   ├── bess_model/            BESS simulation and optimization modules
│   ├── streamlit/             Streamlit scripts for dashboards
│   ├── ai_forecasting/        ML models for load, PV, and tariff prediction
│   ├── blockchain/            Smart contracts for energy trading
│   └── utils/                 Helper scripts for data processing
├── docs/                      Documentation and reports
│   ├── architecture_design.md  System architecture details
│   ├── regulatory_framework.md  Oman regulations and tariffs
│   ├── tool_guide.md          Decision-making tool usage guide
│   └── bess_report.pdf        Consultant-grade BESS evaluation report
├── tests/                     Test scripts and validation datasets
├── requirements.txt           Python dependencies
├── LICENSE                    License file
└── README.md                  This file
```

---

## Key Features

### Technical Highlights
- **AI-Driven Optimization:** Real-time BESS dispatch using reinforcement learning.
- **Digital Twin Simulation:** Models energy flows, battery degradation, and grid interactions with >95% accuracy.
- **Quantum-Ready Framework:** Prepares for high-dimensional optimization using quantum computing by 2030.
- **Scenario Modeling:** Simulates solar charging, grid charging, peak discharge, and arbitrage.

### Financial Insights
- **Cost Reduction:** Minimize costs through tariff arbitrage and peak shaving.
- **Revenue Optimization:** Maximize savings and generate revenue from grid export and tax incentives.
- **Dynamic Dashboards:** Visualize key metrics like NPV, IRR, LCOS, and TCO interactively.

### Future-Proofing
- **Blockchain Energy Trading:** Ethereum-based smart contracts for peer-to-peer trading.
- **Sustainability:** Battery recycling and lifecycle carbon tracking for ESG compliance.
- **Advanced Batteries:** Support for solid-state and flow batteries for future deployments.

---

## Demo
> Screenshots and a live demo link will be added upon first release.

---

## Installation

### Prerequisites

| Dependency | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Core runtime |
| Git | Any | Repository cloning |

### Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/arunjyoti-ec/PV-BESS.git
   cd PV-BESS
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

3. **Install Dependencies:**
   ```bash
   pip install -e .
   ```

4. **Prepare Data Inputs:**
   - Tariffs: `data/tariffs/` (CSV)
   - Load Profiles: `data/loads/` (CSV)
   - PV Generation: `data/pv/` (CSV)
   - Weather: `data/weather/` (CSV)

5. **Copy and edit the configuration:**
   ```bash
   cp data/config.yaml.example data/config.yaml
   # Edit data/config.yaml to match your site parameters
   ```

---

## Developer Setup

Install development dependencies and activate pre-commit hooks:

```bash
pip install -e ".[dev]"
pre-commit install
```

**Run the full test suite:**

```bash
pytest                          # all tests
pytest -m "not slow"            # skip long-running tests
pytest --cov --cov-report=html  # with HTML coverage report
```

**Lint and format:**

```bash
ruff check .        # linting
ruff format .       # auto-format
mypy simulate.py config.py validators.py logger.py  # type checking
```

---

## Usage

### Run the Dashboard Suite

1. **Launch Streamlit Interface:**
   ```bash
   streamlit run src/streamlit/app.py
   ```
2. Access at: [http://localhost:8501](http://localhost:8501).
3. **Features:**
   - Upload data and modify assumptions (e.g., battery size, tariffs).
   - View interactive dashboards.
   - Export reports as PDFs or Power BI/Tableau files.

### Run Simulations

1. Execute standalone simulations:
   ```bash
   python src/bess_model/simulate.py --config data/config.yaml
   ```
2. Outputs: Saved in `data/outputs/` (CSV/JSON).

### Critical Decision-Making Requirements
- **Objective Prioritization:** Cost reduction, peak management, or sustainability.
- **Scenario Selection:** Based on weighted scores and stakeholder input.
- **Assumption Approval:** Validate discount rates, project lifetime, and risk tolerance.

---

## Regulatory Standards

| Standard | Scope |
|---|---|
| Oman Grid Code | Grid connection requirements |
| Oman Electrical Standards | National electrical compliance |
| NFPA 855 | BESS fire & safety |
| IEEE 1547 | Distributed energy interconnection |
| 2025 CRT Tariff | Cost-reflective tariff structure |

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/<feature-name>
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add <feature>"
   ```
4. Push the branch and open a pull request.
5. Ensure adherence to the Code of Conduct and Contribution Guidelines.

---

## License
This project is licensed under the [MIT License](LICENSE) — see the LICENSE file for details.

---

## Contact
- **Email:** arunjyoti.ec@gmail.com
- **GitHub Issues:** [Create an issue](https://github.com/arunjyoti-ec/PV-BESS/issues) in this repository.

---

## Acknowledgments
- APSR, OETC, and NEDC for regulatory and technical guidance.
- Oman's Vision 2040 for renewable energy initiatives.
- NASA POWER and IPCC AR6 for climate data.
