"""AI Governance assessment tools for questionnaire management."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from langchain_core.tools import tool

# Directories
QUESTIONNAIRE_DIR = Path(__file__).parent.parent / "questionnaire"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Assessment state file
ASSESSMENT_FILE = OUTPUT_DIR / "current_assessment.json"


def parse_questionnaire() -> dict[str, Any]:
    """Parse the governance questionnaire markdown into structured format."""
    questionnaire_path = QUESTIONNAIRE_DIR / "governance_questionnaire.md"
    content = questionnaire_path.read_text()

    sections: dict[str, Any] = {}
    current_section = None
    current_question: dict[str, Any] = {}

    for line in content.split("\n"):
        line = line.strip()

        # Section header
        if line.startswith("## Section"):
            match = re.match(r"## Section (\d+): (.+)", line)
            if match:
                section_num = match.group(1)
                section_name = match.group(2)
                current_section = {
                    "number": section_num,
                    "name": section_name,
                    "questions": {},
                }
                sections[f"S{section_num}"] = current_section

        # Question ID
        elif line.startswith("### Q"):
            if current_question and current_section:
                qid = current_question.get("id")
                if qid:
                    current_section["questions"][qid] = current_question
            match = re.match(r"### (Q[\d.]+) - (.+)", line)
            if match:
                current_question = {
                    "id": match.group(1),
                    "title": match.group(2),
                    "question": "",
                    "type": "text",
                    "required": True,
                    "options": None,
                }

        # Question text
        elif line.startswith("**Question:**"):
            current_question["question"] = line.replace("**Question:**", "").strip()

        # Options
        elif line.startswith("**Options:**"):
            options = line.replace("**Options:**", "").strip()
            current_question["options"] = [o.strip() for o in options.split(",")]
            current_question["type"] = "choice"

        # Type
        elif line.startswith("**Type:**"):
            current_question["type"] = line.replace("**Type:**", "").strip()

        # Required
        elif line.startswith("**Required:**"):
            current_question["required"] = (
                line.replace("**Required:**", "").strip().lower() == "true"
            )

    # Add last question
    if current_question and current_section:
        qid = current_question.get("id")
        if qid:
            current_section["questions"][qid] = current_question

    return sections


def load_assessment() -> dict[str, Any]:
    """Load or create the current assessment state."""
    if ASSESSMENT_FILE.exists():
        return json.loads(ASSESSMENT_FILE.read_text())
    return {
        "created": datetime.now().isoformat(),
        "status": "in_progress",
        "answers": {},
        "metadata": {},
    }


def save_assessment(assessment: dict[str, Any]) -> None:
    """Save the assessment state."""
    assessment["updated"] = datetime.now().isoformat()
    ASSESSMENT_FILE.write_text(json.dumps(assessment, indent=2))


@tool(parse_docstring=True)
def load_questionnaire() -> str:
    """Load the AI Governance questionnaire and return an overview.

    Use this at the start of an assessment to understand the full scope
    of questions that need to be answered.

    Returns:
        Overview of all sections and questions in the questionnaire.
    """
    sections = parse_questionnaire()
    assessment = load_assessment()
    answered = set(assessment.get("answers", {}).keys())

    result = "# AI Governance Questionnaire Overview\n\n"

    total_questions = 0
    total_answered = 0

    for section_id, section in sections.items():
        questions = section["questions"]
        section_answered = sum(1 for q in questions if q in answered)
        total_questions += len(questions)
        total_answered += section_answered

        result += f"## {section['name']}\n"
        result += f"**Questions:** {len(questions)} | **Answered:** {section_answered}\n\n"

        for qid, q in questions.items():
            status = "[x]" if qid in answered else "[ ]"
            required = "*" if q["required"] else ""
            result += f"- {status} **{qid}**: {q['title']}{required}\n"

        result += "\n"

    result += f"---\n**Total Progress:** {total_answered}/{total_questions} questions answered\n"
    result += "\n*Questions marked with * are required.*"

    return result


@tool(parse_docstring=True)
def get_question(question_id: str) -> str:
    """Get the details of a specific question to ask the user.

    Use this to retrieve the full question text, options (if applicable),
    and any guidance before asking the user.

    Args:
        question_id: The question ID (e.g., 'Q1.1', 'Q2.3', 'Q4.5').

    Returns:
        Full question details including text, type, and options if applicable.
    """
    sections = parse_questionnaire()
    assessment = load_assessment()

    # Find the question
    for section_id, section in sections.items():
        if question_id in section["questions"]:
            q = section["questions"][question_id]
            current_answer = assessment.get("answers", {}).get(question_id)

            result = f"## {question_id}: {q['title']}\n\n"
            result += f"**Section:** {section['name']}\n"
            result += f"**Required:** {'Yes' if q['required'] else 'No'}\n\n"
            result += f"### Question\n{q['question']}\n\n"

            if q["options"]:
                result += "### Options\n"
                for i, opt in enumerate(q["options"], 1):
                    result += f"{i}. {opt}\n"
                result += "\n"

            if current_answer:
                result += f"### Current Answer\n{current_answer}\n\n"
                result += "*This question has already been answered. The user can update it if needed.*\n"

            return result

    return f"Error: Question '{question_id}' not found in the questionnaire."


@tool(parse_docstring=True)
def save_answer(question_id: str, answer: str, notes: Optional[str] = None) -> str:
    """Save the user's answer to a specific question.

    Use this after the user has provided their response to a question.
    The answer will be stored and the assessment file updated.

    Args:
        question_id: The question ID (e.g., 'Q1.1', 'Q2.3').
        answer: The user's answer to the question.
        notes: Optional additional notes or context for the answer.

    Returns:
        Confirmation message with updated progress.
    """
    sections = parse_questionnaire()
    assessment = load_assessment()

    # Validate question exists
    question_found = False
    question_title = ""
    section_name = ""

    for section_id, section in sections.items():
        if question_id in section["questions"]:
            question_found = True
            question_title = section["questions"][question_id]["title"]
            section_name = section["name"]
            break

    if not question_found:
        return f"Error: Question '{question_id}' not found in the questionnaire."

    # Save the answer
    if "answers" not in assessment:
        assessment["answers"] = {}

    assessment["answers"][question_id] = {
        "answer": answer,
        "notes": notes,
        "timestamp": datetime.now().isoformat(),
    }

    save_assessment(assessment)

    # Calculate progress
    total_questions = sum(
        len(s["questions"]) for s in sections.values()
    )
    answered_count = len(assessment["answers"])

    return (
        f"Answer saved successfully!\n\n"
        f"**Question:** {question_id} - {question_title}\n"
        f"**Section:** {section_name}\n"
        f"**Answer:** {answer[:200]}{'...' if len(answer) > 200 else ''}\n\n"
        f"**Progress:** {answered_count}/{total_questions} questions answered"
    )


@tool(parse_docstring=True)
def get_assessment_progress() -> str:
    """Get the current progress of the AI governance assessment.

    Use this to check how many questions have been answered and
    identify which sections still need attention.

    Returns:
        Progress summary with section-by-section breakdown.
    """
    sections = parse_questionnaire()
    assessment = load_assessment()
    answered = set(assessment.get("answers", {}).keys())

    result = "# Assessment Progress\n\n"
    result += f"**Started:** {assessment.get('created', 'Unknown')}\n"
    result += f"**Last Updated:** {assessment.get('updated', 'Not yet')}\n"
    result += f"**Status:** {assessment.get('status', 'in_progress')}\n\n"

    total_questions = 0
    total_answered = 0
    total_required = 0
    required_answered = 0

    result += "## Section Progress\n\n"
    result += "| Section | Total | Answered | Required | Req. Answered |\n"
    result += "|---------|-------|----------|----------|---------------|\n"

    for section_id, section in sections.items():
        questions = section["questions"]
        sect_total = len(questions)
        sect_answered = sum(1 for q in questions if q in answered)
        sect_required = sum(1 for q in questions.values() if q["required"])
        sect_req_answered = sum(
            1 for qid, q in questions.items() if q["required"] and qid in answered
        )

        total_questions += sect_total
        total_answered += sect_answered
        total_required += sect_required
        required_answered += sect_req_answered

        status_icon = "Complete" if sect_answered == sect_total else "In Progress"
        result += f"| {section['name']} | {sect_total} | {sect_answered} | {sect_required} | {sect_req_answered} |\n"

    result += f"\n**Overall Progress:** {total_answered}/{total_questions} ({100*total_answered//total_questions if total_questions else 0}%)\n"
    result += f"**Required Questions:** {required_answered}/{total_required} answered\n"

    if required_answered < total_required:
        result += "\n### Unanswered Required Questions\n\n"
        for section_id, section in sections.items():
            for qid, q in section["questions"].items():
                if q["required"] and qid not in answered:
                    result += f"- **{qid}**: {q['title']} ({section['name']})\n"

    return result


@tool(parse_docstring=True)
def get_current_answers(section_filter: Optional[str] = None) -> str:
    """Get all current answers in the assessment.

    Use this to review what has been answered so far, optionally
    filtered by section.

    Args:
        section_filter: Optional section number to filter (e.g., '1', '2', '3').

    Returns:
        List of all current answers organized by section.
    """
    sections = parse_questionnaire()
    assessment = load_assessment()
    answers = assessment.get("answers", {})

    if not answers:
        return "No answers have been recorded yet. Start by loading the questionnaire and asking questions."

    result = "# Current Assessment Answers\n\n"

    for section_id, section in sections.items():
        section_num = section["number"]

        if section_filter and section_num != section_filter:
            continue

        section_answers = {
            qid: answers[qid]
            for qid in section["questions"]
            if qid in answers
        }

        if not section_answers:
            continue

        result += f"## Section {section_num}: {section['name']}\n\n"

        for qid, answer_data in section_answers.items():
            q = section["questions"][qid]
            result += f"### {qid}: {q['title']}\n"
            result += f"**Answer:** {answer_data['answer']}\n"
            if answer_data.get("notes"):
                result += f"**Notes:** {answer_data['notes']}\n"
            result += "\n"

    return result


@tool(parse_docstring=True)
def generate_assessment_report(
    use_case_name: Optional[str] = None,
    assessor_name: Optional[str] = None,
) -> str:
    """Generate the final AI Governance Assessment Report.

    Use this when all required questions have been answered to create
    the final assessment document. The report will be saved as a markdown file.

    Args:
        use_case_name: Optional override for the use case name (defaults to Q1.1 answer).
        assessor_name: Optional name of the person conducting the assessment.

    Returns:
        Path to the generated report and a summary of findings.
    """
    sections = parse_questionnaire()
    assessment = load_assessment()
    answers = assessment.get("answers", {})

    # Check required questions
    missing_required = []
    for section_id, section in sections.items():
        for qid, q in section["questions"].items():
            if q["required"] and qid not in answers:
                missing_required.append(f"{qid}: {q['title']}")

    if missing_required:
        return (
            "Cannot generate report - the following required questions are unanswered:\n\n"
            + "\n".join(f"- {q}" for q in missing_required)
            + "\n\nPlease answer all required questions before generating the report."
        )

    # Get use case name
    if not use_case_name:
        use_case_name = answers.get("Q1.1", {}).get("answer", "Unnamed AI Use Case")

    # Generate report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = f"""# AI Governance Assessment Report

