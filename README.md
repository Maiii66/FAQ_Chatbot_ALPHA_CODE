🏋️ FitZone Gym FAQ Chatbot
A lightweight, production-structured FAQ chatbot for a gym website. The system uses classical Natural Language Processing (NLP) rather than a generative LLM: user questions are cleaned and normalized, converted into TF-IDF vectors, and matched against a curated FAQ knowledge base using cosine similarity.
Project type: Retrieval-based NLP chatbot
Domain: Gym / Fitness FAQ
Backend: Python + Flask
NLP: NLTK + TF-IDF + Cosine Similarity
Frontend: HTML + CSS + Vanilla JavaScript
Data source: CSV
Testing: Pytest + dedicated accuracy evaluation

✨ Key Features
- 💬 Natural-language FAQ matching
- 🔎 TF-IDF + cosine similarity retrieval
- 🧹 NLP preprocessing with:
  - lowercasing
  - punctuation normalization
  - tokenization
  - stop-word removal
  - synonym normalization
  - Porter stemming
- 🧠 Curated keyword matching to improve intent detection
- 🛡️ Similarity threshold to reject weak/irrelevant questions
- 🎯 Token-coverage gate to reduce false-positive matches
- ⚡ Intent overrides for highly ambiguous one-word queries
- 📊 Similarity-based confidence score
- 🏷️ FAQ category returned with every successful response
- 🌐 Flask REST API
- 📱 Responsive web chat interface
- ♿ Accessibility considerations such as labels, live chat semantics, focus states and reduced-motion support
- ❤️ Health-check endpoint for basic service monitoring
- 🧪 Unit, integration and accuracy tests
- ⚙️ Environment-variable configuration via .env
🏗️ Architecture
                         ┌─────────────────────┐
                         │   User / Browser    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Flask Web App     │
                         │    app/main.py      │
                         └──────────┬──────────┘
                                    │
                           POST /api/chat
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    FAQChatbot       │
                         │   src/chatbot.py    │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     ▼                             ▼
          ┌────────────────────┐        ┌────────────────────┐
          │ TextPreprocessor   │        │ SimilarityMatcher  │
          │ preprocessing.py   │        │ similarity.py     │
          └─────────┬──────────┘        └─────────┬──────────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │     faqs.csv        │
                         │  56 FAQ records     │
                         └─────────────────────┘
                                   │
                                   ▼
                         JSON response to UI
📁 Project Structure
FAQ_Chatbot_ALPHA_CODE-main/
│
├── app/
│   ├── main.py                 # Flask application and API routes
│   ├── static/
│   │   ├── script.js            # Frontend chat logic
│   │   └── style.css            # UI styling and responsive design
│   └── templates/
│       └── index.html           # Chat interface
│
├── config/
│   └── settings.py             # Paths and runtime configuration
│
├── data/
│   └── faqs.csv                # FAQ knowledge base
│
├── src/
│   ├── __init__.py
│   ├── chatbot.py              # Main chatbot orchestration
│   ├── preprocessing.py        # NLP preprocessing pipeline
│   ├── similarity.py           # TF-IDF and cosine similarity
│   └── utils.py                # Windows UTF-8 console helper
│
├── tests/
│   ├── conftest.py             # Shared pytest fixture
│   ├── eval.py                 # End-to-end accuracy evaluation
│   ├── test_accuracy.py        # Parameterized FAQ accuracy tests
│   ├── test_app.py             # Flask/API tests
│   ├── test_chatbot.py         # Chatbot behavior tests
│   └── test_preprocessing.py   # NLP preprocessing tests
│
├── .env.example                # Example environment configuration
├── .gitignore
├── pytest.ini
└── requirements.txt
🧠 How the Chatbot Works
1. Load the knowledge base
data/faqs.csv contains 56 FAQ records with:
- id
- question
- answer
- category
- keywords
The categories currently represented are:
Category	FAQ Count
Membership	8
Facilities	7
About	7
Classes	7
Timings	6
Greeting	5
Payment	5
Policies	4
Hygiene	3
Services	3
Safety	1


2. Preprocess the FAQ content
Each FAQ question, answer and keyword field is passed through the same preprocessing pipeline used for incoming user questions.
Example:
"What's the membership price?"
            ↓
lowercase
            ↓
punctuation normalization
            ↓
tokenization
            ↓
synonym mapping: price → cost
            ↓
stop-word removal
            ↓
stemming
            ↓
"membership cost"
Using the same preprocessing on both sides makes wording variations easier to match.
3. Normalize synonyms
The project contains a small domain-specific synonym map.
Examples:
price / pricing → cost
hours / timing / closing → timing
weekend → holiday
diet → nutrition
protein → supplement
corona / coronavirus → covid
pause → freeze
This is a simple but effective way to handle common user vocabulary.
4. Convert text to TF-IDF vectors
The project uses Scikit-learn's TfidfVectorizer.
TF-IDF gives higher importance to words that are useful for distinguishing documents and lower importance to words that appear across many documents.
5. Calculate cosine similarity
The processed user query is compared against the FAQ question vectors and the additional keyword/answer matching text.
Conceptually:
similarity = cosine(user_vector, faq_vector)
The result is between 0 and 1 for the relevant vector comparison.
6. Apply the token-coverage gate
The matcher does not rely only on similarity.
It also checks whether more than half of the user's meaningful query tokens occur in the candidate FAQ vocabulary.
This reduces cases where a generic word such as discount causes an unrelated FAQ to win.
7. Apply the similarity threshold
The default threshold is:
SIMILARITY_THRESHOLD = 0.25
If the best candidate is below the threshold, the chatbot returns a no_match response instead of guessing.
8. Apply intent overrides
Some very short queries are too ambiguous for TF-IDF.
The current code explicitly maps:
class / classes → FAQ 28
facil / facilities → FAQ 23
This is implemented in src/chatbot.py.
9. Return structured JSON
A successful response contains:
{
  "answer": "...",
  "confidence": "85.4%",
  "category": "Timings",
  "faq_id": 20,
  "status": "success"
}
For an unknown question:
{
  "answer": "I couldn't find an exact match...",
  "confidence": "0%",
  "category": "unknown",
  "status": "no_match"
}
Important: the confidence value is the similarity score expressed as a percentage. It is not a statistically calibrated probability of correctness.

