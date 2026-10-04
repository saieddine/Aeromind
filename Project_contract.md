AeroMind — Project Contract

Project: AeroMind — Interactive Aircraft Intelligence Lab
Duration: 20 active development days + 3-day emergency buffer
Deployment: Localhost only
Team: You, Sasha, Nirmin

1. Project Purpose

AeroMind is an interactive AI-powered aircraft learning and exploration system.

The system combines:

Traditional RAG

GraphRAG

LightRAG

A shared backend API

A structured aircraft knowledge database

Interactive 3D aircraft visualization

Educational "What If?" simulations

A conversational AI assistant

The system is intended as an academic/research prototype and will run locally. It is not intended to provide operational aviation, maintenance, or safety instructions for real-world use.

The core research goal is to use the same aircraft knowledge base and comparable questions to explore and demonstrate different retrieval approaches.

2. Team Ownership

You — AI, Backend & Database

Primary ownership

Traditional RAG

GraphRAG

Backend/API

Database

Data ingestion and organization

Knowledge-base architecture

Conversation state

AI service integration

Evaluation of retrieval systems

Final system integration

Database rule

The database architecture and database implementation are owned by you.

Sasha and Nirmin may request fields, provide requirements, and contribute data, but they should not create independent database schemas that compete with the main schema.

Sasha — Frontend & LightRAG

Primary ownership

LightRAG implementation

Frontend architecture

Chat interface

Navigation

Aircraft selection interface

Search/knowledge interface

User/profile interface

Frontend ↔ backend integration

Frontend ownership

Sasha owns the main frontend architecture together with Nirmin.

Sasha is responsible for making sure the frontend can consume the agreed backend API without requiring backend implementation changes.

Nirmin — Frontend, 3D Visualization & Simulation

Primary ownership

Interactive 3D aircraft visualization

Aircraft/component interaction

Engine visualization

"What If?" simulation

Simulation UI

Frontend contribution

Visualization ↔ frontend integration

Frontend ownership

Nirmin and Sasha jointly own the frontend.

Sasha focuses more on application structure, UI, interaction flow, and LightRAG integration.

Nirmin focuses more on visualization, simulation, and the visual/interactive experience.

3. Core Architecture

                         FRONTEND
                  Sasha + Nirmin
                         |
                     HTTP / JSON
                         |
                    BACKEND API
                         |
        +----------------+----------------+
        |                |                |
       RAG           GraphRAG         LightRAG
        |                |                |
        +----------------+----------------+
                         |
                  Knowledge Layer
                         |
              +----------+----------+
              |                     |
          Vector/Data          Graph/Data
              |                     |
              +----------+----------+
                         |
                  Aircraft Dataset

Visualization is connected through the backend/frontend contracts:

3D Aircraft
     |
Component selected
     |
Frontend
     |
Backend API
     |
Aircraft knowledge

Simulation follows:

User selects scenario
        |
Simulation engine
        |
Standardized simulation state/event
        |
Frontend visualization
        |
Optional AI explanation

4. The Most Important Rule: Module Contracts

Every major module must have a clearly defined input/output contract.

A developer must NOT deliver a module that only works inside their own local implementation.

A module is considered complete only when another team member can use it through its documented interface without modifying its internal implementation.

Example

Bad:

"Here is my LightRAG code. You need to modify it to work with your backend."

Good:

"Here is the LightRAG service. Send it this request and it returns this response."

5. Standard AI Query Contract

All three retrieval systems must expose the same conceptual interface.

Request

{
  "aircraft_id": "a320",
  "question": "How does the engine generate thrust?",
  "conversation_id": "conversation_001"
}

Optional:

{
  "mode": "rag"
}

The exact internal implementation is up to the owner of each retrieval system.

6. Standard AI Response Contract

RAG, GraphRAG, and LightRAG should return a compatible structure.

{
  "answer": "The engine generates thrust by...",
  "sources": [
    {
      "document_id": "doc_001",
      "title": "Aircraft Technical Manual",
      "section": "Engine Systems",
      "page": 42
    }
  ],
  "metadata": {
    "method": "rag",
    "latency_ms": 820
  }
}

The frontend should be able to display the result without knowing how the answer was generated.

7. Retrieval Method Values

The method field should use:

rag
graphrag
lightrag

Example:

{
  "metadata": {
    "method": "graphrag"
  }
}

8. Frontend ↔ Backend Rule

The frontend must communicate with the backend through documented API endpoints.

The frontend must NOT:

Directly access the database

Directly manipulate the vector database

Directly manipulate the graph database

Contain private API keys

Depend on internal Python/backend modules

The backend is the central gateway.

Frontend
   |
   | HTTP/JSON
   ↓
Backend
   |
   +--> Database
   +--> RAG
   +--> GraphRAG
   +--> LightRAG

9. Visualization Contract

The visualization system must use stable aircraft/component identifiers.

Example:

{
  "aircraft_id": "a320",
  "component_id": "engine_1"
}

Components should have stable IDs such as:

fuselage
left_wing
right_wing
engine_1
engine_2
cockpit
landing_gear
tail

The exact component list may change according to the aircraft model.

The important rule is:

The identifier must remain stable once agreed upon.

This allows the frontend, backend, database, and visualization system to refer to the same component.

