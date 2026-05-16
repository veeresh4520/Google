from google.adk.agents import Agent
from google.adk.toolsets import McpToolset

# Define the ADK Agent for GitHub Dev Card Generation
github_card_agent = Agent(
    name="github_card_agent",
    model="gemini-2.0-flash",  # Gemini 2.5 Flash (represented as 2.0-flash in some SDK versions)
    instruction=(
        "You are a GitHub profile analyst and dev card generator. "
        "When a user gives you a GitHub username, you ALWAYS follow this exact sequence: "
        "1. Call scrape_github with the username.\n"
        "2. Call analyze_profile with the result from scrape_github.\n"
        "3. Call generate_card_html with the username, github_data, and analysis results.\n"
        "4. Call save_card with the username and the generated HTML.\n\n"
        "Never skip steps. Be enthusiastic about developers' work. "
        "If the profile is private or doesn't exist, say so clearly."
    ),
    toolsets=[
        McpToolset(command="python", args=["mcp_server.py"])
    ]
)
