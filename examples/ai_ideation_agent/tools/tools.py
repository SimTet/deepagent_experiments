"""AI Ideation Canvas tools for guided idea capture and export."""

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

# Canvas state file
CANVAS_FILE = OUTPUT_DIR / "current_canvas.json"

# Section metadata for navigation
SECTION_INFO = {
    "S1": {"name": "Stakeholders", "description": "Identify key stakeholders and owners"},
    "S2": {"name": "Problem & Goal", "description": "Define the problem and success criteria"},
    "S3": {"name": "Value Proposition", "description": "Quantify the business value"},
    "S4": {"name": "Classification", "description": "Categorize the AI initiative"},
    "S5": {"name": "Data Requirements", "description": "Identify data sources and needs"},
    "S6": {"name": "Data Privacy", "description": "Quick privacy checklist"},
    "S7": {"name": "IT Security", "description": "Quick security checklist"},
    "S8": {"name": "EU AI Act", "description": "Quick regulatory checklist"},
    "S9": {"name": "Summary & Next Steps", "description": "Risks, approvals, and actions"},
}


def parse_canvas() -> dict[str, Any]:
    """Parse the ideation canvas markdown into structured format."""
    canvas_path = QUESTIONNAIRE_DIR / "ideation_canvas.md"
    content = canvas_path.read_text()

    sections: dict[str, Any] = {}
    current_section = None
    current_question: dict[str, Any] = {}

    for line in content.split("\n"):
        line = line.strip()

        # Section header
        if line.startswith("## Section"):
            # Save the last question from the previous section before switching
            if current_question and current_section:
                qid = current_question.get("id")
                if qid:
                    current_section["questions"][qid] = current_question
                current_question = {}

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


def load_canvas() -> dict[str, Any]:
    """Load or create the current canvas state."""
    if CANVAS_FILE.exists():
        return json.loads(CANVAS_FILE.read_text())
    return {
        "created": datetime.now().isoformat(),
        "status": "in_progress",
        "use_case_name": "",
        "answers": {},
        "metadata": {},
    }


def save_canvas(canvas: dict[str, Any]) -> None:
    """Save the canvas state."""
    canvas["updated"] = datetime.now().isoformat()
    CANVAS_FILE.write_text(json.dumps(canvas, indent=2))


@tool(parse_docstring=True)
def start_new_canvas(use_case_name: str) -> str:
    """Start a new AI Use Case Canvas with the given name.

    Use this at the beginning of an ideation session to initialize a fresh canvas.
    Any existing canvas will be archived.

    Args:
        use_case_name: The name of the AI use case being ideated.

    Returns:
        Confirmation message with canvas overview.
    """
    # Archive existing canvas if present
    if CANVAS_FILE.exists():
        existing = load_canvas()
        if existing.get("answers"):
            archive_name = f"canvas_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            archive_path = OUTPUT_DIR / archive_name
            archive_path.write_text(json.dumps(existing, indent=2))

    # Create fresh canvas
    new_canvas = {
        "created": datetime.now().isoformat(),
        "status": "in_progress",
        "use_case_name": use_case_name,
        "answers": {},
        "metadata": {},
    }
    save_canvas(new_canvas)

    sections_overview = "\n".join(
        f"  {sid}. {info['name']} - {info['description']}"
        for sid, info in SECTION_INFO.items()
    )

    return (
        f"New AI Use Case Canvas started!\n\n"
        f"**Use Case:** {use_case_name}\n\n"
        f"The canvas covers 9 sections:\n{sections_overview}\n\n"
        f"Use `load_canvas_template` to see all questions, or start with Section 1."
    )


