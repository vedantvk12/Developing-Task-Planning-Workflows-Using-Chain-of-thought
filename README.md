# Intelligent Task-Planning Workflows Using Chain-of-Thought, Tree-of-Thought, and ReAct

**Course**: Unit II: Reasoning, Planning and Decision-Making (CO-II)  
**Student Name**: Vedant Sattejkumar Kirange  
**Roll No**: 55  
**PRN**: ADT23SOCB1294  
**Institution**: MIT ADT University, Pune  

---

## 1. Project Overview

This project implements an autonomous, intelligent task-planning and decision-making system that unifies three core AI reasoning paradigms:
1. **Chain-of-Thought (CoT)**: Decomposes complex, ambiguous natural-language goals into ordered subtasks with explicit justifications, dependency graphs, and execution constraints.
2. **Tree-of-Thought (ToT)**: Explores a combinatorial decision tree of alternative travel strategies (Budget-Focused, Balanced, and Experience-Focused), computing rigorous mathematical cost estimates, multi-attribute scores (Cost, Feasibility, Experience), and pruning infeasible branches before execution.
3. **ReAct (Reasoning + Acting)**: Executes the chosen plan through an interleaved **THOUGHT → ACTION → OBSERVATION** loop against concrete Python tools and environment simulators.
4. **Dynamic Replanning & Fault Recovery**: Detects violated assumptions (e.g., room unavailability for Sunset Beach Resort) in real time via live tool observations, interrupts linear execution, dispatches fallback tools to select a verified alternative (Palm Breeze Budget Guesthouse), updates the in-flight plan state, and reconciles the final budget without restarting the workflow.

---

## 2. Core Goal & Constraints

**Mission Objective**:
> *"Plan a 2-day trip to Goa for 2 people within a total budget of ₹10,000, including transportation, accommodation, food and sightseeing."*

### Key Constraints:
- **Budget Ceiling**: ₹10,000 max (hard constraint).
- **Party Size**: 2 persons (all per-person expenses scale by 2).
- **Trip Duration**: 2 Days / 1 Night.
- **Geographic Scope**: Goa (requires inter-city transit and local commute).
- **Mandatory Categories**: Transportation, Accommodation, Food, and Sightseeing.

---

## 3. Unified Architecture & Workflow

```
               [ User Natural Language Travel Goal ]
                                 │
                                 ▼
       ┌──────────────────────────────────────────────────┐
       │   PHASE 1: CHAIN-OF-THOUGHT (CoT) REASONING      │
       │   - Entity & Constraint Parsing                  │
       │   - Subtask Decomposition with Justifications    │
       │   - Dependency Graph & Execution Order Mapping   │
       └─────────────────────────┬────────────────────────┘
                                 │
                                 ▼
       ┌──────────────────────────────────────────────────┐
       │   PHASE 2: TREE-OF-THOUGHT (ToT) TREE SEARCH     │
       │   - Branch 1: Plan A (Budget-Focused: ₹5,900)    │
       │   - Branch 2: Plan B (Balanced: ₹9,200) [BEST]   │
       │   - Branch 3: Plan C (Experience: ₹14,100) [FAIL]│
       │   - Multi-Criteria Scoring (Cost, Feas, Exp)     │
       │   - Select Top-Ranked Feasible Strategy (Plan B) │
       └─────────────────────────┬────────────────────────┘
                                 │
                                 ▼
       ┌──────────────────────────────────────────────────┐
       │   PHASE 3: ReAct EXECUTION & DYNAMIC REPLANNING  │
       │   ┌──────────────────────────────────────────┐   │
       │   │  THOUGHT: Contextual reasoning step      │   │
       │   │  ACTION: Execute concrete Python tool    │   │
       │   │  OBSERVATION: Inspect real environment   │   │
       │   └─────────────────────┬────────────────────┘   │
       │                         │                        │
       │       [Assumption Failure Detected: Hotel 404]   │
       │                         │                        │
       │   ┌─────────────────────▼────────────────────┐   │
       │   │  DYNAMIC REPLANNING & IN-FLIGHT RECOVERY │   │
       │   │  - Replan Tool -> Select Budget Guesthouse│  │
       │   │  - Cost Drops from ₹3,000 to ₹2,000      │   │
       │   │  - Update Plan & Continue Execution      │   │
       │   └──────────────────────────────────────────┘   │
       └─────────────────────────┬────────────────────────┘
                                 │
                                 ▼
       ┌──────────────────────────────────────────────────┐
       │   PHASE 4: FINAL BUDGET AUDIT & PERSISTENCE      │
       │   - Total Spent: ₹8,200 | Buffer: ₹1,800         │
       │   - Execution Trace, Candidate Plans & Plan JSON │
       └──────────────────────────────────────────────────┘
```

