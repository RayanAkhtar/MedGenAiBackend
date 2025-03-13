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

## Environment Variables
You will need to have the following file in your system:
medgenaifirebase.json
You can generate this yourself or contact Mohamed Sharif (mas222@ic.ac.uk)for it.
You will also need to have the postgres database running with your username and password, we currently use medgen_user and blackberry as the username and password, this isn't running on the main server so make sure to keep your alternative usernames and passwords safe.


## Other Requirements
You will need to have a folder to contain images in the same level as this backend repo called MedGenAI-Images
Please contact Rayan Akhtar (ra1422@ic.ac.uk) for this.

### Running the Server
```
flask run
# or
python app.py
```

## Creating the database
We use a PostgreSQL database to store the data.
To create the database, first install the dependencies:
If on mac:
```
brew install postgresql
```

If on windows install from here: https://www.postgresql.org/download/windows/
If on linux:
```
sudo apt-get install postgresql postgresql-contrib
```

Then, start the server:
```
sudo service postgresql start
```

## Mac

```
brew install postgresql
psql postgres
CREATE DATABASE medgen;
CREATE USER medgen_user WITH PASSWORD 'blackberry';
GRANT ALL PRIVILEGES ON DATABASE medgen TO medgen_user;
\c medgen
GRANT ALL ON SCHEMA public TO medgen_user;
\q
```

## Windows

```
psql -U postgres
CREATE DATABASE medgen;
CREATE USER medgen_user WITH PASSWORD 'blackberry';
GRANT ALL PRIVILEGES ON DATABASE medgen TO medgen_user;
\c medgen
GRANT ALL ON SCHEMA public TO medgen_user;
\q
```

## Linux

```
sudo -u postgres psql
CREATE DATABASE medgen;
CREATE USER medgen_user WITH PASSWORD 'blackberry';
GRANT ALL PRIVILEGES ON DATABASE medgen TO medgen_user;
```


## Updating the database with new migrations
Some prerequisites are needed to be installed:
```
pip install Flask-Migrate
```

Then, run the following command to create a new migration:
```
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

If you need to reset the database, run the following command:
```
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```


## Backfilling the images database
Use the scripts/vm_images_setup.py file to backfill the images database, however you will need to have the images in the Images folder in the MedGenAi-Images folder which is in the same directory containing the MedGenAiBackend folder.
You can download this from a onedrive link.

Run the script with:
```
python scripts/vm_images_setup.py
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

