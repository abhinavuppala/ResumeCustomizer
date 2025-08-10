import os

from resumecompiler.construct_latex import compile_latex, construct_latex_resume
from resumecompiler.resume_field_populator import DefaultResumeFieldPopulator, AIResumeFieldPopulator


if __name__ == '__main__':
    filename = input("What to call the resume file? ")
    job_info = input("Enter Job Description:\n")

    if job_info:
        tex_file_path = construct_latex_resume(
            AIResumeFieldPopulator(),
            job_info=job_info,
            output_filename=filename
        )
    else:
        tex_file_path = construct_latex_resume(
            AIResumeFieldPopulator(),
            output_filename=filename
        )
    compile_latex(tex_file_path, "build")