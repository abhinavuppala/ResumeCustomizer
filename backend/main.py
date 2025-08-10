from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse

from resumecompiler.construct_latex import compile_latex, compile_latex_async, construct_latex_resume
from resumecompiler.resume_field_populator import DefaultResumeFieldPopulator, AIResumeFieldPopulator
import os
import sys


app = FastAPI()

@app.post("/tailored_resume/")
async def tailored_resume(
    job_info: str = Form(...)
):
    # Generate the LaTeX file
    tex_file_path = construct_latex_resume(
        AIResumeFieldPopulator(),
        job_info=job_info
    )

    # Compile to PDF
    # on windows async subprocess is not supported
    # so unfortunately this becomes a blocking operation
    if sys.platform.startswith("win"):
        compile_latex(tex_file_path, "build")
    else:
        await compile_latex_async(tex_file_path, "build")

    name = os.path.splitext(os.path.basename(tex_file_path))[0]
    pdf_path = os.path.join("build", name, f"{name}.pdf")

    # Return the PDF file as a download
    return FileResponse(pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path))