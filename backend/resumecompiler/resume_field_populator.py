import os

from resumecompiler.models import *
from resumecompiler.claude_interface import AnthropicAIInterface


class DefaultResumeFieldPopulator(BaseResumeFieldPopulator):
    def get_resume_data(self, job_info: str) -> Resume:
        """
        Get Abhinav Uppala default resume info (as of 8-9-25)
        Does NOT customize it to the job info
        """
        with open(os.path.join('static', 'base_resume.json'), 'r') as f:
            json_str = f.read()
        resume = Resume.model_validate_json(json_str)
        return resume
    
    def name(self) -> str:
        return "Default Resume Populator"
    

class AIResumeFieldPopulator(BaseResumeFieldPopulator):
    def get_resume_data(self, job_info: str, ai_interface: BaseAIInterface = AnthropicAIInterface()):
        """
        Generates a tailored version of Abhinav's Resume (8-9-25) to the job info.
        Also prints out a log of the changes made to the resume by the LLM
        """
        with open(os.path.join('static', 'base_resume.json'), 'r') as f:
            json_str = f.read()
        base_resume = Resume.model_validate_json(json_str)

        # use injected AI interface to generate tailored resume
        result: ResumeCustomizationResult = ai_interface.generate_customized_resume(base_resume, job_info)
        changelog = result.changelog
        tailored_resume = result.resume

        # print changes made if any
        if not changelog:
            print("No changes made.")
            return tailored_resume
        
        print("Changes made:\n")
        for change in changelog:
            print(f">> ORIGINAL: {change.before}")
            print(f">> AFTER:    {change.after}")
            print(f">> REASON:   {change.reason}")
            print()
        return tailored_resume

    
    def name(self):
        return "AI Resume Populator"