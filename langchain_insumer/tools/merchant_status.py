"""Tool for getting private merchant status."""

import json
from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_insumer.wrapper import InsumerAPIWrapper


class MerchantStatusSchema(BaseModel):
    """Input for InsumerMerchantStatusTool."""

    id: str = Field(description="Merchant ID to check status for.")


class InsumerMerchantStatusTool(BaseTool):
    """Get full private merchant details. Owner only.

    Returns credits, token configurations, NFT collections, directory
    status, verification status, and USDC payment settings.
    """

    name: str = "insumer_merchant_status"
    description: str = (
        "Get full private merchant details: credits remaining, token configs, "
        "NFT collections, directory publication status, domain verification "
        "status, and USDC payment settings. Owner only."
    )
    args_schema: Type[MerchantStatusSchema] = MerchantStatusSchema

    api_wrapper: InsumerAPIWrapper = Field(..., exclude=True)

    def __init__(self, api_wrapper: InsumerAPIWrapper) -> None:
        super().__init__(api_wrapper=api_wrapper)

    def _run(
        self,
        id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get merchant status."""
        result = self.api_wrapper.get_merchant_status(merchant_id=id)
        return json.dumps(result, indent=2)
