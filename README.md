Music Metadata Processing System

Music Metadata Processing System is a FastAPI project for managing music data from musicbrainzngs api. 
It connects to a PostgreSQL database using environment variables and Docker Compose for local debugging.

Prerequisites

Before running the project, ensure you have the following installed:
- Python (>=3.7)
- Docker
- Docker Compose
- 
Installation
Clone the repository:
git clone https://github.com/yourusername/MusicAPI.git

Navigate to the project directory:
cd music_metadata_processing_system

Install the required Python libraries:
pip install -r requirements.txt

Create a .env file in the project directory and set the following environment variables:

DB_HOST=
DB_PORT=
DB_USER=
DB_PWD=
DB_NAME=

Running the Project
To run the project locally:

Start the PostgreSQL database using Docker Compose:
docker-compose up -d


Run the FastAPI application:

music_processing_api.main:app --host 127.0.0.1 --reload
The API will be available at http://127.0.0.1:8000.

The test task endpoint:
http://127.0.0.1:8000/musicbrainzngs/imagine_dragons/search_song/Demons