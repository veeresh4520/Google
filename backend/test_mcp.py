import asyncio
import os
import json
from mcp_server import scrape_github, analyze_profile, generate_card_html

async def test_end_to_end():
    username = "torvalds"
    print(f"--- Testing end-to-end for user: {username} ---")
    
    try:
        # 1. Scrape GitHub
        print("1. Calling scrape_github...")
        github_data = await scrape_github(username)
        print("   [Success] Data fetched.")
        
        # 2. Analyze Profile
        print("2. Calling analyze_profile...")
        analysis = await analyze_profile(github_data)
        print("   [Success] Analysis completed.")
        
        # 3. Generate Card HTML
        print("3. Calling generate_card_html...")
        html = await generate_card_html(username, github_data, analysis)
        print("   [Success] HTML generated.")
        
        # 4. Print Results
        print("\n--- Analysis Results ---")
        print(f"Card Theme: {analysis.get('card_theme')}")
        print(f"Developer Vibe: {analysis.get('developer_vibe')}")
        
    except Exception as e:
        print(f"\n[Error] Tool failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
