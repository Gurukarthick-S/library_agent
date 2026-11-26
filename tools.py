"""Tools the agent may call. Rules: read, compute or draft ONLY.
No tool may send, delete or pay anything."""
from datetime import date, datetime, timedelta

from langchain_core.tools import tool

from rag_core import clip


@tool
def today() -> str:
    """Return today's date as YYYY-MM-DD. Use when a question depends on the current date."""
    return date.today().isoformat()


@tool
def add_days(start_date: str, days: int) -> str:
    """Add a number of days to a date written as YYYY-MM-DD and return the new date (YYYY-MM-DD).
    Use for due dates, deadlines and other date arithmetic."""
    try:
        start = datetime.strptime(start_date.strip(), "%Y-%m-%d").date()
    except ValueError:
        return "Please give the date in YYYY-MM-DD format, for example 2026-11-03."
    return (start + timedelta(days=int(days))).isoformat()


# ---------------------------------------------------------------------------
# TODO: write YOUR TWO tools below (the two above are only samples and do not
# count). Each one: a clear name, a one-sentence docstring, simple typed inputs,
# a short string result (use clip), a helpful message for bad input.
# Example for this library topic:
#
# @tool
# def fine_due(days_late: int, books: int) -> str:
#     """Calculate the library fine in rupees for late books. Use when a user asks what fine they owe."""
#     if days_late < 0 or books < 1:
#         return "days_late must be 0 or more and books must be at least 1."
#     per_book = min(2 * days_late, 200)
#     return f"Fine: Rs {per_book * books} ({books} book(s), {days_late} day(s) late)."
# ---------------------------------------------------------------------------

TOOLS = [today, add_days]  # add your two tools to this list
