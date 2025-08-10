import subprocess
import os
from pathlib import Path
from datetime import datetime

from resumecompiler.resume_field_populator import BaseResumeFieldPopulator
from resumecompiler.models import *


def compile_latex(tex_path: str, output_dir: str = 'build') -> None:
    """
    Compile the latex at the given path to a PDF using pdflatex.
    Need to have some version of latex installed along with the relevant packages.
    """
    name = Path(tex_path).stem
    output_dir = os.path.join(output_dir, name)
    os.makedirs(output_dir, exist_ok=True)

    # to debug, remove "-interaction=nonstopmode"
    # and remove the stdout & stderr specifiers
    print(f"Compiling {tex_path} -> PDF")
    subprocess.run(
        ["pdflatex", "-output-directory", output_dir, tex_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )
    print("Output saved at main.pdf.\n")


def construct_latex_resume(
        field_populator: BaseResumeFieldPopulator,
        job_info: str = "No job info given. Assume it's a generic SWE internship.",
        output_filename: str = ""
    ) -> str:
    """
    Construct a .tex file of a custom resume from a template & Resume object
    """
    print(f"Populating resume data from {field_populator.name()}...")
    resume: Resume = field_populator.get_resume_data(job_info)
    print(f"Resume data populated.\n")

    # by default use current time to add to filename
    if not output_filename:
        output_filename = f"AbhinavUppala_Resume_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.tex"
        print("Filename not specified. Using current datetime for filename.")
    print(f"Writing to file {output_filename} ...")

    # read template.tex
    with open(os.path.join(".", "static", "template.tex")) as f:
        template_str = f.read()

    # use given field populator to add resume info to template doc
    template_str += "\n" + ComponentCompiler.compile_education(resume.education)
    
    template_str += '\n\\section{Experience}\n\\resumeSubHeadingListStart'
    for experience in resume.experiences:
        template_str += "\n" + ComponentCompiler.compile_experience(experience)
    template_str += '\n\\resumeSubHeadingListEnd'

    template_str += '\n\\section{Projects}\n\\resumeSubHeadingListStart'
    for project in resume.projects:
        template_str += "\n" + ComponentCompiler.compile_project(project)
    template_str += '\n\\resumeSubHeadingListEnd'

    template_str += "\n" + ComponentCompiler.compile_skills(resume.skills)
    template_str += '\n\\end{document}'
    
    # write to new tex file
    result_path = os.path.join(".", "tex", output_filename)
    os.makedirs(os.path.join(".", "tex"), exist_ok=True)
    with open(result_path, "w") as f:
        f.write(template_str)
    
    print(f"Saved latex resume to {result_path}.\n")
    return result_path