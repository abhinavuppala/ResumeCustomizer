import os
from resumecompiler.construct_latex import compile_latex, construct_latex_resume
from resumecompiler.resume_field_populator import DefaultResumeFieldPopulator

construct_latex_resume(DefaultResumeFieldPopulator(), "main.tex")
compile_latex(os.path.join("tex", "main.tex"), "build")