---

## 4. Tree-of-Thought Candidate Evaluation

| Plan ID | Strategy Name | Total Cost | Feasible? | Cost Score | Experience Score | Composite Score | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Plan A** | Budget-Focused | ₹5,900 | YES | 70.5 | 55.0 | 75.40 | Feasible (High savings, basic comfort) |
| **Plan B** | Balanced Travel | ₹9,200 | YES | 54.0 | 88.0 | **82.00** | **SELECTED (Optimal balance)** |
| **Plan C** | Experience-Focused | ₹14,100 | NO | 0.0 | 96.0 | 33.60 | Disqualified (Exceeds ₹10,000 budget) |

---

## 5. Directory Structure

```
react-travel-agent/
│
├── main.py              # Main execution coordinator (CoT -> ToT -> ReAct)
├── agent.py             # ReAct Agent loop, trace logging, failure handler
├── reasoning.py         # Chain-of-Thought (CoT) decomposition and dependency mapping
├── tree_search.py       # Tree-of-Thought (ToT) branch exploration and scoring
├── planner.py           # Task sequence creation and dynamic replanning task insertion
├── tools.py             # Concrete Python tools (transport, hotel, food, sightseeing)
├── models.py            # Dataclasses and Enums (Goal, Task, CandidatePlan, Trace)
├── README.md            # Comprehensive project documentation
└── outputs/
    ├── execution_trace.txt    # Complete THOUGHT -> ACTION -> OBSERVATION trace
    ├── candidate_plans.json   # Machine-readable ToT candidate comparisons
    └── final_plan.json        # Comprehensive final executed plan state
```

---

## 6. Installation & Execution

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Standard library modules (no third-party dependencies required for execution).

### Execution Command
```bash
# Navigate to the project directory
cd "react-travel-agent"

# Run the complete unified planning pipeline
python main.py
```

### Passing a Custom Goal
```bash
python main.py "Plan a 3-day trip to Goa for 2 people within a total budget of ₹15,000"
```

---

## 7. Dynamic Replanning Case Study

During execution of Task 2 (`search_accommodation`), the agent attempts to book **Sunset Beach Resort** for ₹3,000. The tool checks real catalog inventory and returns:
> `Selected hotel 'Sunset Beach Resort' is unavailable. (Fully booked for the selected dates due to peak weekend season.)`

### Agent Recovery Actions:
1. **Detects Assumption Failure**: Intercepts `success=False` without crashing.
2. **Records Observation**: Logs the error message into the execution trace.
3. **Reasoning Synthesis**: Formulates a thought explaining that the original plan cannot proceed as-is and that an alternative budget guesthouse is required.
4. **Tool Dispatch**: Executes `replan_accommodation()`, booking **Palm Breeze Budget Guesthouse** for **₹2,000**.
5. **In-Flight Plan Mutation**: Modifies the active task list, setting status `REPLANNED` and replacing the cost.
6. **Reconciled Budget**: Recalculates final expenditure:
   - Transport: ₹2,000
   - Accommodation: ₹2,000 (Saved ₹1,000!)
   - Food: ₹3,000
   - Sightseeing: ₹1,200
   - **Total**: ₹8,200 (Well within ₹10,000 ceiling, leaving ₹1,800 safety buffer).

---

## 8. Author Information

- **Student**: Vedant Sattejkumar Kirange
- **PRN**: ADT23SOCB1294 | **Roll No**: 55
- **Course**: Experiential Learning Unit II (Reasoning, Planning and Decision-Making)
- **University**: MIT ADT University, Pune

