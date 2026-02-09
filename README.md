# Communication Bridge AI

Production-ready autonomous agent system for bridging communication between verbal and non-verbal users.

## System Architecture

### Multi-Agent System
- **Intent Detection Agent**: Determines user intent from input
- **Non-Verbal Interpretation Agent**: Converts gesture tokens/symbols to semantic meaning
- **Speech/Text Generation Agent**: Produces output for verbal users
- **Context & Learning Agent**: Stores session context and adapts responses
- **Coordinator Agent**: Central decision-maker routing tasks between agents

### Tech Stack
- **Backend**: Python FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **AI**: Google Gemini API
- **Database**: SQLite
- **Deployment**: Vultr VM (Linux)

## Quick Start

### Local Development

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Set Environment Variable**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

3. **Run Backend**
```bash
cd backend
python main.py
```

4. **Open Frontend**
Open `frontend/index.html` in your browser or serve with:
```bash
python -m http.server 8080 --directory frontend
```

### Docker Deployment

1. **Build Image**
```bash
docker build -t communication-bridge-ai .
```

2. **Run Container**
```bash
docker run -d -p 8000:8000 -e GEMINI_API_KEY="your-key" communication-bridge-ai
```

## Vultr Deployment

### Setup VM

1. Create Ubuntu 22.04 VM on Vultr
2. SSH into server
3. Install Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Deploy Application

```bash
# Clone repository
git clone <your-repo-url>
cd communication-bridge-ai

# Build and run
docker build -t comm-bridge .
docker run -d -p 80:8000 -e GEMINI_API_KEY="your-key" --name comm-bridge comm-bridge
```

### Configure Firewall
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## API Endpoints

- `POST /simulate/start` - Start classroom simulation
- `POST /simulate/step` - Process simulation step
- `POST /communicate` - Direct communication endpoint
- `GET /logs` - Retrieve agent logs
- `GET /session/{id}` - Get session details
- `GET /sessions` - List recent sessions

## Features

### Autonomous Operation
- Automatic agent selection and routing
- Confidence-based retry logic
- Decision logging and context tracking
- No manual intervention during simulation

### Classroom Simulation
- Non-verbal student input (text, symbols, gestures)
- AI processing with multi-agent coordination
- Verbal teacher output
- Real-time workflow visualization

### Token System
Predefined gesture tokens:
- 👋 Greeting
- 🙋 Need attention/help
- ❓ Question
- ✋ Stop/wait
- 👍 Yes/agree
- 👎 No/disagree
- 🚽 Bathroom need
- 🍎 Hungry/food
- 💧 Thirsty/water

## Project Structure

```
communication-bridge-ai/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── coordinator/
│   │   └── orchestrator.py     # Central coordinator
│   ├── agents/
│   │   ├── intent_agent.py
│   │   ├── nonverbal_agent.py
│   │   ├── speech_agent.py
│   │   └── context_agent.py
│   ├── simulation/
│   │   └── classroom_sim.py
│   └── database/
│       ├── db.py
│       └── models.py
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── app.js
│   └── styles.css
├── requirements.txt
├── Dockerfile
└── README.md
```

## Usage

1. Open dashboard at `http://your-server-ip/dashboard.html`
2. Click "Start Simulation"
3. Enter non-verbal input (text or tokens)
4. Click "Send Message"
5. View AI processing workflow
6. See teacher output
7. Monitor agent decision logs

## Configuration

### Environment Variables
- `GEMINI_API_KEY`: Google Gemini API key (required for AI features)

### Database
SQLite database created automatically at `communication_bridge.db`

## Production Considerations

- Set up HTTPS with Let's Encrypt
- Configure proper logging
- Implement rate limiting
- Add authentication if needed
- Monitor resource usage
- Set up backup for database
- Use PostgreSQL for production scale

## License

MIT
