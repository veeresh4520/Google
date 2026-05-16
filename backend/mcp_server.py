import httpx
import json
import os
from datetime import datetime
from fastmcp import FastMCP
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

mcp = FastMCP("GitHub Toolset")

# Initialize Gemini Client for internal analysis tool
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@mcp.tool()
async def scrape_github(username: str) -> dict:
    """Fetches public profile data, top repos, and aggregated languages for a GitHub user."""
    headers = {}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    async with httpx.AsyncClient(headers=headers) as client:
        # Fetch User Profile
        user_res = await client.get(f"https://api.github.com/users/{username}")
        user_res.raise_for_status()
        user_data = user_res.json()

        # Fetch Repos (sorted by stars)
        repos_res = await client.get(f"https://api.github.com/users/{username}/repos?sort=stargazers_count&per_page=30")
        repos_res.raise_for_status()
        repos_data = repos_res.json()

        # Extract Top 6 Repos
        top_6_repos = []
        languages = {}
        for r in repos_data:
            if len(top_6_repos) < 6:
                top_6_repos.append({
                    "name": r["name"],
                    "stars": r["stargazers_count"],
                    "language": r["language"],
                    "description": r["description"]
                })
            
            if r["language"]:
                languages[r["language"]] = languages.get(r["language"], 0) + 1

        # Sort languages by usage
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        most_used_languages = [l[0] for l in sorted_langs[:5]]

        return {
            "name": user_data.get("name") or username,
            "avatar_url": user_data.get("avatar_url"),
            "bio": user_data.get("bio"),
            "location": user_data.get("location"),
            "public_repos": user_data.get("public_repos"),
            "followers": user_data.get("followers"),
            "top_6_repos": top_6_repos,
            "most_used_languages": most_used_languages
        }

@mcp.tool()
async def analyze_profile(github_data: dict) -> dict:
    """Uses Gemini 2.5 Flash to analyze the developer's vibe, skills, and fun facts."""
    prompt = f"""
    Analyze this GitHub developer data and return a JSON object.
    Data: {json.dumps(github_data)}
    
    Required JSON structure:
    {{
        "developer_vibe": "one sentence personality description",
        "top_skills": ["skill1", "skill2", "skill3"],
        "fun_fact": "something clever inferred from their repos or bio",
        "card_theme": "one of: hacker, builder, researcher, designer, open-source-hero"
    }}
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash", # Assuming user meant 2.0/2.5 flash
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    return json.loads(response.text)

@mcp.tool()
async def generate_card_html(username: str, github_data: dict, analysis: dict) -> str:
    """Generates a self-contained, beautiful HTML string for the dev card."""
    theme = analysis.get("card_theme", "builder")
    themes = {
        "hacker": "bg-black text-green-500 font-mono border-green-500",
        "builder": "bg-slate-100 text-slate-900 border-blue-500",
        "researcher": "bg-indigo-900 text-white border-purple-400",
        "designer": "bg-pink-50 text-pink-900 border-pink-400",
        "open-source-hero": "bg-orange-500 text-white border-white"
    }
    theme_class = themes.get(theme, themes["builder"])

    repos_html = "".join([
        f'<div class="mb-2 p-2 border-b border-opacity-20"><strong>{r["name"]}</strong> ({r["stars"]} ⭐) - {r["language"]}</div>'
        for r in github_data["top_6_repos"][:3]
    ])

    skills_html = "".join([
        f'<span class="px-2 py-1 m-1 text-xs rounded-full border border-opacity-50">{s}</span>'
        for s in analysis["top_skills"]
    ])

    html = f"""
    <div class="max-w-md mx-auto p-6 rounded-2xl border-4 shadow-2xl {theme_class}">
        <div class="flex items-center gap-4 mb-4">
            <img src="{github_data['avatar_url']}" class="w-20 h-20 rounded-full border-2" />
            <div>
                <h2 class="text-2xl font-bold">{github_data['name']}</h2>
                <p class="text-sm opacity-80">@{username}</p>
            </div>
        </div>
        <p class="italic mb-4">"{analysis['developer_vibe']}"</p>
        <div class="flex flex-wrap mb-4">{skills_html}</div>
        <div class="grid grid-cols-2 gap-2 mb-4 text-center text-sm">
            <div class="p-2 bg-white bg-opacity-10 rounded">Repos: {github_data['public_repos']}</div>
            <div class="p-2 bg-white bg-opacity-10 rounded">Followers: {github_data['followers']}</div>
        </div>
        <div class="text-sm">
            <h3 class="font-bold mb-2 uppercase">Top Projects</h3>
            {repos_html}
        </div>
        <p class="mt-4 text-xs opacity-60">💡 {analysis['fun_fact']}</p>
    </div>
    """
    return html

@mcp.tool()
async def save_card(username: str, html: str) -> str:
    """Saves the generated HTML card to the static directory."""
    static_dir = os.path.join(os.getcwd(), "static", "cards")
    os.makedirs(static_dir, exist_ok=True)
    
    file_path = os.path.join(static_dir, f"{username}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return f"/static/cards/{username}.html"

if __name__ == "__main__":
    mcp.run()
