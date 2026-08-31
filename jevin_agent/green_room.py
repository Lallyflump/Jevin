from google.adk.tools.tool_context import ToolContext


def put_candidate_in_green_room(
    location: str,
    property_summary: str,
    research_request: str,
    tool_context: ToolContext,
) -> str:
    """Stores a property candidate and research request in shared session state."""

    tool_context.state["green_room_candidate"] = {
        "location": location,
        "property_summary": property_summary,
        "research_request": research_request,
    }

    tool_context.state["green_room_status"] = "awaiting_area_research"

    return f"Candidate stored in Green Room for {location}."


def get_green_room_candidate(tool_context: ToolContext) -> dict:
    """Returns the current property candidate from shared session state."""

    return tool_context.state.get("green_room_candidate", {})


def put_area_report_in_green_room(
    report: str,
    tool_context: ToolContext,
) -> str:
    """Stores Jimothy's completed local-area report in shared session state."""

    tool_context.state["green_room_jimothy_report"] = report
    tool_context.state["green_room_status"] = "area_research_complete"

    return "Jimothy's area report has been stored in the Green Room."


def get_green_room_report(tool_context: ToolContext) -> str:
    """Returns Jimothy's completed report from shared session state."""

    return tool_context.state.get("green_room_jimothy_report", "")
