import subprocess
import os
from datetime import datetime

from resumecompiler.resume_field_populator import BaseResumeFieldPopulator
from resumecompiler.models import *


def compile_latex(tex_path: str, output_dir: str = 'build') -> None:
    """
    Compile the latex at the given path to a PDF using pdflatex.
    Need to have some version of latex installed along with the relevant packages.
    """
    os.makedirs(output_dir, exist_ok=True)
    subprocess.run(
        ["pdflatex", "-output-directory", output_dir, tex_path],
        check=True
    )


def construct_latex_resume(field_populator: BaseResumeFieldPopulator, output_filename: str = "") -> str:
    """
    Construct a .tex file of a custom resume from a template & Resume object
    """
    resume: Resume = field_populator.get_resume_data()

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

    # by default use current time to add to filename
    if not output_filename:
        output_filename = f"AbhinavUppala_Resume_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.tex"

    # write to new tex file
    result_path = os.path.join(".", "tex", output_filename)
    with open(result_path, "w") as f:
        f.write(template_str)
    
    print(f"Saved latex resume to {result_path}")
    return result_path