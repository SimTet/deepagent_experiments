"""Custom tools for the Project Kickoff Agent.

These tools supplement the native deepagent tools (write_file, read_file, write_todos, task).
They provide templates and validation to ensure consistent, high-quality deliverables.
"""

from typing import Literal

from langchain_core.tools import tool


@tool(parse_docstring=True)
def get_deliverable_template(
    deliverable_type: Literal["architecture", "tasks", "risks", "project_plan"],
) -> str:
    """Get a markdown template for a specific project deliverable.

    Use this to ensure consistent structure across all project documents.

    Args:
        deliverable_type: Type of deliverable template needed.

    Returns:
        Markdown template string for the requested deliverable type.
    """
    templates = {
        "architecture": """# Architecture Document: {PROJECT_NAME}

**Version**: 1.0
**Date**: {DATE}
**Author**: Architecture Subagent

---

## 1. System Overview

### 1.1 Purpose
{Describe the system's purpose and objectives}

### 1.2 Scope
{Define what is in and out of scope}

### 1.3 Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

---

## 2. Architecture Diagram

```
{ASCII diagram of system architecture}
```

---

## 3. Component Design

### 3.1 Frontend
{Frontend component descriptions}

### 3.2 Backend Services
{Backend service descriptions}

### 3.3 Data Layer
{Database and storage descriptions}

### 3.4 External Integrations
{Third-party service integrations}

---

## 4. Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| Frontend | | |
| Backend | | |
| Database | | |
| Infrastructure | | |

---

## 5. Non-Functional Requirements

### 5.1 Scalability
{Scalability approach}

### 5.2 Security
{Security considerations}

### 5.3 Performance
{Performance targets}

### 5.4 Monitoring
{Monitoring strategy}

---

## 6. Decisions Log

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| | | |
""",
        "tasks": """# Task Breakdown: {PROJECT_NAME}

**Version**: 1.0
**Date**: {DATE}
**Author**: Task Planner Subagent

---

## Executive Summary

- **Total Epics**: {N}
- **Total Tasks**: {N}
- **Estimated Duration**: {N weeks}
- **Recommended Team Size**: {N}

---

## Epic Overview

| Epic ID | Name | Priority | Effort | Tasks |
|---------|------|----------|--------|-------|
| EPIC-1 | | High | L | 5 |
| EPIC-2 | | Medium | M | 4 |

---

## Detailed Breakdown

### EPIC-1: {Epic Name}

**Description**: {What this epic delivers}
**Priority**: High
**Effort**: Large (2-3 weeks)

| Task ID | Description | Effort | Dependencies | Assignee |
|---------|-------------|--------|--------------|----------|
| T1.1 | | 2d | - | |
| T1.2 | | 3d | T1.1 | |
| T1.3 | | 1d | - | |

---

## Dependency Graph

```
{ASCII dependency diagram}
```

---

## Suggested Timeline

| Phase | Duration | Epics | Milestone |
|-------|----------|-------|-----------|
| Phase 1 - MVP | Weeks 1-4 | EPIC-1, EPIC-2 | MVP Release |
| Phase 2 - Core | Weeks 5-8 | EPIC-3, EPIC-4 | Feature Complete |
| Phase 3 - Polish | Weeks 9-10 | EPIC-5 | Production Ready |

---

## Team Recommendations

### Required Roles
- Role 1: {Description}
- Role 2: {Description}

### Key Skills
- Skill 1
- Skill 2
""",
        "risks": """# Risk Assessment: {PROJECT_NAME}

**Version**: 1.0
**Date**: {DATE}
**Author**: Risk Assessor Subagent

---

## Executive Summary

- **Total Risks Identified**: {N}
- **Critical Risks**: {N}
- **Overall Risk Level**: {Low/Medium/High}

---

## Risk Matrix

```
              │ Low Impact  │ Med Impact  │ High Impact │
──────────────┼─────────────┼─────────────┼─────────────┤
High Prob     │             │             │  RISK-XXX   │
Medium Prob   │             │  RISK-XXX   │             │
Low Prob      │  RISK-XXX   │             │             │
```

---

## Risk Register

### RISK-001: {Risk Name}

| Attribute | Value |
|-----------|-------|
| **Category** | Technical / Resource / Timeline / External |
| **Probability** | Low / Medium / High |
| **Impact** | Low / Medium / High |
| **Risk Score** | {1-9} |
| **Status** | Open / Mitigating / Closed |

**Description**:
{Detailed risk description}

**Warning Indicators**:
- Indicator 1
- Indicator 2

**Mitigation Strategy**:
1. Preventive action
2. Contingency plan

**Owner**: {Role}

---

## Top Risks to Watch

1. **RISK-XXX**: {Brief description}
2. **RISK-XXX**: {Brief description}
3. **RISK-XXX**: {Brief description}

---

## Risk Response Plan

### Monitoring
- Weekly risk review meetings
- Automated monitoring for technical risks

### Escalation Path
1. Project Manager (first line)
2. Technical Lead (technical risks)
3. Steering Committee (critical risks)

### Review Frequency
- High risks: Weekly
- Medium risks: Bi-weekly
- Low risks: Monthly
""",
        "project_plan": """# Project Plan: {PROJECT_NAME}

**Version**: 1.0
**Date**: {DATE}
**Status**: Draft

---

## 1. Executive Summary

{High-level project overview - 2-3 paragraphs}

---

## 2. Project Overview

### 2.1 Vision
{What success looks like}

### 2.2 Objectives
1. Objective 1
2. Objective 2
3. Objective 3

### 2.3 Success Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| | | |

---

## 3. Architecture Summary

{Summary from architecture.md - key decisions and components}

**Key Components**:
- Component 1
- Component 2

**Technology Choices**:
- Choice 1: {Rationale}
- Choice 2: {Rationale}

[Full details: /docs/architecture.md]

---

## 4. Work Breakdown Summary

{Summary from tasks.md - epics and timeline}

**Epics**:
1. EPIC-1: {Name} - {Effort}
2. EPIC-2: {Name} - {Effort}

**Timeline**:
- Phase 1: {Duration} - {Milestone}
- Phase 2: {Duration} - {Milestone}

[Full details: /docs/tasks.md]

---

## 5. Risk Summary

{Summary from risks.md - top risks}

**Critical Risks**:
1. RISK-XXX: {Name} - {Mitigation}
2. RISK-XXX: {Name} - {Mitigation}

**Overall Risk Level**: {Low/Medium/High}

[Full details: /docs/risks.md]

---

## 6. Team & Resources

### Recommended Team
| Role | Count | Responsibilities |
|------|-------|------------------|
| | | |

### Budget Considerations
- {Item 1}
- {Item 2}

---

## 7. Next Steps

1. [ ] Review and approve this plan
2. [ ] Assemble project team
3. [ ] Set up development environment
4. [ ] Begin Phase 1 execution

---

## Appendices

- [Architecture Document](/docs/architecture.md)
- [Task Breakdown](/docs/tasks.md)
- [Risk Assessment](/docs/risks.md)
""",
    }

    if deliverable_type not in templates:
        return f"Error: Unknown template type '{deliverable_type}'. Valid types: architecture, tasks, risks, project_plan"

    return templates[deliverable_type]