🌐 API
GET /
Returns the main chatbot web page.
POST /api/chat
Request:
{
  "message": "What are the gym timings?"
}
Successful response:
{
  "answer": "...",
  "confidence": "100.0%",
  "category": "Timings",
  "faq_id": 20,
  "status": "success"
}
GET /api/health
Returns basic application health information:
{
  "status": "healthy",
  "faqs_loaded": 56
}
🚀 Installation
1. Clone the repository
git clone <your-repository-url>
cd FAQ_Chatbot_ALPHA_CODE-main
2. Create a virtual environment
Windows:
python -m venv venv
venv\Scripts\activate
macOS/Linux:
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables
Copy:
.env.example → .env
Default configuration:
DEBUG=true
PORT=5000
SIMILARITY_THRESHOLD=0.25
MAX_RESULTS=3
VERBOSE=false
For deployment, use:
DEBUG=false
5. Run the application
python app/main.py
Open:
http://localhost:5000
🧪 Testing
Run the full test suite:
pytest -q
Run the dedicated accuracy evaluation:
python tests/eval.py
The evaluation harness contains representative queries covering:
- greetings
- timings
- membership
- facilities
- classes
- payment
- policies
- safety
- services
- irrelevant queries
- regression cases
The expected behavior is defined explicitly in tests/eval.py.
⚙️ Configuration
Variable	Default	Purpose
DEBUG	true	Flask debug mode
PORT	5000	Local server port
SIMILARITY_THRESHOLD	0.25	Minimum similarity for a match
MAX_RESULTS	3	Number of candidates considered
VERBOSE	false	Enables detailed startup logging


🔐 Security & Production Notes
This is a local/demo-oriented application and should be hardened before public production deployment.
Recommended next steps:
- Use a production WSGI server such as Gunicorn/waitress.
- Put the application behind HTTPS.
- Disable Flask debug mode.
- Add rate limiting.
- Validate and limit request sizes server-side.
- Add structured logging.
- Avoid returning raw exception messages to clients.
- Add authentication if the API becomes private.
- Add monitoring and error tracking.
- Consider a persistent database for larger knowledge bases.
📈 Strengths
- Simple and inexpensive to run
- No paid LLM/API required
- Deterministic retrieval behavior
- Fast inference for a small FAQ dataset
- Easy to understand and maintain
- Explicit test cases make regressions easier to detect
- Domain-specific synonym handling improves matching
- Thresholding helps prevent random answers
⚠️ Current Limitations
- It is not a generative AI chatbot.
- It cannot create new answers outside the FAQ knowledge base.
- It depends heavily on the quality and coverage of the CSV data.
- TF-IDF can struggle with semantic paraphrases that share few words.
- The synonym map is manually maintained.
- Intent overrides are manually maintained.
- The confidence score is a similarity score, not a calibrated probability.
- The current dataset is small and gym-specific.
- Conversation memory/context is not implemented.
- There is no authentication, rate limiting or production deployment layer.
🔮 Possible Future Improvements
NLP / Retrieval
- Add n-gram features.
- Tune TF-IDF parameters using the evaluation set.
- Add fuzzy matching for spelling mistakes.
- Use sentence embeddings for semantic similarity.
- Add a hybrid BM25 + vector retrieval approach.
- Add reranking for top candidates.
Knowledge Base
- Move FAQs from CSV to PostgreSQL/SQLite.
- Add an admin interface for editing FAQs.
- Add versioning for knowledge-base changes.
- Add multilingual FAQs.
Product Features
- Conversation history
- Suggested follow-up questions
- Admin analytics dashboard
- Unanswered-question logging
- Human handoff
- WhatsApp/Telegram integration
- Authentication
- User feedback buttons
Production
- Dockerize the application.
- Add CI/CD.
- Add structured logs and monitoring.
- Deploy behind a reverse proxy.
- Add automated evaluation on every knowledge-base change.
👨‍💻 Project Summary
FitZone Gym FAQ Chatbot demonstrates how a practical FAQ assistant can be built using classical NLP, information retrieval and a lightweight Flask web application without relying on a paid generative AI API.
The project combines:
Data → NLP preprocessing → TF-IDF → Similarity matching
     → Threshold/coverage checks → Flask API → Web UI
This makes it a useful portfolio project for demonstrating Python, NLP fundamentals, information retrieval, Flask API development, frontend integration and software testing.
📄 License
MIT License.
👤 Author
Maiyarasu M
Computer Science / Data Science Student
