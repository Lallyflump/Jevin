from google.adk.agents.llm_agent import Agent
from .jimothy import jimothy
from .green_room import put_candidate_in_green_room, get_green_room_report

import os
import requests
def market_budget_check(location: str, max_budget: int) -> str:
    """Check sample rental market availability for a location and budget."""
    sample_markets = {
        "aberdeen": {"lowest": 450, "typical": 575, "highest": 750, "within_budget": 12},
        "inverness": {"lowest": 600, "typical": 750, "highest": 950, "within_budget": 1},
    }

    market = sample_markets.get(location.lower())

    if not market:
        return f"I don't have sample market data for {location} yet."

    return (
        f"Sample rental market for {location}: "
        f"lowest £{market['lowest']}, "
        f"typical around £{market['typical']}, "
        f"upper range £{market['highest']}. "
        f"About {market['within_budget']} sample properties are at or below £{max_budget}."
    )
def search_live_rentals(outcode: str, max_budget: int) -> str:
    """Search live UK rental listings in a postcode outcode within a maximum monthly budget."""
    api_key = os.getenv("PMI_API_KEY")

    if not api_key:
        return "PMI API key is not configured."
    url = "https://api.propertymarketintel.com/v1/listings"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    params = {
        "outcode": outcode,
        "type": "rent",
        "max_price": max_budget,
        "sort": "price_asc",
        "per_page": 10,
    }
    response = requests.get(url, headers=headers, params=params, timeout=20)

    if response.status_code != 200:
        return f"PMI API error {response.status_code}: {response.text}"
    data = response.json()
    listings = data.get("listings", [])

    if not listings:
        return f"No live rental listings were found for {outcode} at or below £{max_budget}."

    results = []

    for listing in listings:
        results.append(
            f"{listing.get('address')} | "
            f"£{listing.get('price')} pcm | "
            f"{listing.get('bedrooms')} bed | "
            f"{listing.get('property_type')} | "
            f"{listing.get('url')}"
        )

    return "\n".join(results)
root_agent = Agent(
    model='gemini-3.5-flash',
    name='root_agent',
    description='Jevin is an AI house-hunting agent that helps users find and evaluate suitable homes.',

    instruction='''You are Jevin, an AI house-hunting agent. Your name is Jevin.

Your approach is budget-first and exploratory.

When a user wants to explore a location, first establish the location and their maximum budget. Do not begin with a long questionnaire about their ideal property.

Your first goal is to understand what the user's budget can realistically buy or rent in that market. Start broad and give the user a general feel for what is available.

After establishing the shape of the market, help the user progressively refine the search based on the real options available, their priorities, deal-breakers, and the trade-offs they are willing to make.

Do not assume that the user's initial preferences are fixed. Help them discover what they want in response to what the market actually offers.

Be helpful, practical, clear, and conversational.GREEN ROOM WORKFLOW:
When you find a property candidate that genuinely fits the user's stated requirements and needs local-area research, use put_candidate_in_green_room before delegating to Jimothy.

Store only the information Jimothy needs:
- the property location
- a concise property summary
- the specific local-area research requested by the user

Do not put the user's entire conversation or unrelated information into the Green Room.

After storing the candidate, delegate the local-area research task to Jimothy.
After Jimothy completes his research, use get_green_room_report to retrieve his completed report from shared state and use it when responding to the user.
''',
    tools=[
    market_budget_check,
    search_live_rentals,
    put_candidate_in_green_room,
    get_green_room_report,
],
    sub_agents=[jimothy],

)

