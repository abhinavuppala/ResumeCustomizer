from pydantic import BaseModel
from abc import ABC, abstractmethod


# ==================================================
# ================== JSON Schemas ==================
# ==================================================


class Education(BaseModel):
    university: str
    location: str
    degree: str
    date: str
    bullets: list[str]


class Experience(BaseModel):
    title: str
    date: str
    company: str
    location: str
    bullets: list[str]


class Project(BaseModel):
    title: str
    skills: str
    bullets: list[str]


class Skills(BaseModel):
    sections: dict[str, str]


class Resume(BaseModel):
    education: Education
    experiences: list[Experience]
    projects: list[Project]
    skills: Skills


class ChangeLog(BaseModel):
    before: str
    after: str
    reason: str

class ResumeCustomizationResult(BaseModel):
    resume: Resume
    changelog: list[ChangeLog]


# ==================================================
# ============= Latex String Templates =============
# ==================================================


EDUCATION_LATEX = """
\\section{{Education}}
  \\resumeSubHeadingListStart
    \\resumeSubheading
      {{{university}}}{{{location}}}
      {{{degree}}}{{{date}}}
      \\resumeItemListStart
        {bullets_str}
      \\resumeItemListEnd
  \\resumeSubHeadingListEnd
"""

EXPERIENCE_LATEX = """
\\resumeSubheading
  {{{title}}}{{{date}}}
  {{{company}}}{{{location}}}
  \\resumeItemListStart
    {bullets_str}
  \\resumeItemListEnd
"""

PROJECT_LATEX = """
\\resumeProjectHeading
  {{\\textbf{{{title}}} $|$ \\emph{{{skills}}}}}{{}}
  \\resumeItemListStart
    {bullets_str}
  \\resumeItemListEnd
"""

SKILLS_LATEX = """
\\section{{Skills}}
 \\begin{{itemize}}[leftmargin=0.15in, label={{}}]
    \\small{{\\item{{
{sections_str}
    }}}}
 \\end{{itemize}}
"""

# ==================================================
# === Class to convert BaseModel -> latex string === 
# ==================================================


class ComponentCompiler:
    
    @staticmethod
    def compile_education(education: Education) -> str:
        """
        :return: Latex string of the education section (Jake's Resume)
        """
        return EDUCATION_LATEX.format(
            university=education.university,
            location=education.location,
            degree=education.degree,
            date=education.date,
            bullets_str="\n".join(
                "\\resumeItem{"+bullet+'}' for bullet in education.bullets
            )
        )

    @staticmethod
    def compile_experience(experience: Experience) -> str:
        """
        :return: Latex string of one experience section (Jake's Resume)
        """
        return EXPERIENCE_LATEX.format(
            title=experience.title,
            date=experience.date,
            company=experience.company,
            location=experience.location,
            bullets_str="\n".join(
                f"\\resumeItem{{{bullet}}}" for bullet in experience.bullets
            )
        )

    @staticmethod
    def compile_project(project: Project) -> str:
        """
        :return: Latex string of one project section (Jake's Resume)
        """
        return PROJECT_LATEX.format(
            title=project.title,
            skills=project.skills,
            bullets_str="\n".join(
                f"\\resumeItem{{{bullet}}}" for bullet in project.bullets
            )
        )

    @staticmethod
    def compile_skills(skills: Skills) -> str:
        """
        :return: Latex string of the skills section (Jake's Resume)
        """
        sections_str = " \\\\\n".join(
            f"\\textbf{{{section}}}{{: {items}}}" for section, items in skills.sections.items()
        )
        return SKILLS_LATEX.format(sections_str=sections_str)
    

# ==================================================
# =================== Interfaces ===================
# ==================================================


class BaseResumeFieldPopulator(ABC):
    @abstractmethod
    def get_resume_data(self, job_info: str) -> tuple[Resume, list[ChangeLog]]:
        pass

    @abstractmethod
    def name(self) -> str:
        pass


class BaseAIInterface(ABC):
    @abstractmethod
    def generate_customized_resume(
        self,
        base_resume: Resume,
        job_info: str
    ) -> ResumeCustomizationResult:
        pass

    @abstractmethod
    def name(self) -> str:
        pass