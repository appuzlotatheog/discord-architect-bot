import os
import json
import asyncio
from groq import AsyncGroq

client = AsyncGroq(api_key=os.getenv('GROQ_API_KEY'))

SYSTEM_PROMPT = """
You are a Discord Server Architect. Your goal is to design a Discord server structure based on the user's request.
Output a JSON object with the following structure:
{
    "server_name": "Name of the server",
    "description": "Brief description of the server theme",
    "delete_unused": true/false,  // Set to true if the user wants a complete overhaul or concept change. This will DELETE existing channels not in the blueprint.
    "roles": [
        {
            "name": "Role Name", 
            "color": "hex_code (e.g. #FF0000)", 
            "permissions": ["administrator", "manage_messages", "kick_members", "ban_members", "read_messages", "send_messages", "connect", "speak"],
            "hoist": true/false,
            "mentionable": true/false
        }
    ],
    "categories": [
        {
            "name": "Category Name",
            "permissions": [
                {"role": "Role Name", "allow": ["read_messages"], "deny": ["send_messages"]}
            ],
            "channels": [
                {
                    "name": "channel-name", 
                    "type": "text|voice|stage|forum", 
                    "description": "topic",
                    "permissions": [
                        {"role": "Role Name", "allow": ["read_messages"], "deny": ["send_messages"]}
                    ]
                }
            ]
        }
    ]
}
Ensure the JSON is valid. Do not include markdown formatting like ```json.
Use standard Discord permission names.

STYLE INSTRUCTIONS:
- **DEFAULT BEHAVIOR**: Unless the user explicitly requests "Minimal" or "Professional", you MUST design the server to be **Themed and Aesthetic**.
- **AESTHETIC/THEMED**: Use Unicode fonts (e.g., 𝓒𝓸𝓸𝓵 𝓣𝓮𝔁𝓽, ꜱᴍᴀʟʟ ᴄᴀᴘꜱ), Kaomojis, and relevant Emojis for ALL category and channel names. Make it look premium and unique.
    - **Examples**:
        - `✧ welcome-lounge ✧`
        - `₊˚⊹︰announcements`
        - `☕・chill-zone`
        - `🎨・art-gallery`
        - `🎮・gaming-lobby`
        - `🎤・general-vc`
        - `🌙﹒night-owls`
- **MINIMAL/PROFESSIONAL**: Only use clean, standard text if the user explicitly asks for "Minimal", "Clean", or "Professional" styles.
- Always include a comprehensive list of roles suitable for the server type, also using fonts/emojis if the server style is aesthetic.
"""

import asyncio

# ... imports ...

# ... SYSTEM_PROMPT ...

from google import genai

# Configure Google API
GOOGLE_API_KEY = "AIzaSyA24oN9iWpCvAYEOvFwhl_nENOfi8Hvl_w"
google_client = genai.Client(api_key=GOOGLE_API_KEY)

async def generate_with_google(prompt):
    try:
        response = await google_client.aio.models.generate_content(
            model='gemini-2.5-flash-lite', 
            contents=prompt
        )
        content = response.text
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Google API Error: {e}")
        raise e

import aiohttp

# Configure OpenRouter
OPENROUTER_KEY = "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"

async def generate_with_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_KEY}",
    }
    payload = {
        "model": "kwaipilot/kat-coder-pro:free",
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status != 200:
                text = await response.text()
                raise Exception(f"OpenRouter Error: {response.status} - {text}")
            
            data = await response.json()
            content = data['choices'][0]['message']['content']
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)

