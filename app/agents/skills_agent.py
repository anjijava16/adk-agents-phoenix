

import pathlib

from google.adk.agents import Agent

from app.config import get_settings
from app.logging import get_logger
from app.models import create_model
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

logger = get_logger(__name__)


def create_skills_agent(model_name: str | None = None) -> Agent:
    
    settings = get_settings()

    # Use provided model or fall back to primary model from settings
    if model_name is None:
        model_name = settings.primary_model

    logger.info(f"Creating Bitcoin agent with model '{model_name}'")

    model = create_model(model_name)

    weather_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "weather-skill"
)

    my_skill_toolset = skill_toolset.SkillToolset(
        skills=[weather_skill]
    )
    #logger.info(f"Loaded skills: {[skill.name for skill in my_skill_toolset.skills]}")

    root_agent = Agent(
        model=model,
        name="skill_user_agent",
        description="An agent that can use specialized skills.",
        instruction=(
            "You are a helpful assistant that can leverage skills to perform tasks."
        ),
        tools=[
            my_skill_toolset,
        ],
    )
    logger.info(f"skill_user_agent agent created successfully with model '{model_name}'")
    return root_agent