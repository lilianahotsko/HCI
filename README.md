# HCI Research Experiment - Movie Dataset Search Platform

A web-based dataset search platform for HCI research comparing three search interfaces:
1. **Faceted baseline** - Traditional filter-based search
2. **LLM-assisted NL with preview** - Natural language input with query preview
3. **LLM-only NL with RAG** - Natural language input with direct answers

## System Architecture

- **Frontend**: React (Vite) SPA
- **Backend**: Flask REST API
- **Database**: SQLite (default) or PostgreSQL
- **LLM**: OpenAI GPT-4 (configurable)

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key (for LLM features)
- TMDB 5000 Movies dataset CSV file

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```bash
cp .env.example .env
```

5. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4
DATABASE_URL=sqlite:///hci_experiment.db
```

6. Download the TMDB 5000 Movies dataset:
   - Download from: https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata
   - Place `tmdb_5000_movies.csv` in the backend directory
   - Or set `TMDB_CSV_PATH` in `.env` to point to the file location

7. Load the data into the database:
```bash
python preprocess_data.py
```

8. Start the Flask server:
```bash
# Make sure you're in the backend directory and venv is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

The backend will run on `http://localhost:5001` (using port 5001 because macOS AirPlay Receiver uses port 5000)

**Troubleshooting:**
- If you get "access denied" or 403 errors, follow these steps:

  1. **Verify the server is running:**
     ```bash
     cd backend
     source venv/bin/activate
     python app.py
     ```
     You should see: `Running on http://0.0.0.0:5001` or `Running on http://127.0.0.1:5001`
  
  2. **Test the server:**
     ```bash
     # In another terminal, test the health endpoint:
     curl http://localhost:5001/api/health
     # Should return: {"status":"ok","message":"Backend is running"}
     ```
  
  3. **Access via frontend proxy (recommended):**
     - Start frontend: `cd frontend && npm run dev`
     - Access: `http://localhost:3000` (frontend will proxy `/api/*` to backend on port 5001)
  
  4. **If accessing backend directly:**
     - Use: `http://localhost:5001/api/health` or `http://127.0.0.1:5001/api/health`
     - Make sure the server is actually running (check terminal)
  
  5. **Common issues:**
     - Port 5000 already in use (macOS AirPlay Receiver): Already configured to use port 5001
     - If port 5001 is also in use: Change port in `app.py` to any available port (e.g., 5002)
     - Firewall blocking: Temporarily disable firewall to test

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Usage

1. Open `http://localhost:3000` in your browser
2. Enter a participant ID (e.g., "P01")
3. Read and accept the consent form
4. Complete the experiment tasks in the assigned interface order
5. Fill out questionnaires after each interface

## Experiment Flow

1. **Participant Login**: Enter participant ID
2. **Consent**: Read and accept consent form
3. **Interface Blocks**: Complete tasks for each interface (order randomized)
4. **Questionnaires**: After each interface, complete SUS, NASA-TLX, Trust, and Preference questionnaires
5. **Completion**: View completion message

## Data Collection

All interactions are logged to the database:

- **Logs**: All events (filter changes, queries, task starts/ends)
- **Questionnaires**: All questionnaire responses
- **Task Submissions**: Selected movies and answers for each task

### Database Schema

- `movies`: Movie data from TMDB dataset
- `participants`: Participant information and interface order
- `tasks`: Task definitions with ground truth
- `log_entries`: All interaction events
- `questionnaire_responses`: Questionnaire submissions

## API Endpoints

### Experiment Control
- `POST /api/experiment/participant` - Create/get participant
- `POST /api/experiment/consent` - Record consent
- `GET /api/experiment/plan?participant_id=X` - Get experiment plan

### Search
- `POST /api/search/faceted` - Faceted search
- `POST /api/search/llm_assist/parse` - Parse NL query (LLM-assisted)
- `POST /api/search/llm_assist/execute` - Execute parsed query
- `POST /api/search/llm_only` - LLM-only search with RAG