async def generate_blueprint(description: str, style: str = "standard", history: list = None, current_structure: dict = None, status_callback=None):
    history_text = json.dumps(history, indent=2) if history else "No previous history."
    structure_text = json.dumps(current_structure, indent=2) if current_structure else "New server (empty)."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"""
Current Server Structure:
{structure_text}

Previous Conversation History:
{history_text}

User Request: {description}
Style: {style}

Generate a JSON blueprint for the requested changes.
"""}
    ]

    # 1. Try Google Gemini (Primary)
    try:
        return await generate_with_google(prompt)
        # For Google Gemini, we need to pass the user content directly, not the full messages array
        google_prompt_content = messages[1]["content"] # Extracting the user message content
        return await generate_with_google(google_prompt_content)
    except Exception as google_e:
        print(f"Google API Error: {google_e}. Switching to Groq...")
        if status_callback:
            await status_callback("⚠️ Google API Error. Switching to Groq...")

        # 2. Try Groq (Secondary)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                completion = await client.chat.completions.create(
                    model="groq/compound",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=4096,
                    top_p=1,
                    stream=False,
                    stop=None,
                )
                content = completion.choices[0].message.content
                content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(content)
            except Exception as groq_e:
                if "429" in str(groq_e):
                    print(f"Groq Rate Limit (429).")
                    if status_callback:
                        await status_callback("⚠️ Groq Rate Limit...")
                    # Break to fallback immediately on rate limit if we want, or retry? 
                    # Let's retry a bit for 429s as before, but if it fails, go to OpenRouter.
                    if attempt < max_retries - 1:
                        wait_time = 5 * (attempt + 1)
                        if status_callback:
                            await status_callback(f"⚠️ Groq Rate Limit. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        # Fallback to OpenRouter
                        break
                elif attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    if status_callback:
                        await status_callback(f"⚠️ Groq Error. Retrying in {wait_time}s...")
                    print(f"Groq Error: {groq_e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    break
        
        # 3. Try OpenRouter (Tertiary)
        print("Switching to OpenRouter fallback...")
        if status_callback:
            await status_callback("⚠️ Groq failed. Switching to OpenRouter (kwaipilot/kat-coder-pro:free)...")
        
        # For OpenRouter, we need to pass the user content directly, not the full messages array
        openrouter_prompt_content = messages[1]["content"] # Extracting the user message content
        return await generate_with_openrouter(openrouter_prompt_content)

async def modify_blueprint(current_blueprint, modification_request, status_callback=None):
    # 1. Try Google Gemini (Primary)
    prompt = f"{SYSTEM_PROMPT}\n\nYou are modifying an existing blueprint.\nCurrent Blueprint: {json.dumps(current_blueprint)}\nModification Request: {modification_request}"
    try:
        return await generate_with_google(prompt)
    except Exception as google_e:
        print(f"Google API Error: {google_e}. Switching to Groq...")
        if status_callback:
            await status_callback("⚠️ Google API Error. Switching to Groq...")

        # 2. Try Groq (Secondary)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                completion = await client.chat.completions.create(
                    model="groq/compound",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT + "\nYou are modifying an existing blueprint based on user feedback. Return the updated JSON."},
                        {"role": "user", "content": f"Current Blueprint: {json.dumps(current_blueprint)}\n\nModification Request: {modification_request}"}
                    ],
                    temperature=0.7,
                    max_tokens=4096,
                    top_p=1,
                    stream=False,
                    stop=None,
                )
                content = completion.choices[0].message.content
                content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(content)
            except Exception as groq_e:
                if "429" in str(groq_e):
                    if status_callback:
                        await status_callback("⚠️ Groq Rate Limit...")
                    if attempt < max_retries - 1:
                        wait_time = 5 * (attempt + 1)
                        if status_callback:
                            await status_callback(f"⚠️ Groq Rate Limit. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        break
                elif attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    if status_callback:
                        await status_callback(f"⚠️ Groq Error. Retrying in {wait_time}s...")
                    print(f"Groq Error: {groq_e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    break
        
        # 3. Try OpenRouter (Tertiary)
        if status_callback:
            await status_callback("⚠️ Groq failed. Switching to OpenRouter (kwaipilot/kat-coder-pro:free)...")
        return await generate_with_openrouter(prompt)