@tool(parse_docstring=True)
def validate_project_plan() -> str:
    """Validate that all required project deliverables have been created.

    Checks for the existence of required documents and returns a validation report.
    This tool reads from the agent's virtual filesystem.

    Returns:
        Validation report indicating which deliverables exist and which are missing.
    """
    # This tool is informational - it tells the agent what to check
    # The actual file checking is done by the agent using read_file

    required_deliverables = [
        ("/docs/architecture.md", "Architecture Document"),
        ("/docs/tasks.md", "Task Breakdown"),
        ("/docs/risks.md", "Risk Assessment"),
        ("/docs/PROJECT_PLAN.md", "Final Project Plan"),
    ]

    report = """## Project Deliverables Checklist

Use `read_file` to verify each deliverable exists:

| Path | Deliverable | Status |
|------|-------------|--------|
"""

    for path, name in required_deliverables:
        report += f"| `{path}` | {name} | Use read_file to check |\n"

    report += """
### Validation Steps

1. Use `read_file` for each path above
2. If file exists, mark as complete
3. If file is missing, delegate to appropriate subagent
4. Once all files exist, compile PROJECT_PLAN.md

### Quality Checks

For each deliverable, verify:
- [ ] Document has meaningful content (not just template)
- [ ] All sections are filled in
- [ ] Consistent project name across documents
- [ ] No placeholder text remaining
"""

    return report
