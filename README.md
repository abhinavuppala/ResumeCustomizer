# Resume Customizer Package

## Requirements

- An existing resume
  - No specific format required but you need to have sections for education, experience, projects, and skills. You will have to convert this to a specific JSON format, which you can just ask an LLM to do for you or do yourself. (I plan to add a feature for this at some point)
- Python 3.11
- LaTeX installed locally
  - Needs to be able to run `pdflatex` in command line
- Anthropic API Key


## Instructions

1. Clone the repo to your local machine
2. Enter backend/ directory
3. Add key ANTHROPIC_API_KEY to `.env`
4. In static/base_resume.json, replace the fields with your own resume's data. As mentioned earlier you can do this manually or use an LLM.
5. In static/template.tex, scroll to the bottom where you'll see the section for the header. Edit these to show your name, email, phone number, etc. Add/remove any fields you want/don't want, just make sure it's seperated by $|$
6. Create a python virtual environment and `pip install -r requirements.txt`
7. Run `python main.py`