from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import redis
import hashlib
import asyncio

import os
import sys
import json
import shutil
from dotenv import load_dotenv

from resumecompiler.construct_latex import compile_latex, compile_latex_async, construct_latex_resume
from resumecompiler.resume_field_populator import DefaultResumeFieldPopulator, AIResumeFieldPopulator
import tasks


app = FastAPI()

load_dotenv()
assert os.getenv("REDIS_URL"), "Missing REDIS_URL environment variable"
r = redis.Redis.from_url(os.getenv("REDIS_URL"))

# Test Redis connection
try:
    r.ping()
    print("Connected to Redis!")
except ConnectionError:
    print("Failed to connect to Redis.")



@app.post("/resume")
async def generate_resume(job_info: str = Form(...)) -> StreamingResponse:
    """
    Generate tailored PDF resume from the job info.
    Saves the PDF in local memory, and return key to retrieve it 
    through GET /resume/{key} endpoint
    """
    def sse_response(event, data):
        return f'event: {event}\ndata: {data}\n\n'

    async def event_generator():

        # 1. generate unique primary key from job_info
        key = hashlib.sha256(job_info.encode('utf-8')).hexdigest()
        yield sse_response('progress', 'Checking cache...')

        # 2. check if key exists in redis
        if r.exists(key):
            yield sse_response('done', json.dumps({'key': key}))
            return

        # 3. generate .tex file using AI
        yield sse_response('progress', 'Generating AI resume...')
        tex_file_path, changelog = construct_latex_resume(
            AIResumeFieldPopulator(),
            job_info=job_info
        )

        # send changes made in changelog
        for change in changelog:
            change_string = f'>> Original: {change.before}\n' \
                          + f'>> After: {change.after}\n' \
                          + f'>> Reason: {change.reason}'
            yield sse_response('progress', change_string)

        # 4. compile to PDF (blocking on windows)
        yield sse_response('progress', 'Compiling LaTeX to PDF...')
        try:
            if sys.platform.startswith("win"):
                compile_latex(tex_file_path, "build")
            else:
                await compile_latex_async(tex_file_path, "build")
        except Exception as e:
            yield sse_response('error', f'Failed to compile LaTeX: {e}')
            return

        name = os.path.splitext(os.path.basename(tex_file_path))[0]
        pdf_path = os.path.join("build", name, f"{name}.pdf")
        dir_path = os.path.join("build", name)

        # Delete the .tex file
        try:
            os.remove(tex_file_path)
            yield sse_response('progress', 'Cleaned up intermediate files.')
        except Exception as e:
            yield sse_response('progress', f'Warning: Could not delete .tex file: {e}')

        # 5. store PDF path in redis for 5 mins
        ttl_seconds = 300
        r.set(key, json.dumps({'pdf_path': pdf_path}), ex=ttl_seconds)
        tasks.cleanup_directory.apply_async(args=[dir_path], countdown=ttl_seconds+1)

        # 6. return the key
        yield sse_response('done', json.dumps({'key': key}))

    return StreamingResponse(event_generator(), media_type='text/event-stream')



@app.get("/resume/{key}")
async def get_resume(key: str) -> FileResponse:
    """
    Get a previously generated resume using key as PDF FileResponse
    """
    cached = r.get(key)
    if not cached:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # check PDF path exists, then return it through FileResponse
    data = json.loads(cached)
    pdf_path = data.get('pdf_path')
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    return FileResponse(pdf_path, media_type='application/pdf', filename=os.path.basename(pdf_path))