@tool(parse_docstring=True)
def get_canvas_overview() -> str:
    """Get an overview of all canvas sections and their questions.

    Use this ONCE at the start to understand the full scope of the canvas.
    Shows all 9 sections, their questions, and which are already answered.
    For detailed progress tracking, use get_canvas_progress instead.

    Returns:
        Overview of all sections and questions with completion status.
    """
    sections = parse_canvas()
    canvas = load_canvas()
    answered = set(canvas.get("answers", {}).keys())

    result = "# AI Use Case Canvas Overview\n\n"
    result += f"**Use Case:** {canvas.get('use_case_name', 'Not started')}\n"
    result += f"**Status:** {canvas.get('status', 'in_progress')}\n\n"

    total_questions = 0
    total_answered = 0

    for section_id, section in sections.items():
        questions = section["questions"]
        section_answered = sum(1 for q in questions if q in answered)
        total_questions += len(questions)
        total_answered += section_answered

        status_icon = "Complete" if section_answered == len(questions) else "In Progress" if section_answered > 0 else "Not Started"
        result += f"## {section_id}: {section['name']} [{status_icon}]\n"
        result += f"**Questions:** {len(questions)} | **Answered:** {section_answered}\n\n"

        for qid, q in questions.items():
            checkbox = "[x]" if qid in answered else "[ ]"
            required = "*" if q["required"] else ""
            result += f"- {checkbox} **{qid}**: {q['title']}{required}\n"

        result += "\n"

    result += f"---\n**Total Progress:** {total_answered}/{total_questions} questions answered\n"
    result += "\n*Questions marked with * are required for export.*"

    return result


@tool(parse_docstring=True)
def get_section(section_id: str) -> str:
    """Get all questions for a specific section of the canvas.

    Use this to focus on one section at a time during the guided workflow.

    Args:
        section_id: The section ID (e.g., 'S1', 'S2', ..., 'S9') or number ('1', '2', ..., '9').

    Returns:
        All questions in the section with current answers if any.
    """
    # Normalize section_id
    if not section_id.startswith("S"):
        section_id = f"S{section_id}"

    sections = parse_canvas()
    canvas = load_canvas()
    answers = canvas.get("answers", {})

    if section_id not in sections:
        return f"Error: Section '{section_id}' not found. Valid sections are S1-S9."

    section = sections[section_id]
    result = f"# Section {section['number']}: {section['name']}\n\n"

    for qid, q in section["questions"].items():
        current_answer = answers.get(qid, {}).get("answer")
        required = " *(required)*" if q["required"] else " *(optional)*"

        result += f"## {qid}: {q['title']}{required}\n\n"
        result += f"**Question:** {q['question']}\n\n"

        if q["options"]:
            result += "**Options:**\n"
            for i, opt in enumerate(q["options"], 1):
                result += f"  {i}. {opt}\n"
            result += "\n"

        if current_answer:
            result += f"**Current Answer:** {current_answer}\n\n"
        else:
            result += "*Not yet answered*\n\n"

        result += "---\n\n"

    return result


@tool(parse_docstring=True)
def get_question(question_id: str) -> str:
    """Get details for a specific question by its ID.

    Use this when the user asks about a specific question or when you need
    to present a single question rather than a whole section.

    Args:
        question_id: The question ID (e.g., 'Q1.1', 'Q3.2', 'Q8.1').

    Returns:
        Question details including text, options (if any), and current answer.
    """
    sections = parse_canvas()
    canvas = load_canvas()
    answers = canvas.get("answers", {})

    # Find the question
    for section_id, section in sections.items():
        if question_id in section["questions"]:
            q = section["questions"][question_id]
            current_answer = answers.get(question_id, {}).get("answer")
            required = "Yes" if q["required"] else "No"

            result = f"## {question_id}: {q['title']}\n\n"
            result += f"**Section:** {section['name']}\n"
            result += f"**Required:** {required}\n\n"
            result += f"**Question:** {q['question']}\n\n"

            if q["options"]:
                result += "**Options:**\n"
                for i, opt in enumerate(q["options"], 1):
                    result += f"  {i}. {opt}\n"
                result += "\n"

            if current_answer:
                result += f"**Current Answer:** {current_answer}\n"
            else:
                result += "*Not yet answered*\n"

            return result

    return f"Error: Question '{question_id}' not found. Use format like 'Q1.1', 'Q3.2', etc."


