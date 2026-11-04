# AFTERMATH

### Govern the city. Shape its future. Survive the consequences.

AFTERMATH is an AI-powered city-management simulation in which you take control of **NOVA YORK**, a futuristic metropolitan city.

As mayor, you are responsible for managing the city's economy, population, infrastructure, environment, public safety, and political stability. Every decision has consequences, and every passing day changes the state of your city.

AFTERMATH combines deterministic simulation systems with AI-powered deliberation to create a dynamic governance experience.

---

## Overview

You are not simply building a city. You are governing one.

Manage competing priorities, respond to emergencies, introduce policies, allocate resources, and make difficult decisions while balancing the needs of different communities.

The simulation advances day by day, with interconnected systems influencing the city's overall condition.

## Features

### City Simulation
- Manage a futuristic metropolitan city.
- Advance the simulation through daily updates.
- Monitor population, economy, environment, and transportation.
- Manage districts, buildings, infrastructure, and city resources.
- Experience changing conditions as the simulation progresses.

### AI Council
- Consult an eight-perspective AI Council.
- Examine decisions through different professional viewpoints.
- Explore potential benefits, risks, and trade-offs.
- Receive structured deliberations before making decisions.
- Retain human control over final decisions.

### Crisis Management
- Monitor emerging city emergencies.
- Respond to disasters and critical incidents.
- Coordinate recovery and response operations.
- Evaluate the impact of emergencies on city systems.

### Security Command Centre
- Monitor public safety conditions.
- Manage security personnel and deployments.
- Coordinate operational responses.
- Track security-related developments.

### Policy and Governance
- Introduce policies and administrative decisions.
- Evaluate their potential consequences.
- Manage campaigns and public priorities.
- Balance economic, environmental, and social objectives.

### City Intelligence
- Monitor city metrics and performance.
- Explore district-level information.
- Visualize city conditions and simulation data.
- Review operational updates and system reports.

### Simulation Management
- Save and load simulation progress.
- Review simulation rules and mechanics.
- Experience different outcomes based on administrative decisions.

---

## Technology Stack

| Area | Technologies |
|---|---|
| Language | Python |
| Application | Streamlit |
| Agent orchestration | LangGraph |
| AI integrations | LangChain |
| AI providers | Gemini, Groq, Otari |
| Data validation | Pydantic |
| Database | SQLite, SQLAlchemy |
| Visualization | Plotly, PyDeck |
| Data processing | Pandas, NumPy |
| 3D assets | Trimesh, GLB models |
| Testing | Pytest |

## AI Architecture

AFTERMATH integrates multiple AI providers through a configurable provider layer.

The application supports:

- **Google Gemini** — general AI capabilities.
- **Groq** — alternative model inference.
- **Otari** — AI gateway integration used for the Mozilla Developers Wilding: Online! hackathon.

The AI Council uses structured deliberation to present different perspectives on governance decisions.

AI-generated recommendations are advisory. The human player retains authority over final decisions.

## Project Structure

```text
AFTERMATH/
│
├── agents/          # Citizen and society agents
├── ai/              # AI providers, routing, graphs and schemas
├── assets/          # Images, styles and 3D assets
├── core/            # Application configuration and core utilities
├── data/            # Local simulation data
├── database/        # Database connection, models and repositories
├── disasters/       # Disaster simulation and response systems
├── events/          # Event generation and handling
├── judgement/       # Assessment and judgement systems
├── scenarios/       # Scenario management
├── security/        # Security operations and deployment
├── simulation/      # Simulation engine and city state
├── static/          # Static application assets
├── ui/              # Streamlit interface and components
├── utils/           # Shared utilities
├── world/           # City, district and building generation
│
├── .env.example     # Environment configuration template
├── app.py           # Application entry point
├── requirements.txt # Python dependencies
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11 or newer recommended.
- Git.
- API credentials for at least one configured AI provider.

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd AFTERMATH
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and add the API credentials for your chosen provider.

```env
# AI PROVIDERS
GEMINI_API_KEY=
GROQ_API_KEY=
OTARI_API_KEY=

# MODEL CONFIGURATION
GEMINI_MODEL=gemini-3.5-flash-lite
GROQ_MODEL=openai/gpt-oss-120b

OTARI_MODEL=alibaba/qwen-3.5-35b-a3b
OTARI_BASE_URL=https://api.otari.ai/api/v1

# AI ROUTING
AI_PROVIDER=gemini

# APPLICATION
APP_NAME=AFTERMATH
DATABASE_PATH=data/aftermath.db
SIMULATION_SPEED=1
```

Keep your API keys private. Never commit your `.env` file.

### 5. Run the application

```powershell
python -m streamlit run app.py
```

Streamlit will provide a local URL in your terminal.

## Running Tests

Run the test suite with:

```powershell
python -m pytest
```

The repository also includes an Otari integration test:

```powershell
python test_otari.py
```

The Otari test requires valid credentials and network access.

## Mozilla Developers Wilding: Online!

AFTERMATH is being developed as a submission for Mozilla's Developers Wilding: Online! hackathon.

The project integrates Otari as an AI provider for its AI-powered governance deliberation workflow.

The hackathon integration demonstrates how an existing application can incorporate Otari into a practical AI-powered system.

## Design Philosophy

AFTERMATH is built around three principles:

1. **Interconnected systems:** City systems influence one another rather than operating independently.
2. **Consequential decisions:** Administrative actions have consequences that shape the simulation.
3. **Human authority:** AI provides analysis and perspectives, while the player remains responsible for decisions.

---

**AFTERMATH — The city is yours to govern. The consequences are yours to face.**