**Use Case:** {use_case_name}
**Assessment Date:** {timestamp}
**Assessor:** {assessor_name or 'Not specified'}
**Status:** Complete

---

"""

    # Add each section
    for section_id, section in sections.items():
        report += f"## {section['name']}\n\n"

        for qid, q in section["questions"].items():
            answer_data = answers.get(qid, {})
            answer = answer_data.get("answer", "*Not answered*")
            notes = answer_data.get("notes")

            report += f"### {q['title']}\n\n"
            report += f"**Question:** {q['question']}\n\n"
            report += f"**Answer:** {answer}\n\n"

            if notes:
                report += f"**Additional Notes:** {notes}\n\n"

            report += "---\n\n"

    # Add summary section
    report += """## Assessment Summary

### Risk Overview

Based on the responses provided, the following key areas require attention:

"""

    # Analyze key risk indicators
    ai_classification = answers.get("Q4.1", {}).get("answer", "")
    personal_data = answers.get("Q3.1", {}).get("answer", "")
    special_category = answers.get("Q3.2", {}).get("answer", "")
    dpia_status = answers.get("Q3.8", {}).get("answer", "")
    ethical_review = answers.get("Q5.8", {}).get("answer", "")

    if "High Risk" in ai_classification or "Unacceptable" in ai_classification:
        report += "- **EU AI Act:** This system is classified as HIGH RISK and requires enhanced compliance measures.\n"
    if "Yes" in personal_data:
        report += "- **Data Privacy:** Personal data is processed - ensure GDPR compliance.\n"
    if "Yes" in special_category:
        report += "- **Special Category Data:** Special category data processing requires additional safeguards.\n"
    if "Not" in dpia_status or "Uncertain" in dpia_status:
        report += "- **DPIA:** A Data Protection Impact Assessment may be required.\n"
    if "Not" in ethical_review:
        report += "- **Ethics:** An ethical review should be considered.\n"

    report += """
