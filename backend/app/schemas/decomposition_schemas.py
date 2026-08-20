from typing import List, Optional
from pydantic import BaseModel, Field

class TaskSpec(BaseModel):
    title: str = Field(description="Title of the development task or story")
    component_type: str = Field(description="Type: 'ApexClass', 'ApexTrigger', 'LWC', 'ApexTest', or 'Config'")
    description: str = Field(description="Detailed technical description and specification for the developer agent")
    target_filename: str = Field(description="Suggested filename e.g. StudentRegistrationController.cls or studentRegistrationForm.js")

class DecompositionResult(BaseModel):
    epic_key: str = Field(description="The key of the Jira Epic")
    epic_summary: str = Field(description="Summary of the original Epic")
    architectural_overview: str = Field(description="High-level architecture & design plan")
    tasks: List[TaskSpec] = Field(description="List of decomposed stories and tasks")
    approval_token: Optional[str] = Field(default=None, description="Generated human approval token")

class HumanFeedbackRequest(BaseModel):
    pipeline_id: str
    stage: str
    action: str  # 'approve', 'request_changes', 'reject'
    feedback_text: Optional[str] = None
