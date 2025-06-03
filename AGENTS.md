# MILO-Codex
Project M.I.L.O: Contributor & Agent Guide
1. Introduction & Vision
Project Name: M.I.L.O (Minimal Input Life Organizer)

Purpose:
MILO aims to provide individuals with a powerful AI system for life organization while prioritizing data privacy and security. It represents a move towards decentralized technology, empowering users with ownership over their data and their experience with AI products. This is a passion project driven by the desire to create a tool that is genuinely useful for personal organization, built with the speed and efficiency that modern AI development tools allow.

Scope:
The initial focus is on building a core, functional product (M.I.L.O Personal Beta) that demonstrates the value of local-first AI. While a passion project, the goal is to move quickly to establish a first-mover advantage in this space.

Vision Statement:
The overarching vision for MILO is to pioneer the Local-First model of AI adoption into daily life. As cloud-based AI becomes ubiquitous, MILO offers an alternative that addresses growing concerns about data privacy. It allows users to harness the convenience of AI and automation without surrendering personal data to large tech companies.

MILO will act as a "Digital Butler" – a Jarvis-like assistant that connects to a user's most-used services and becomes a central hub for their digital life (emails, tasks, home management, goals). All data processing will occur on the user's physical device, with no cloud service interaction for core reasoning, effectively creating a physical "safe" for user data. The long-term vision includes a community-driven ecosystem of plugins and expansions, starting with a Smart Mirror integration.

2. Core Functionality & Architecture
MILO is built on the following principles and components:

Local-First Infrastructure: All primary reasoning, automation tasks, and data storage will run locally on the user's device. The user's only costs are their existing software subscriptions and the hardware to run MILO.

Local Skills: A suite of default local Python scripts designed to automate specific, on-device productivity tasks (e.g., file management, application control, web scraping for information).

n8n Local-Hosted Orchestrations: A collection of default n8n workflows, self-hosted by the user, to securely connect to external SaaS APIs (e.g., Notion, Gmail, Drive). These act as a secure "bridge" for external data.

Natural Language System: MILO will feature a natural-sounding voice with a distinct personality, fine-tuned for instruction-following and hands-free system control. The core LLM for this will be a GGUF-compatible model like Gemma, run locally.

Plugins & Expansions: MILO's core functionality will be built as a "Core Framework" with a modular and expandable plugin system. This allows for user personalization and future development of new capabilities. All new features (local skills, n8n connections) should be developed as self-contained plugins.

Key Technical Stack:
Primary Language: Python 3.12+

Dependency Management: Poetry (use pyproject.toml and poetry.lock)

Local LLM Interface: The system will interact with local LLMs via a defined Python interface (milo_core.llm.LocalModelInterface). The actual model files (e.g., Gemma GGUF) are not part of this repository and are downloaded by the user separately.

n8n Workflows: Stored as JSON files in the /.n8n/workflows/ directory.

Dev Environment Tips: 
Agent Environment Setup: Your Codex environment is automatically configured by the setup.sh script defined in the repository settings. This script installs Poetry and then runs poetry install to set up all Python dependencies from pyproject.toml.

Local User Environment: Users setting up MILO locally should run poetry install after cloning the repository to install all Python dependencies.

Adding Python Dependencies: If a task requires a new Python library:

Use the command poetry add <package_name>.

Ensure the pyproject.toml and poetry.lock files are updated and included in your changes.

Adding Node.js Dependencies (for n8n tooling): If a task requires a new Node.js package for n8n-related development (e.g., a validation tool):

Add the dependency to the package.json file.

Ensure package.json and package-lock.json (or equivalent) are updated and included in your changes. The setup.sh script runs npm install for this.

Testing Instructions
Running Python Unit Tests: Execute the full Python test suite using the command: poetry run pytest.

Test Coverage: All new Python functions, classes, and significant logic branches must be accompanied by unit tests. Tests should cover:

Expected use case (happy path).

Edge cases.

Failure cases and proper error handling.

Test Location: Python tests should reside in the /tests directory, mirroring the main application structure. Mock external services and file system interactions as needed.

