# MedGenAiBackend

The Flask backend for the MedGenAi project, designed to handle medical data processing and AI-powered analysis.

## Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation
1. Clone the repository
```
git clone https://github.com/RayanAkhtar/MedGenAiBackend.git
cd MedGenAiBackend
```

2. Create and activate a virtual environment
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```
pip install -r requirements.txt
```


### Running the Server
```
flask run
# or
python app.py
```

## Project Structure
```
MedGenAiBackend/
├── app/
│   ├── __init__.py
│   ├── routes/
│   ├── models/
│   └── services/
├── config/
│   └── config.py
├── tests/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

