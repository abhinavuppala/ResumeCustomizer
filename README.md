# Resume Customizer Package

I can't seem to land a damn internship so I made this in hopes that it would help. To be honest it probably won't but it's a good learning experience nonetheless

## Technologies Used

- Python
- FastAPI
- Redis
- Celery
- Anthropic API
- LaTeX


# How to Run

## Requirements

- Docker
  - Must come with Docker Compose
- An existing resume
  - No specific format required but you need to have sections for education, experience, projects, and skills. You will have to convert this to a specific JSON format, which you can just ask an LLM to do for you or do yourself. (I plan to add a feature for this at some point)
- Git (obviously)


## Instructions

1. Clone repo to local machine and enter backend/ directory
2. Create a .env file with:
   1. `REDIS_URL=redis://redis:6379/0`
   2. `ANTHROPIC_API_KEY=<your_api_key>`
3. To build and start the containers first time:
   1. `docker compose up --build`
4. To run containers after they've been build:
   1. `docker compose up`
5. To stop the containers:
   1. `docker compose down`

You should also be able to run it through Docker Desktop.

Then to host the frontend:

1. Navigate to frontend/ in a different terminal
2. Run `npm run dev`, and go to localhost:3000

This runs locally and works better for personal use.
I haven't hosted it yet since I need to implement a way for other users to add their own API keys when making requests, as I don't have the kind of money to let people use my API key.


This will run our server on port 8080. It has the following endpoints:

- `POST /resume`: Takes job_info in body (string), and returns a key which we can use with the GET to download a tailored PDF resume to the given job_info
  - It returns a StreamingResponse, giving constant text updates of the process until the final one with the key.
  - Any POSTs with the same job_info for the next 5 minutes will return the cached key rather than generating another resume.
- `GET /resume/{key}`: Takes the string key, and returns a FileResponse PDF with the stored resume
  - This resume lives for 5 minutes after the original POST in local memory. Any subsequent GETs in that time will return the same resume.


Test it with these commands:

- `curl -N -X POST http://127.0.0.1:8080/resume -F "job_info=<job_info>"`
- `curl -X GET http://127.0.0.1:8080/resume/<your_key> --output resume.pdf`


# Features to Add

- Containerize backend for ease of use
- Create & deploy a frontend
- Possibly - deploy a backend where users can use their own API key & select model type, so they don't have to run a container locally



# Optional - Run without Docker Compose

As of 8-10-25

## Requirements

- An existing resume
  - No specific format required but you need to have sections for education, experience, projects, and skills. You will have to convert this to a specific JSON format, which you can just ask an LLM to do for you or do yourself. (I plan to add a feature for this at some point)
- Python 3.11
- LaTeX installed locally
  - Needs to be able to run `pdflatex` in command line
- Anthropic API Key
- Docker (or Redis installed another way)


### Setup

1. Clone the repo to your local machine
2. Enter backend/ directory
3. Add key ANTHROPIC_API_KEY to `.env`, and `REDIS_URL=redis://redis:6379/0`
4. In static/base_resume.json, replace the fields with your own resume's data. As mentioned earlier you can do this manually or use an LLM.
5. In static/template.tex, scroll to the bottom where you'll see the section for the header. Edit these to show your name, email, phone number, etc. Add/remove any fields you want/don't want, just make sure it's seperated by $|$
6. Create a python virtual environment and `pip install -r requirements.txt`
7. Run `docker pull redis` to get the Redis image. If you have Redis already then no need to do this step. I used the image ID sha256:b0efb06f6b4d8c1e2fd1b7c1e89e178d787b432b7b09286b4e7ea3dcdbac777a (latest version as of 8-10-25), in case it causes compatibility issues.

### Run

1. Start a terminal and run `docker run --name redis -d -p 6379:6379 redis`. 
   1. This will start the redis server locally on port 6379. This enables us to cache responses for 5 minutes and prevent unnecessary Anthropic API use.
2. In another terminal, run `celery -A tasks.celery_app worker --loglevel=info` while in the backend directory.
   1.  If you are on windows you will need to set the environment variable FORKED_BY_MULTIPROCESSING=1. I recommend doing this in this terminal with `set FORKED_BY_MULTIPROCESSING=1`. Make sure you run this before starting the celery worker.
   2.  This enables us to automatically delete PDF files from local memory after it expires in redis.
3. In another terminal, while in the backend directory, run `uvicorn main:app --reload --port 8080`. 
   1. This starts our server on port 8080, and automatically reloads the server when we make code changes.
4. To test, you can use curl. Swagger UI will not work because POST /resume returns a StreamingResponse (gives us constant updates on progress).
   1. Give a job description & return a key -> `curl -N -X POST http://127.0.0.1:8080/resume -F "job_info=<your job description here>"`
   2. Give a key & return a PDF file download -> `curl -X GET http://127.0.0.1:8080/resume/<your_key> --output resume.pdf`