# Discord Architect Bot

An advanced Discord bot that designs and builds server structures based on natural language descriptions, powered by multiple AI providers.

## What It Does

Discord Architect Bot takes your plain English descriptions and transforms them into complete Discord server layouts. Instead of manually creating dozens of channels, categories, and roles, you simply describe what you want and let the bot handle the technical work.

The bot uses state-of-the-art language models (Google Gemini, Groq, and OpenRouter) to understand your vision and translate it into a functional server structure. It applies thoughtful styling with custom fonts, kaomojis, and emojis to give your server personality while maintaining clean organization.

## Key Features

**Natural Language Processing** - Describe your ideal server in plain English. Something like "A chill gaming server with a retro vibe" is all you need.

**Intelligent Design System** - The bot doesn't just copy templates. It generates unique layouts based on your specific requirements, complete with appropriate permissions and role hierarchies.

**Smart Updates** - When modifying an existing server, the bot intelligently updates what needs changing without destroying your existing setup (unless you specifically request a clean slate).

**Multi-Provider Fallback** - Built-in redundancy across three AI providers means the bot keeps working even if one service experiences downtime or rate limits.

**Backup and Restore** - Save snapshots of your server configuration and restore them whenever needed.

**Style Customization** - Choose from different aesthetic approaches: Standard, Minimal, Professional, or Aesthetic, each with its own design philosophy.

## Getting Started

### What You'll Need

- Python 3.9 or higher
- A Discord bot token with Administrator permissions
- API keys for at least one of these services:
  - Google Gemini (recommended as primary)
  - Groq (good backup option)
  - OpenRouter (tertiary fallback)

### Installation Steps

First, clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/discord-architect-bot.git
cd discord-architect-bot
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the root directory and add your credentials:

```env
DISCORD_TOKEN=your_discord_bot_token
DISCORD_APP_ID=your_app_id
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_google_api_key
OPENROUTER_API_KEY=your_openrouter_key
```

Run the bot:

```bash
./run.sh
```

## How to Use

### Basic Workflow

The typical flow involves three steps: generate a design, preview it, and then build it.

1. Use `/architect` with a description to generate a server blueprint
2. Use `/preview` to review what will be created
3. Use `/build` to apply the changes to your server

### Available Commands

**/architect [description] [style]**
Generates a new server structure based on your description. The style parameter is optional and accepts: Standard, Minimal, Professional, or Aesthetic.

Example: `/architect A community for indie game developers with separate spaces for different game engines`

**/preview**
Shows you the complete blueprint that was generated, including all categories, channels, and roles that will be created.

**/modify [changes]**
Request adjustments to the current blueprint without starting over.

Example: `/modify Add a music bot channel and remove the memes category`

**/build**
Applies the current blueprint to your Discord server. This actually creates the channels, categories, and roles.

**/backup [name]**
Creates a snapshot of your current server structure that you can restore later.

**/clean_slate**
Warning: This command deletes all existing channels and roles to give you a completely fresh start. Use with caution.

**/ping**
Quick health check that shows the bot's response time.

**/info**
Displays information about the bot, including version and active AI provider.

**/help**
Lists all available commands with brief descriptions.

## Contributing

Contributions are welcome and appreciated. If you'd like to improve the bot, feel free to fork the repository and submit a pull request. Whether it's bug fixes, new features, or documentation improvements, all contributions help make this project better.

## A Few Notes

This bot requires administrator permissions to function properly since it needs to create and manage channels, categories, and roles. Always test new configurations in a development server before applying them to your main community.

The AI-generated designs are creative starting points, but you'll likely want to refine them based on your community's specific needs. The `/modify` command makes this iterative process straightforward.