@tool(parse_docstring=True)
def save_answer(question_id: str, answer: str, notes: Optional[str] = None) -> str:
    """Save a single answer to a specific question.

    Use this when the user provides one answer at a time.
    For multiple answers at once, use save_section_answers instead.

    Args:
        question_id: The question ID (e.g., 'Q1.1', 'Q2.3').
        answer: The user's answer to the question.
        notes: Optional additional notes or context.

    Returns:
        Confirmation message with updated progress.
    """
    sections = parse_canvas()
    canvas = load_canvas()

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
        return f"Error: Question '{question_id}' not found in the canvas."

    # Save the answer
    if "answers" not in canvas:
        canvas["answers"] = {}

    canvas["answers"][question_id] = {
        "answer": answer,
        "notes": notes,
        "timestamp": datetime.now().isoformat(),
    }

    save_canvas(canvas)

    # Calculate progress
    total_questions = sum(len(s["questions"]) for s in sections.values())
    answered_count = len(canvas["answers"])
    required_total = sum(
        1 for s in sections.values() for q in s["questions"].values() if q["required"]
    )
    required_answered = sum(
        1 for s in sections.values()
        for qid, q in s["questions"].items()
        if q["required"] and qid in canvas["answers"]
    )

    return (
        f"Answer saved!\n\n"
        f"**Question:** {question_id} - {question_title}\n"
        f"**Section:** {section_name}\n"
        f"**Answer:** {answer[:200]}{'...' if len(answer) > 200 else ''}\n\n"
        f"**Progress:** {answered_count}/{total_questions} total | {required_answered}/{required_total} required"
    )


@tool(parse_docstring=True)
def save_section_answers(section_id: str, answers: dict[str, str]) -> str:
    """Save multiple answers for a section at once.

    Use this when the user provides multiple answers in a single message.
    More efficient than calling save_answer multiple times.

    Args:
        section_id: The section ID (e.g., 'S1', '1', 'S2', '2').
        answers: Dictionary mapping question IDs to answers, e.g., {"Q1.1": "Lisa Chen", "Q1.2": "David Park"}.

    Returns:
        Confirmation message with all saved answers and progress.
    """
    # Normalize section_id
    if not section_id.startswith("S"):
        section_id = f"S{section_id}"

    sections = parse_canvas()
    canvas = load_canvas()

    if section_id not in sections:
        return f"Error: Section '{section_id}' not found. Valid sections are S1-S9."

    section = sections[section_id]
    valid_questions = set(section["questions"].keys())

    # Validate all question IDs
    invalid_ids = [qid for qid in answers.keys() if qid not in valid_questions]
    if invalid_ids:
        return f"Error: Invalid question IDs for {section_id}: {invalid_ids}. Valid IDs: {list(valid_questions)}"

    if "answers" not in canvas:
        canvas["answers"] = {}

    # Save all answers
    saved = []
    for question_id, answer in answers.items():
        canvas["answers"][question_id] = {
            "answer": answer,
            "notes": None,
            "timestamp": datetime.now().isoformat(),
        }
        title = section["questions"][question_id]["title"]
        saved.append(f"- **{question_id}**: {title} = {answer[:50]}{'...' if len(answer) > 50 else ''}")

    save_canvas(canvas)

    # Calculate progress
    total_questions = sum(len(s["questions"]) for s in sections.values())
    answered_count = len(canvas["answers"])
    required_total = sum(
        1 for s in sections.values() for q in s["questions"].values() if q["required"]
    )
    required_answered = sum(
        1 for s in sections.values()
        for qid, q in s["questions"].items()
        if q["required"] and qid in canvas["answers"]
    )

    return (
        f"Saved {len(answers)} answers for Section {section['number']}: {section['name']}\n\n"
        + "\n".join(saved)
        + f"\n\n**Progress:** {answered_count}/{total_questions} total | {required_answered}/{required_total} required"
    )


@tool(parse_docstring=True)
def get_canvas_progress() -> str:
    """Get the current progress of the AI Use Case Canvas.

    Use this to check completion status by section and identify
    which required questions still need answers.

    Returns:
        Progress summary with section-by-section breakdown.
    """
    sections = parse_canvas()
    canvas = load_canvas()
    answered = set(canvas.get("answers", {}).keys())

    result = "# Canvas Progress\n\n"
    result += f"**Use Case:** {canvas.get('use_case_name', 'Not started')}\n"
    result += f"**Started:** {canvas.get('created', 'Unknown')}\n"
    result += f"**Last Updated:** {canvas.get('updated', 'Not yet')}\n"
    result += f"**Status:** {canvas.get('status', 'in_progress')}\n\n"

    total_questions = 0
    total_answered = 0
    total_required = 0
    required_answered = 0

    result += "## Section Progress\n\n"
    result += "| Section | Total | Answered | Required | Req. Done |\n"
    result += "|---------|-------|----------|----------|----------|\n"

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

        result += f"| {section_id}: {section['name'][:20]} | {sect_total} | {sect_answered} | {sect_required} | {sect_req_answered} |\n"

    pct = 100 * total_answered // total_questions if total_questions else 0
    result += f"\n**Overall:** {total_answered}/{total_questions} ({pct}%)\n"
    result += f"**Required:** {required_answered}/{total_required} answered\n"

    # List unanswered required questions
    if required_answered < total_required:
        result += "\n### Unanswered Required Questions\n\n"
        for section_id, section in sections.items():
            for qid, q in section["questions"].items():
                if q["required"] and qid not in answered:
                    result += f"- **{qid}**: {q['title']} ({section['name']})\n"

    return result


