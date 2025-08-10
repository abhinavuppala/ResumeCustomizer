import anthropic
from dotenv import load_dotenv
import os
import requests
import json

from enum import Enum
from pydantic import BaseModel

from resumecompiler.resume_field_populator import BaseAIInterface
from resumecompiler.models import *


# Load anthropic API key
load_dotenv()
assert os.environ.get('ANTHROPIC_API_KEY', '') != '', "Add anthropic API key to .env"


system_prompt = f"""
You are an expert resume writer who tailors resumes to specific job postings.
Always output only valid JSON.
Never include extra text, explanations, or formatting outside the JSON.

Your response must follow this JSON schema:
{json.dumps(ResumeCustomizationResult.model_json_schema(), indent=2)}

`resume` should preserve all existing structure from the input resume JSON unless modified to improve alignment with the job posting.
`changelog` must contain one entry per change made, explaining the reasoning. Each reason should be 15 words max.

You only make changes when they pertain to the specific job description given
and have a large positive impact on making the candidate seem more desirable.

This could include adding specific hard or soft skill keywords by modifying bullet points or
changing/reordering the skills section to highlight specific relevant skills.

However, do not make up any skills, experiences, or figures that aren't specifically stated on the resume.
"""

prompt = """
Here is the job posting:

{job_description}

Here is my current resume (in JSON format):

{resume}

Here are the constraints and rules:
{rules}

Please return only valid JSON following the schema in the system prompt.
"""

rules_and_constraints = """
Any special characters in latex like # $ % & _ { } ~ ^ \\ must be escaped with a backslash.
In particular avoid the characters ~ ^ \\ as they are more complex to deal with.

Any unicode-8 characters are allowed. However, make sure the resume is ATS friendly,
so try and limit the amount of rare and possibly-unsupported characters used.

Mimic the tone, style, and convention in the original resume. For instance, if all bullet points end
with a . then make sure yours do as well, and vice versa.

Be concise and direct - make sure each bullet point is purposeful.
When unsure about modifying a bullet point, you should choose to leave it the same.

Any modified bullet points should be the same length as the original or shorter.
That may mean cutting out some less important info in favor of new information.

Do **NOT** add any hard skills to the resume that aren't explicitly already listed.
"""


class AnthropicModel(Enum):
    opus_4_1 = "claude-opus-4-1-20250805"
    sonnet_4 = "claude-sonnet-4-20250514"
    haiku_3_5 = "claude-3-5-haiku-20241022"
    haiku_3 = "claude-3-haiku-20240307"

class AnthropicAIInterface(BaseAIInterface):
    def __init__(self):
        """
        Initializes client
        """
        self.client = anthropic.Anthropic()

    def generate_customized_resume(
            self,
            base_resume: Resume,
            job_info: str,
            model: AnthropicModel = AnthropicModel.sonnet_4
        ) -> ResumeCustomizationResult:
        """
        Generates a resume tailored to the job posting along with a log of changes made.
        """
        print(f"\nPrompting {model.name}...")

        # Use Python SDK to get anthropic LLM response
        # pass in system prompt & formatted base prompt from above
        response = self.client.messages.create(
            model=model.value,
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": prompt.format(
                        job_description=job_info,
                        resume=json.dumps(base_resume.model_dump_json(), indent=2),
                        rules=rules_and_constraints
                    )
                }
            ],
        )
        print(f"{model.name} response received.")
        response_content = response.content[0].text.lstrip('```json').rstrip('```')

        # try converting to JSON
        try:
            output = json.loads(response_content)
        except:
            print(response_content)
            raise RuntimeError("Anthropic model response was not JSON. Might have run out of tokens too.")
        
        # try converting to specified schema
        try:
            result = ResumeCustomizationResult.model_validate(output)
        except:
            print(output)
            raise RuntimeError("Anthropic model response was JSON, but did not meet the schema.")

        return result
    
    def name(self) -> str:
        return f"Anthropic AI Interface"