### Logging
- `POST /api/log` - Generic event logging
- `POST /api/log/task/start` - Log task start
- `POST /api/log/task/end` - Log task end

### Questionnaires
- `POST /api/questionnaire` - Submit questionnaire responses

## Development

### Adding New Tasks

Edit `backend/preprocess_data.py` and add tasks to the `create_sample_tasks()` function.

### Modifying Interfaces

- Faceted: `frontend/src/components/interfaces/FacetedInterface.jsx`
- LLM-Assisted: `frontend/src/components/interfaces/LLMAssistInterface.jsx`
- LLM-Only: `frontend/src/components/interfaces/LLMOnlyInterface.jsx`

### Customizing Questionnaires

Edit questionnaire components in `frontend/src/components/questionnaires/`

## Notes

- The system uses counterbalanced design: 6 permutations of interface order
- Each participant sees all three interfaces
- Tasks are marked as "simple" or "complex"
- All interactions are timestamped for analysis

## Data Analysis

After running experiments, you can analyze the results using the analysis script:

```bash
cd backend
source venv/bin/activate
python analyze_results.py
```

### Available Commands:

1. **Export all data to CSV:**
   ```bash
   python analyze_results.py export
   ```
   Creates CSV files in the `results/` folder (project root):
   - `results/task_performance.csv` - Task completion times, reformulations, accuracy
   - `results/questionnaire_responses.csv` - SUS, NASA-TLX, trust, preference responses
   - `results/all_logs.csv` - All interaction logs
   - `results/participants.csv` - Participant information and interface orders

2. **View summary statistics:**
   ```bash
   python analyze_results.py summary
   ```

3. **View specific data:**
   ```bash
   python analyze_results.py tasks          # Task performance data
   python analyze_results.py questionnaires # Questionnaire responses
   python analyze_results.py participants    # Participant data
   ```

4. **Generate visualizations:**
   ```bash
   python create_visualizations.py
   ```
   Creates visualization files in `results/visualizations/`:
   - `task_duration_by_interface.png` - Box plots of completion times
   - `reformulations_by_interface.png` - Average reformulation counts
   - `sus_scores_by_interface.png` - System Usability Scale scores
   - `nasa_tlx_by_interface.png` - NASA-TLX workload scores
   - `trust_scores_by_interface.png` - Trust questionnaire ratings
   - `preference_scores_by_interface.png` - User preference ratings
   - `task_duration_by_complexity.png` - Performance by task complexity
   - `summary_dashboard.png` - Combined dashboard with key metrics

### Direct Database Access:

You can also access the SQLite database directly:

```bash
cd backend
sqlite3 hci_experiment.db
```

Useful queries:
```sql
-- View all participants
SELECT * FROM participants;

-- View task completions
SELECT participant_id, task_id, interface_type, event_type, timestamp 
FROM log_entries 
WHERE event_type = 'task_completed'
ORDER BY timestamp;

-- View questionnaire responses
SELECT participant_id, interface_type, questionnaire_type, responses 
FROM questionnaire_responses;

-- Calculate average task duration by interface
SELECT interface_type, 
       AVG((julianday(end_time) - julianday(start_time)) * 86400) as avg_duration_seconds
FROM (
  SELECT participant_id, task_id, interface_type,
         MIN(CASE WHEN event_type = 'task_started' THEN timestamp END) as start_time,
         MAX(CASE WHEN event_type = 'task_completed' THEN timestamp END) as end_time
  FROM log_entries
  GROUP BY participant_id, task_id, interface_type
) GROUP BY interface_type;
```

### Key Metrics Available:

- **Task Completion Time**: Duration from task_started to task_completed
- **Reformulations**: Number of query modifications (counted from logs)
- **Accuracy**: Compare selected_movie_ids with ground_truth (requires manual comparison)
- **SUS Scores**: System Usability Scale responses
- **NASA-TLX Scores**: Workload assessment scores
- **Trust Ratings**: Trust questionnaire responses
- **Preferences**: Interface preference ratings

## License

For research use only.