@tool(parse_docstring=True)
def get_canvas_answers(section_filter: Optional[str] = None) -> str:
    """Get all answers that have been recorded on the canvas.

    Use this to review what the user has provided so far. Useful before
    generating the export or when user wants to review their responses.
    For progress/completion status, use get_canvas_progress instead.

    Args:
        section_filter: Optional section number to filter (e.g., '1', '2', ..., '9').

    Returns:
        All current answers organized by section.
    """
    sections = parse_canvas()
    canvas = load_canvas()
    answers = canvas.get("answers", {})

    if not answers:
        return "No answers have been recorded yet. Start by using `start_new_canvas` with your use case name."

    result = f"# Current Canvas: {canvas.get('use_case_name', 'Unnamed')}\n\n"

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
def assess_compliance_flags() -> str:
    """Assess compliance flags based on current canvas answers.

    Use this to summarize potential compliance concerns based on
    the Data Privacy, IT Security, and EU AI Act sections.

    Returns:
        Summary of compliance flags and recommendations.
    """
    canvas = load_canvas()
    answers = canvas.get("answers", {})

    result = "# Compliance Assessment Summary\n\n"
    result += f"**Use Case:** {canvas.get('use_case_name', 'Unnamed')}\n\n"

    flags = []
    recommendations = []

    # Data Privacy (Section 6)
    personal_data = answers.get("Q6.1", {}).get("answer", "")
    special_category = answers.get("Q6.2", {}).get("answer", "")
    dpia_required = answers.get("Q6.3", {}).get("answer", "")

    if "Yes" in personal_data or "Uncertain" in personal_data:
        flags.append("Personal data processing identified")
        recommendations.append("Ensure GDPR compliance measures are in place")

    if "Yes" in special_category:
        flags.append("Special category data (sensitive) processing")
        recommendations.append("Additional safeguards required for special category data")

    if "Yes" in dpia_required or "Uncertain" in dpia_required:
        flags.append("DPIA likely required")
        recommendations.append("Conduct Data Protection Impact Assessment before proceeding")

    # IT Security (Section 7)
    data_classification = answers.get("Q7.1", {}).get("answer", "")

    if "Confidential" in data_classification or "Strictly Confidential" in data_classification:
        flags.append(f"High data sensitivity: {data_classification}")
        recommendations.append("Enhanced security controls required")

    # EU AI Act (Section 8)
    ai_risk = answers.get("Q8.1", {}).get("answer", "")
    human_oversight = answers.get("Q8.2", {}).get("answer", "")

    if "High" in ai_risk:
        flags.append("EU AI Act HIGH RISK classification")
        recommendations.append("Comprehensive EU AI Act compliance review required")
        recommendations.append("Technical documentation and conformity assessment needed")

    if "Unacceptable" in ai_risk:
        flags.append("EU AI Act UNACCEPTABLE RISK - Prohibited use case")
        recommendations.append("STOP: This AI application may be prohibited under EU AI Act")

    if "Uncertain" in ai_risk:
        flags.append("EU AI Act classification uncertain")
        recommendations.append("Seek regulatory guidance on risk classification")

    if "Full Automation" in human_oversight and ("High" in ai_risk or "Uncertain" in ai_risk):
        flags.append("Full automation with elevated AI risk")
        recommendations.append("Consider adding human oversight mechanisms")

    # Build result
    result += "## Compliance Flags\n\n"
    if flags:
        for flag in flags:
            result += f"  {flag}\n"
    else:
        result += "No significant compliance flags identified.\n"

    result += "\n## Recommendations\n\n"
    if recommendations:
        for rec in recommendations:
            result += f"- {rec}\n"
    else:
        result += "- Continue with standard approval process\n"

    # Overall status
    result += "\n## Overall Compliance Status\n\n"
    if any("UNACCEPTABLE" in f for f in flags):
        result += "**HIGH CONCERN** - Potential prohibited use case. Legal review required.\n"
    elif any("HIGH RISK" in f for f in flags) or any("special category" in f.lower() for f in flags):
        result += "**ELEVATED CONCERN** - Additional compliance measures needed.\n"
    elif flags:
        result += "**MODERATE CONCERN** - Standard compliance review recommended.\n"
    else:
        result += "**LOW CONCERN** - Standard approval process should suffice.\n"

    return result