### Next Steps

1. Review all flagged risk areas
2. Implement recommended controls
3. Schedule periodic reassessment
4. Document any changes to the AI system

---

*This report was generated by the AI Governance Agent.*
*Review date should be scheduled according to the response in Q6.3.*
"""

    # Save report
    safe_name = re.sub(r"[^\w\s-]", "", use_case_name.lower())
    safe_name = re.sub(r"[\s-]+", "_", safe_name)[:50]
    report_filename = f"assessment_{safe_name}_{datetime.now().strftime('%Y%m%d')}.md"
    report_path = OUTPUT_DIR / report_filename

    report_path.write_text(report)

    # Update assessment status
    assessment["status"] = "completed"
    assessment["report_file"] = report_filename
    save_assessment(assessment)

    return (
        f"Assessment report generated successfully!\n\n"
        f"**File:** {report_path}\n"
        f"**Use Case:** {use_case_name}\n\n"
        f"The complete assessment has been saved. You can share this report with stakeholders."
    )


@tool(parse_docstring=True)
def start_new_assessment() -> str:
    """Start a fresh AI governance assessment.

    Use this to begin a new assessment, clearing any previous answers.
    Previous assessments are preserved as completed reports.

    Returns:
        Confirmation that a new assessment has been started.
    """
    # Archive existing assessment if it exists
    if ASSESSMENT_FILE.exists():
        existing = load_assessment()
        if existing.get("answers"):
            archive_name = f"assessment_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            archive_path = OUTPUT_DIR / archive_name
            archive_path.write_text(json.dumps(existing, indent=2))

    # Create fresh assessment
    new_assessment = {
        "created": datetime.now().isoformat(),
        "status": "in_progress",
        "answers": {},
        "metadata": {},
    }
    save_assessment(new_assessment)

    return (
        "New AI Governance Assessment started!\n\n"
        "The questionnaire covers the following areas:\n"
        "1. General Information\n"
        "2. IT Security\n"
        "3. Data Privacy (GDPR)\n"
        "4. EU AI Act Compliance\n"
        "5. AI Ethics\n"
        "6. Implementation and Monitoring\n\n"
        "Use `load_questionnaire` to see all questions, or start asking questions directly."
    )
