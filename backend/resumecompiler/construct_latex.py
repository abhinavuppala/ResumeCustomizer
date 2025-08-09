import subprocess
import os

def compile_latex(tex_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    subprocess.run(
        ["pdflatex", "-output-directory", output_dir, tex_path],
        check=True
    )