@tool(parse_docstring=True)
def generate_canvas_export(project_key: str = "AIUC") -> str:
    """Generate export files from the completed canvas.

    Creates both a human-readable markdown document and a Jira-importable
    JSON Epic structure. Requires all required questions to be answered.

    Args:
        project_key: Jira project key for the Epic (default: 'AIUC').

    Returns:
        Paths to generated files and export summary.
    """
    sections = parse_canvas()
    canvas = load_canvas()
    answers = canvas.get("answers", {})

    # Check required questions
    missing_required = []
    for section_id, section in sections.items():
        for qid, q in section["questions"].items():
            if q["required"] and qid not in answers:
                missing_required.append(f"{qid}: {q['title']}")

    if missing_required:
        return (
            "Cannot generate export - the following required questions are unanswered:\n\n"
            + "\n".join(f"- {q}" for q in missing_required)
            + "\n\nPlease answer all required questions before generating the export."
        )

    use_case_name = canvas.get("use_case_name", "Unnamed AI Use Case")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # === Generate Markdown Export ===
    md_export = f"""# AI Use Case Canvas: {use_case_name}

**Generated:** {timestamp}
**Status:** Complete

---

"""

    for section_id, section in sections.items():
        md_export += f"## {section['name']}\n\n"

        for qid, q in section["questions"].items():
            answer_data = answers.get(qid, {})
            answer = answer_data.get("answer", "*Not answered*")
            notes = answer_data.get("notes")

            md_export += f"### {q['title']}\n\n"
            md_export += f"**{answer}**\n\n"

            if notes:
                md_export += f"*Notes: {notes}*\n\n"

        md_export += "---\n\n"

    # Add compliance summary
    compliance_flags = []
    if answers.get("Q6.1", {}).get("answer", "") in ["Yes", "Uncertain"]:
        compliance_flags.append("Personal data involved")
    if answers.get("Q6.2", {}).get("answer", "") == "Yes":
        compliance_flags.append("Special category data")
    if answers.get("Q8.1", {}).get("answer", "") in ["High", "Unacceptable"]:
        compliance_flags.append(f"EU AI Act: {answers.get('Q8.1', {}).get('answer', '')}")

    md_export += "## Compliance Flags\n\n"
    if compliance_flags:
        for flag in compliance_flags:
            md_export += f"- {flag}\n"
    else:
        md_export += "No significant compliance flags.\n"

    md_export += "\n---\n*Generated by AI Ideation Agent*\n"

    # === Generate Jira Epic JSON ===
    # Build description in Jira markup format
    jira_description = f"h2. Problem Statement\n{answers.get('Q2.1', {}).get('answer', 'N/A')}\n\n"
    jira_description += f"h2. Goal\n{answers.get('Q2.2', {}).get('answer', 'N/A')}\n\n"
    jira_description += f"h2. Success Metrics\n{answers.get('Q2.3', {}).get('answer', 'N/A')}\n\n"

    jira_description += "h2. Stakeholders\n"
    jira_description += f"* *Problem Owner:* {answers.get('Q1.1', {}).get('answer', 'N/A')}\n"
    jira_description += f"* *Budget Owner:* {answers.get('Q1.2', {}).get('answer', 'N/A')}\n"
    jira_description += f"* *Technical Owner:* {answers.get('Q1.3', {}).get('answer', 'N/A')}\n"
    jira_description += f"* *Executive Sponsor:* {answers.get('Q1.4', {}).get('answer', 'N/A')}\n\n"

    jira_description += "h2. Value Proposition\n"
    jira_description += f"* *Type:* {answers.get('Q3.1', {}).get('answer', 'N/A')}\n"
    jira_description += f"* *Qualitative:* {answers.get('Q3.2', {}).get('answer', 'N/A')}\n"
    jira_description += f"* *Quantitative:* {answers.get('Q3.3', {}).get('answer', 'N/A')}\n"
    jira_description += f"* *Time to Value:* {answers.get('Q3.4', {}).get('answer', 'N/A')}\n\n"

    jira_description += "h2. Classification\n"
    jira_description += f"* *AI Type:* {answers.get('Q4.1', {}).get('answer', 'N/A')}\n"
    jira_description += f"* *Business Unit:* {answers.get('Q4.2', {}).get('answer', 'N/A')}\n"
    jira_description += f"* *Innovation Category:* {answers.get('Q4.4', {}).get('answer', 'N/A')}\n\n"

    jira_description += "h2. Data Requirements\n"
    jira_description += f"* *Sources:* {answers.get('Q5.1', {}).get('answer', 'N/A')}\n"
    jira_description += f"* *Data Types:* {answers.get('Q5.2', {}).get('answer', 'N/A')}\n"
    jira_description += f"* *Volume:* {answers.get('Q5.4', {}).get('answer', 'N/A')}\n\n"

    jira_description += "h2. Compliance\n"
    jira_description += f"* *Personal Data:* {answers.get('Q6.1', {}).get('answer', 'N/A')}\n"
    jira_description += f"* *Data Classification:* {answers.get('Q7.1', {}).get('answer', 'N/A')}\n"
    jira_description += f"* *EU AI Act Risk:* {answers.get('Q8.1', {}).get('answer', 'N/A')}\n"
    jira_description += f"* *Human Oversight:* {answers.get('Q8.2', {}).get('answer', 'N/A')}\n\n"

    jira_description += "h2. Next Steps\n"
    jira_description += f"{answers.get('Q9.3', {}).get('answer', 'N/A')}\n\n"

    jira_description += "h2. Key Risks\n"
    jira_description += f"{answers.get('Q9.1', {}).get('answer', 'N/A')}\n"

    # Build labels
    labels = ["ai-use-case"]
    idea_type = answers.get("Q4.1", {}).get("answer", "").lower().replace(" ", "-")
    if idea_type:
        labels.append(idea_type)
    business_unit = answers.get("Q4.2", {}).get("answer", "").lower().replace(" ", "-")[:20]
    if business_unit:
        labels.append(business_unit)
    innovation = answers.get("Q4.4", {}).get("answer", "").lower()
    if innovation:
        labels.append(innovation)

    jira_epic = {
        "fields": {
            "project": {"key": project_key},
            "issuetype": {"name": "Epic"},
            "summary": f"AI Use Case: {use_case_name}",
            "description": jira_description,
            "labels": labels,
        },
        "canvas_metadata": {
            "generated": timestamp,
            "use_case_name": use_case_name,
            "total_questions_answered": len(answers),
            "compliance_flags": compliance_flags,
        },
    }

    # === Save files ===
    safe_name = re.sub(r"[^\w\s-]", "", use_case_name.lower())
    safe_name = re.sub(r"[\s-]+", "_", safe_name)[:50]
    date_suffix = datetime.now().strftime("%Y%m%d")

    md_filename = f"canvas_{safe_name}_{date_suffix}.md"
    json_filename = f"jira_epic_{safe_name}_{date_suffix}.json"

    md_path = OUTPUT_DIR / md_filename
    json_path = OUTPUT_DIR / json_filename

    md_path.write_text(md_export)
    json_path.write_text(json.dumps(jira_epic, indent=2))

    # Update canvas status
    canvas["status"] = "completed"
    canvas["export_files"] = {
        "markdown": md_filename,
        "jira_json": json_filename,
    }
    save_canvas(canvas)

    return (
        f"Canvas export generated successfully!\n\n"
        f"**Use Case:** {use_case_name}\n\n"
        f"**Files Created:**\n"
        f"- Markdown: `{md_path}`\n"
        f"- Jira Epic JSON: `{json_path}`\n\n"
        f"**Compliance Flags:** {len(compliance_flags)}\n"
        f"**Questions Answered:** {len(answers)}\n\n"
        f"The Jira JSON can be imported using Jira's REST API or bulk import tools."
    )
