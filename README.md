# 🚦 DriveWise

An intelligent WhatsApp chatbot for learning French road signs, powered by AI. DriveWise helps users master the French driving code through interactive quizzes, sign recognition, and personalized learning experiences.

## ✨ Features

- **📚 Learn Road Signs**: Browse and learn about French road signs with detailed descriptions, rules, and typical locations
- **🧠 AI-Powered Quizzes**: Generate personalized multiple-choice questions based on your learning history
- **🎯 Adaptive Learning**: Smart algorithm tracks viewed signs and adjusts difficulty based on your progress
- **📸 Sign Recognition**: Upload images to identify road signs using AI vision
- **💾 Progress Tracking**: SQLite database stores your quiz history and learning progress
- **🌐 RESTful API**: FastAPI-based endpoints for easy integration

## 🏗️ Architecture

- **Backend**: FastAPI (Python)
- **Database**: SQLite with async support (aiosqlite)
- **AI**: [Pydantic AI](https://ai.pydantic.dev/) with support for multiple LLM providers (default: Groq GPT-OSS-120B)
- **Data**: Comprehensive road sign database with 119+ French road signs

## 📋 Prerequisites

- Python 3.11+
- API KEY from your LLM provider

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/DriveWise.git
cd DriveWise
```

### 2. Install Dependencies

**For Groq (default):**
```bash
uv venv
uv pip install -r requirements.txt
```

**For other LLM providers:**

DriveWise uses [Pydantic AI](https://ai.pydantic.dev/) which supports multiple LLM providers. To use a different provider, install the slim version with the appropriate extras:

```bash
uv venv
uv pip install fastapi[standard] aiosqlite pydantic
uv pip install "pydantic-ai-slim[your-provider]"
```

Supported providers include:
- `groq` - Groq API (default, already in requirements.txt)
- `openai` - OpenAI API
- `anthropic` - Anthropic Claude API
- `google` - Google Gemini API
- `mistral` - Mistral AI API
- `cohere` - Cohere API
- And more...

See the [Pydantic AI installation guide](https://ai.pydantic.dev/install/#slim-install) for the complete list of supported providers and installation instructions.

**Example for OpenAI:**
```bash
uv pip install "pydantic-ai-slim[openai]"
```

**Example for multiple providers:**
```bash
uv pip install "pydantic-ai-slim[openai,anthropic,logfire]"
```

This will:
- Create a virtual environment
- Install all project dependencies
- Set up the project for development

### 3. Configure Environment Variables

Create a `.env` file from the template:

```bash
cp env_template .env
```

Edit `.env` and add your API key based on your provider:

**For Groq (default):**
```env
GROQ_API_KEY=your_groq_api_key_here
```

**For other providers:**
- OpenAI: `OPENAI_API_KEY=your_key_here`
- Anthropic: `ANTHROPIC_API_KEY=your_key_here`
- Google: `GOOGLE_API_KEY=your_key_here`
- Mistral: `MISTRAL_API_KEY=your_key_here`

Get your API key from your provider's console/dashboard.

### 4. Update Agent Configuration

If using a provider other than Groq, update the agent model in `src/modules/agent/__init__.py`:

```python
# For OpenAI
agent = Agent("openai:gpt-4", deps_type=AgentDeps)

# For Anthropic
agent = Agent("anthropic:claude-3-opus-20240229", deps_type=AgentDeps)

# For Google
agent = Agent("google:gemini-pro", deps_type=AgentDeps)
```

See [Pydantic AI Models documentation](https://ai.pydantic.dev/models/) for available models.

### 5. Initialize the Database

The database will be automatically created on first run. The schema is defined in `src/db.sql`.

### 6. Run the Application

```bash
fastapi dev src.main
```

The API will be available at `http://localhost:8000`

You can also access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📖 API Endpoints

### `GET /sign-quizz`
Generate a road sign quiz based on viewed signs.

**Parameters:**
- `phone` (required): User phone number identifier
- `level` (optional): Difficulty level (1-5), default: "2"

**Response:**
```json
{
  "text": "Question text with options...",
  "buttons": [
    {"id": "0", "label": "Option 1", "description": "..."},
    ...
  ],
  "answer": "0",
  "explanation": "Explanation of the correct answer"
}
```

### `GET /general-quizz`
Generate a general driving code quiz.

**Parameters:**
- `phone` (required): User phone number identifier
- `level` (optional): Difficulty level (1-5), default: "2"

**Response:** Same format as `/sign-quizz`

### `GET /learn-sign`
Get a random road sign to learn (prioritizes unseen signs).

**Parameters:**
- `phone` (required): User phone number identifier

**Response:**
```json
{
  "text": "Formatted sign information...",
  "image": "https://wims.math.cnrs.fr/wims/modules/data/images/roadsigns.fr/images/png100/A0.png"
}
```

## 🗂️ Project Structure

```
DriveWise/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── db.sql               # Database schema
│   ├── data.json            # Road signs database (119+ signs)
│   ├── utils.py             # Utility functions
│   └── modules/
│       ├── database.py      # SQLite database API
│       ├── road.py          # Road sign module & quiz generation
│       ├── types.py         # Pydantic models
│       └── agent/
│           ├── __init__.py  # AI agent setup
│           └── prompt.py   # AI prompts for quizzes
├── pyproject.toml           # Project configuration & dependencies
├── .env                     # Environment variables (not in git)
├── env_template             # Environment template
└── README.md               # This file
```


### Database Management

The SQLite database (`database.db`) is automatically created in the project root. To reset:

```bash
rm database.db
# Database will be recreated on next run
```

## 📊 Database Schema

### `user` Table
- `id`: Primary key (auto-increment)
- `phone`: Unique phone identifier
- `sign_viewed`: JSON array of viewed sign IDs
- `blocked`: Boolean flag
- `pro`: Pro subscription status
- `created_at`: Timestamp

### `quizz` Table
- `id`: Primary key (UUID string)
- `user`: Foreign key to user.phone
- `question`: Question text
- `difficulty`: Difficulty level
- `type`: Quiz type ("general" or "sign")
- `correct`: Boolean (0/1)
- `created_at`: Timestamp

## 🤖 AI Integration

DriveWise uses [Pydantic AI](https://ai.pydantic.dev/) for AI-powered features:
- **Quiz Generation**: Creates contextually relevant questions
- **Sign Recognition**: Identifies road signs from images
- **Adaptive Learning**: Adjusts difficulty based on user history

### Supported LLM Providers

DriveWise supports multiple LLM providers through Pydantic AI. The default configuration uses Groq, but you can easily switch to other providers:

- **Groq** (default) - Fast inference with GPT-OSS-120B
- **OpenAI** - GPT-4, GPT-3.5, and other models
- **Anthropic** - Claude models
- **Google** - Gemini models
- **Mistral** - Mistral AI models
- **Cohere** - Command models
- And more...

To use a different provider:
1. Install the provider-specific dependencies (see [Installation](#2-install-dependencies))
2. Update the agent model in `src/modules/agent/__init__.py`
3. Set the appropriate environment variable

For detailed installation instructions, see the [Pydantic AI installation guide](https://ai.pydantic.dev/install/#slim-install).

## 📝 Road Signs Data

The project includes comprehensive data for 119+ French road signs, including:
- Warning signs (A-series)
- Regulatory signs (B-series)
- Information signs (C-series)
- Priority signs (AB-series)

Each sign includes:
- Official name and ID
- Category and subcategory
- Description and rules
- Typical locations
- Common mistakes
- High-quality images

## 🔒 Security Notes

- Never commit `.env` file with API keys (already in `.gitignore`)
- Database file (`database.db`) is excluded from git
- Use environment variables for sensitive configuration
- Keep your API key secure and rotate it if exposed


Made with ❤️ for safer roads

