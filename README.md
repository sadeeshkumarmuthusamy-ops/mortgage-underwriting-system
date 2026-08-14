Here is the comprehensive README content structured exactly as you requested.

*Note: Since you requested this for a Word document, you can simply copy the rendered text below and paste it directly into Microsoft Word. Word will automatically recognize and preserve the headings, bullet points, and formatting.*

---

# Mortgage Underwriting System

## Project Overview

The **Mortgage Underwriting System** is an intelligent, Python-based application designed to automate and augment the mortgage approval process. By leveraging large language models (LLMs), Retrieval-Augmented Generation (RAG), and autonomous AI agents, the system efficiently ingests applicant data, analyzes complex financial documents, evaluates risk, and provides actionable underwriting recommendations.

## Architecture/Workflow

The system follows an agentic and retrieval-augmented architecture:

1. **Data Ingestion:** User applications and supporting financial documents are ingested via an API.
2. **Vectorization & Storage:** Document text is embedded and stored within a Vector Database for semantic search capabilities.
3. **Agentic Pipeline (LangGraph):** A stateful graph orchestrates the underwriting workflow, routing tasks to specialized AI agents (e.g., Income Verifier, Credit Analyst).
4. **Context Retrieval (RAG):** Agents query the VectorDB to retrieve pertinent policies, regulations, and applicant document snippets to ground their decisions.
5. **Decision Synthesis:** A final underwriting agent synthesizes the findings and outputs a structured approval, denial, or manual review recommendation.

## Features

* **Automated Agentic Workflows:** Specialized agents handle distinct parts of the underwriting process.
* **Intelligent Document Retrieval (RAG):** Seamlessly retrieves context from dense mortgage guidelines and applicant files.
* **Vector Database API Integration:** Built-in endpoints to load, update, and query data in the VectorDB.
* **Robust Auditing & Logging:** Centralized logging to track agent reasoning and system events for compliance.
* **Modular Design:** Easily extensible to accommodate new lending rules or documentation types.

## Technology Stack

* **Language:** Python
* **LLM Orchestration:** LangChain, LangGraph
* **Vector Database:** ChromaDB (or similar VectorDB as configured)
* **Testing:** Pytest
* **Dependency Management:** pip / `pyproject.toml`

## Repository Structure

Based on the current repository layout:

* `src/`: Core application source code, including APIs, agents, RAG logic, and custom loggers.
* `tests/`: Test suite, including unit tests for agents and system components.
* `README.md`: Project documentation.
* `pyproject.toml` / `requirements.txt`: Python dependencies and package configurations.
* `.python-version`: Specifies the required Python runtime.
* `.gitignore`: Untracked files and directories.

## Installation/Setup

1. **Clone the repository:**
```bash
git clone https://github.com/sadeeshkumarmuthusamy-ops/mortgage-underwriting-system.git
cd mortgage-underwriting-system

```


2. **Set up a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```


3. **Install dependencies:**
```bash
pip install -r requirements.txt
# OR if utilizing pyproject.toml
pip install -e .

```



## Environment Variables

Create a `.env` file in the root directory and configure the following required variables:

* `OPENAI_API_KEY`: Your LLM provider API key (or alternative provider key).
* `CHROMADB_HOST` / `CHROMADB_PORT`: Connection details for your VectorDB.
* `LOG_LEVEL`: Logging verbosity (e.g., `DEBUG`, `INFO`, `WARNING`).
* `ENVIRONMENT`: Deployment environment (e.g., `development`, `production`).

## Running the Application

To start the primary application or API server, run the main entry point located in the `src` directory:

```bash
python src/main.py

```

*(Note: Adjust the entry point command based on whether you are running a FastAPI server or a CLI script).*

## Running Tests

To execute the test suite (including agent behavioral tests), use `pytest`:

```bash
pytest tests/ -v

```

## Underwriting Workflow

1. **Intake:** The system receives the mortgage application (JSON payload) and applicant documents (PDFs/Images).
2. **Extraction & Chunking:** Documents are parsed, chunked, and loaded into the VectorDB.
3. **Verification:** Agents verify income, calculate Debt-to-Income (DTI) ratios, and assess Loan-to-Value (LTV) limits.
4. **Policy Check:** The RAG system cross-references the applicant's profile against current lending guidelines.
5. **Decision:** The system flags anomalies and generates a final comprehensive underwriting report.

## RAG/ChromaDB Usage

The project relies heavily on RAG to ensure LLM responses are factually grounded in lending policies and applicant data.

* **Ingestion API:** The `src` directory contains specific endpoints/scripts to vectorize PDF documents and load them into ChromaDB.
* **Retrieval:** When an agent needs to verify a rule (e.g., "What is the max DTI for an FHA loan?"), it performs a similarity search against the VectorDB, fetching the top-k most relevant text chunks to use as context for the prompt.

## LangGraph/LangChain Components

* **LangChain:** Used for constructing prompts, interacting with LLM APIs, and defining tools (e.g., calculator tools, database query tools).
* **LangGraph:** Used to build cyclical, stateful agent workflows. The underwriting process is modeled as a graph where nodes represent specific agents (Income Agent, Credit Agent) and edges represent conditional logic (e.g., if DTI > 50%, route to "Manual Underwriter" node).

## Configuration

Application-wide configuration is managed via `pyproject.toml` (for build and dependency settings) and environment variables (for runtime secrets). Logging behavior can be customized within the `src/logger` configurations to ensure compliance trails are properly formatted and stored.

## Troubleshooting

* **VectorDB Connection Errors:** Ensure your ChromaDB instance is running and the `.env` variables match your local/remote host ports.
* **LLM Rate Limits:** If agents fail mid-workflow, check your LLM provider's rate limits or token usage.
* **Missing Dependencies:** Ensure you are operating within the activated virtual environment and that `uv.lock` or `requirements.txt` are strictly synced.

## Security Considerations

* **PII Handling:** Mortgage applications contain highly sensitive Personally Identifiable Information (PII). Ensure data is anonymized where possible before sending it to external LLM APIs.
* **Data Encryption:** Vector databases should be encrypted at rest.
* **Secret Management:** Never commit the `.env` file or hardcode API keys into the repository.

## Future Enhancements

* Implementation of a frontend dashboard for human-in-the-loop (HITL) manual reviews.
* Integration with live credit bureau APIs (Experian, Equifax, TransUnion).
* Multi-modal support to process handwritten application forms via OCR.
* Migration to cloud-managed Vector databases (e.g., Pinecone, AWS OpenSearch).

## License/Contribution Information

**Contributing:** We welcome pull requests! Please ensure all new agents and API endpoints are accompanied by tests in the `tests/` directory. For major changes, please open an issue first to discuss what you would like to change.

**License:** Please refer to the `LICENSE` file in the repository root for usage and distribution terms.