Linting & Formatting:

Format all Python code using: poetry run ruff format .

Check for linting errors using: poetry run ruff check .

n8n Workflow Validation: If you create or modify an n8n workflow JSON file, ensure it is syntactically valid. If a specific validation command via n8n-cli is available and configured, use it.

All Checks Must Pass: The commit should pass all tests, linting, and formatting checks before you consider a task complete or merge a PR. Fix any errors until the entire suite is green.

PR Instructions
Branching: Create a new, descriptively named branch for each task.

Title Format: [Scope] A brief, descriptive title of the change

Examples:

[Feature] Implement FileFinder local skill

[Fix] Correct error in n8n Gmail workflow trigger

[Docs] Update LLM interface documentation

[Refactor] Improve plugin loading logic

Body/Description:

Briefly summarize the changes made.

Clearly explain the "why" behind the changes, especially for complex logic or architectural decisions.

Reference the original task or issue number if applicable.

If you made any assumptions or encountered ambiguities during development, please state them explicitly.

Self-Review: Before submitting the PR, thoroughly review your own changes to catch any obvious errors, typos, or omissions. Double-check that all tests and linters pass.

Coding Standards & Style
Read This File First: Before starting any task, thoroughly review this entire AGENTS.MD file to understand the project's architecture, goals, style, and constraints.

One Task at a Time: Focus on implementing one distinct feature or fixing one specific bug per pull request.

Clarity is Key: If any instruction is unclear or ambiguous, please state your assumptions or ask for clarification in the PR description.

Python Specifics:

Follow PEP 8 guidelines.

Use type hints for all function signatures and variable declarations.

Write clear, concise, and well-commented code. Non-obvious logic should be explained with inline comments or in the PR description.

Organize code into clearly separated modules, grouped by feature or responsibility.

Modularity: New features, especially "Local Skills" or "n8n Orchestrations," must be implemented as plugins within the /plugins directory. This is crucial for maintaining the core framework's integrity and promoting expandability.

Specific Feature Implementation Notes
V0 (Core) Features - Agent Focus:

Core App Framework:

Establish the main application structure in milo_core/.

Implement milo_core.llm.LocalModelInterface and a placeholder implementation.

Implement milo_core.plugin_manager.PluginManager capable of discovering and loading plugins from the /plugins directory.

Memory Store & RAG + Startup:

Design a basic in-memory store for short-term conversation context.

Implement a placeholder for RAG functionality that can be expanded later. It should be clear where a local knowledge base would integrate.

Default n8n Workflows (Initial Set):

Create valid JSON workflow files in /.n8n/workflows/ for basic PUSH/PULL operations for 2-3 key services (e.g., Gmail: read new emails, Notion: create a note).

MILO -> n8n Connect:

Implement logic in milo_core to parse a user's voice/text command (represented as structured JSON for now) and trigger the corresponding n8n workflow via a local webhook call.

Default Local Skills (Initial Set):

Implement 1-2 simple local skills as plugins in /plugins/. Examples:

FileFinder: A skill that takes a filename and searches common user directories.

OpenApplication: A skill that takes an application name and attempts to open it.

MILO -> Local Skills:

Implement logic in milo_core (likely via the PluginManager) to parse a user's command and execute the corresponding local skill plugin.

MILO Voice Setup (Interface Only):

Define the interfaces for Text-to-Speech (TTS) and Speech-to-Text (STT) within milo_core. Actual voice training and fine-tuning are outside the agent's scope.

Agent, Please Note:
Local-First Mandate: Do NOT write any code that relies on cloud services for core reasoning, data storage, or AI model processing. All such operations must be designed to run on the user's local machine.

Model Handling: The actual LLM (e.g., Gemma) is NOT downloaded or run by you. You will write code that interacts with the LocalModelInterface. The user is responsible for downloading the model separately using a script like download_model.sh (which you may be asked to create or update).

Security & Privacy: Be mindful of security best practices, even though the app is local. Avoid writing code that unnecessarily exposes sensitive information or creates vulnerabilities if the user's machine were compromised.
