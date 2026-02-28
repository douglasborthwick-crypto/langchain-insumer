"""Tool for listing available compliance templates."""

import json
from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_insumer.wrapper import InsumerAPIWrapper


class ComplianceTemplatesSchema(BaseModel):
    """Input for InsumerComplianceTemplatesTool (no parameters required)."""

    pass


class InsumerComplianceTemplatesTool(BaseTool):
    """List available compliance templates for EAS attestation verification.

    Templates provide pre-configured schema IDs, attester addresses, and
    decoder contracts for KYC/identity providers (Coinbase Verifications on
    Base, Gitcoin Passport on Optimism). No authentication or credits required.
    """

    name: str = "insumer_compliance_templates"
    description: str = (
        "List available compliance templates for EAS attestation verification. "
        "Templates provide pre-configured schema IDs for KYC/identity providers "
        "(Coinbase Verifications on Base, Gitcoin Passport on Optimism). Use a "
        "template name in insumer_attest conditions instead of raw EAS parameters. "
        "No authentication or credits required."
    )
    args_schema: Type[ComplianceTemplatesSchema] = ComplianceTemplatesSchema

    api_wrapper: InsumerAPIWrapper = Field(..., exclude=True)

    def __init__(self, api_wrapper: InsumerAPIWrapper) -> None:
        super().__init__(api_wrapper=api_wrapper)

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """List compliance templates."""
        result = self.api_wrapper.get_compliance_templates()
        return json.dumps(result, indent=2)
