# 🏗️ Discord Architect Bot

An advanced, AI-powered Discord bot that designs and builds server structures based on natural language descriptions.

## ✨ Features

- **AI-Powered Design**: Uses advanced LLMs (Google Gemini, Groq, OpenRouter) to generate server blueprints.
- **Natural Language Input**: Just describe what you want (e.g., "A chill gaming server with a retro vibe").
- **Aesthetic & Themed**: Automatically applies premium fonts, kaomojis, and emojis to channel names.
- **Intelligent Building**: Creates categories, channels, and roles with proper permissions.
- **Smart Updates**: Modifies existing servers without destroying everything (unless requested).
- **Robust Fallback**: Automatically switches between AI providers if rate limits or errors occur.
- **Backup & Restore**: Save server states and restore them later.

## 🚀 Installation

### Prerequisites

- Python 3.9+
- A Discord Bot Token (with Administrator permissions)
- API Keys for:
    - Google Gemini (Primary)
    - Groq (Secondary)
    - OpenRouter (Tertiary)

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/discord-architect-bot.git
    cd discord-architect-bot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment:**
    Create a `.env` file in the root directory and add your keys:
    ```env
    DISCORD_TOKEN=your_discord_bot_token
    DISCORD_APP_ID=your_app_id
    GROQ_API_KEY=your_groq_key
    # Google and OpenRouter keys are currently configured in utils/ai.py, 
    # but you can move them here for better security.
    ```

4.  **Run the bot:**
    ```bash
    ./run.sh
    ```

## 🛠️ Usage

### Commands

- **/architect [description] [style]**: Generate a new server structure.
    - `style`: Standard, Minimal, Professional, or Aesthetic.
- **/preview**: View the generated blueprint before building.
- **/modify [changes]**: Request changes to the blueprint (e.g., "Add a music channel").
- **/build**: Apply the blueprint to your server.
- **/backup [name]**: Create a backup of your current server layout.
- **/clean_slate**: **WARNING** Deletes all channels and roles to start fresh.
- **/ping**: Check bot latency.
- **/info**: View bot information.
- **/help**: List all commands.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
