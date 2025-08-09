import os
from resumecompiler.construct_latex import compile_latex


compile_latex(os.path.join("static", "main.tex"), "build")