10. Simulation Contract

The "What If?" system should communicate using structured events/states rather than directly modifying backend data.

Example:

{
  "aircraft_id": "a320",
  "scenario": "engine_failure",
  "affected_components": [
    "engine_1"
  ],
  "state_changes": {
    "engine_1": "failed"
  }
}

The simulation should be educational/conceptual.

It is not intended to model a real aircraft with operational accuracy.

11. Database Contract

The database is centrally owned by the backend/data owner.

The database should provide stable identifiers for:

Aircraft

Components

Documents

Document sections

Sources

Conversations

Simulation scenarios where necessary

Example:

Aircraft
---------
id
manufacturer
model
description
3d_model_id

Component
---------
id
aircraft_id
name
type

Document
--------
id
aircraft_id
title
path
metadata

The exact schema may evolve during development.

However, schema changes must be communicated before they are implemented because other modules may depend on them.

12. Data Rules

All team members must use the same identifiers and naming conventions.

For example:

a320
a330
a350
b737
b777
b787

Do not create:

A320
airbus_a320
Airbus320
320_airbus

for the same aircraft in different modules.

One canonical identifier must be selected.

13. No Hard-Coded Fake Integration

Mock data is allowed during early frontend development.

However, before integration:

Mock responses must be clearly marked as mock data.

Real API responses must replace them.

No fake aircraft information should remain accidentally in the production/demo path.

No hard-coded answers should be used to simulate AI functionality during the final demo.

14. Git Rules

Recommended branches:

main
develop

feature/rag
feature/graphrag
feature/lightrag
feature/backend
feature/frontend
feature/visualization
feature/simulation

Rules

Do not directly push unfinished work to main.

Each feature should be developed on its own branch.

Commit messages should describe what changed.

Before merging, the developer must confirm that the module still follows the contract.

Breaking API/schema changes must be discussed before merging.

15. Definition of Done

A task is not finished just because the code runs on the developer's computer.

A feature is considered complete when:

The code runs.

The feature has been tested.

The input/output format is documented.

Required dependencies are documented.

Another team member can run/use it.

It follows the agreed project contract.

It does not require another developer to rewrite its internal code.

Any known limitations are documented.

16. Integration Rule

Every major module must provide:

1. Code

The actual implementation.

2. Usage example

Example:

result = service.ask(
    aircraft_id="a320",
    question="How does the engine work?",
    conversation_id="test_001"
)

3. Input specification

What does the module require?

4. Output specification

What does it return?

5. Setup instructions

How does another team member run it?

6. Test

At least one automated or reproducible test demonstrating that the module works.

17. Dependency Rule

No team member should make another person's module a hidden dependency without agreement.

For example:

Bad:

Nirmin's simulation
        |
        ↓
random internal function from backend.py

Good:

Nirmin's simulation
        |
        ↓
documented API / contract
        |
        ↓
Backend

This keeps the system modular.

18. Communication Rule

If a developer needs to change a shared contract, they must communicate:

What is changing?
Why is it changing?
Who will be affected?
What needs to be updated?

Small internal changes do not require discussion.

Changes to:

API request/response

database schema

IDs

file structure used by another module

shared data format

must be communicated.

19. Daily Development

The team works continuously during the development period.

A short daily synchronization should cover:

What I finished.

What I am doing today.

What is blocking me.

Whether I changed anything affecting another module.

The purpose is coordination, not reporting.

20. Development Priorities

The project should be developed in this order:

1. Shared contracts
       ↓
2. Basic working modules
       ↓
3. First integration
       ↓
4. Complete core functionality
       ↓
5. Visualization / creative features
       ↓
6. Evaluation
       ↓
7. UI polish
       ↓
8. Demo preparation

A beautiful interface is not considered a successful milestone if the core AI system does not work.

21. MVP

The minimum successful system should contain:

AI

RAG

GraphRAG

LightRAG

Shared aircraft knowledge base

Conversational question answering

Source information

Backend

API

Database

Aircraft data

Conversation handling

Frontend

Aircraft selection

AI assistant

Search/knowledge interface

Retrieval method integration

Visualization

At least one usable aircraft model

Selectable components

Basic engine visualization

Simulation

At least one functional "What If?" scenario

22. Evaluation

The final project should allow comparison of:

RAG

GraphRAG

LightRAG

using comparable questions.

Possible measurements:

Answer quality

Source relevance

Retrieval latency

Response latency

Retrieved context

Hallucination/error cases

The same question set should be used where practical.

23. Scope Rule

The project has a limited development period.

New ideas are welcome, but they must not endanger the MVP.

Priority:

MVP
  >
Core AI
  >
Integration
  >
Visualization
  >
Creative features
  >
Extra features

If a new feature threatens the completion of the core system, it should be moved to the future-work list.

24. Final Principle

Build modules, not isolated projects.

Each person's work must be designed so that it can become a component of the same system.

The goal is not:

"Three people made three good projects."

The goal is:

"Three people built three independent modules that work together as one coherent system."

Team Agreement

By contributing code to the project, each team member agrees to respect the shared contracts, communicate breaking changes, document their modules, and prioritize integration over isolated implementation.

Project name: AeroMind
Project type: Local academic/research prototype
Team: You / Sasha / Nirmin
Development period: 20 days + 3-day buffer