"""Tool for checking verification credit balance."""

import json
from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_insumer.wrapper import InsumerAPIWrapper


class CreditsSchema(BaseModel):
    """Input for InsumerCreditsTool. No parameters required."""

    pass


class InsumerCreditsTool(BaseTool):
    """Check the verification credit balance for the current API key."""

    name: str = "insumer_credits"
    description: str = (
        "Check the verification credit balance, tier, and daily rate limit "
        "for the current Insumer API key. No parameters needed."
    )
    args_schema: Type[CreditsSchema] = CreditsSchema

    api_wrapper: InsumerAPIWrapper = Field(..., exclude=True)

    def __init__(self, api_wrapper: InsumerAPIWrapper) -> None:
        super().__init__(api_wrapper=api_wrapper)

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Check credits."""
        result = self.api_wrapper.get_credits()
        return json.dumps(result, indent=2)
