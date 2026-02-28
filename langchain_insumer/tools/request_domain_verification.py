"""Tool for requesting a domain verification token."""

import json
from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_insumer.wrapper import InsumerAPIWrapper


class RequestDomainVerificationSchema(BaseModel):
    """Input for InsumerRequestDomainVerificationTool."""

    merchant_id: str = Field(description="Merchant ID.")
    domain: str = Field(description="Domain to verify (e.g. 'example.com').")


class InsumerRequestDomainVerificationTool(BaseTool):
    """Request a domain verification token for a merchant.

    Returns the token and three verification methods: DNS TXT record,
    HTML meta tag, or file upload. After placing the token, call
    ``insumer_verify_domain`` to complete verification. Verified merchants
    get a trust badge in the public directory. Owner only.
    """

    name: str = "insumer_request_domain_verification"
    description: str = (
        "Request a domain verification token for a merchant. Returns the "
        "token and three verification methods (DNS TXT record, HTML meta tag, "
        "or file upload). After placing the token, call insumer_verify_domain "
        "to complete verification. Owner only."
    )
    args_schema: Type[RequestDomainVerificationSchema] = RequestDomainVerificationSchema

    api_wrapper: InsumerAPIWrapper = Field(..., exclude=True)

    def __init__(self, api_wrapper: InsumerAPIWrapper) -> None:
        super().__init__(api_wrapper=api_wrapper)

    def _run(
        self,
        merchant_id: str,
        domain: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Request domain verification token."""
        result = self.api_wrapper.request_domain_verification(
            merchant_id=merchant_id,
            domain=domain,
        )
        return json.dumps(result, indent=2)
