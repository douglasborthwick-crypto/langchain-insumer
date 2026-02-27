"""Tool for validating INSR-XXXXX discount codes."""

import json
from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_insumer.wrapper import InsumerAPIWrapper


class ValidateCodeSchema(BaseModel):
    """Input for InsumerValidateCodeTool."""

    code: str = Field(description="Discount code in INSR-XXXXX format.")


class InsumerValidateCodeTool(BaseTool):
    """Validate an INSR-XXXXX discount code.

    For merchant backends during ACP/UCP checkout to confirm code validity,
    discount percent, and expiry. No authentication required, no credits
    consumed. Does not expose wallet or token data.
    """

    name: str = "insumer_validate_code"
    description: str = (
        "Validate an INSR-XXXXX discount code. Returns valid/invalid status "
        "with merchant ID, discount percent, and expiry (if valid) or reason "
        "(if invalid: expired, already_used, not_found). No auth required, "
        "no credits consumed."
    )
    args_schema: Type[ValidateCodeSchema] = ValidateCodeSchema

    api_wrapper: InsumerAPIWrapper = Field(..., exclude=True)

    def __init__(self, api_wrapper: InsumerAPIWrapper) -> None:
        super().__init__(api_wrapper=api_wrapper)

    def _run(
        self,
        code: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Validate discount code."""
        result = self.api_wrapper.validate_code(code=code)
        return json.dumps(result, indent=2)
