"""Tool for getting a merchant's public profile."""

import json
from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_insumer.wrapper import InsumerAPIWrapper


class GetMerchantSchema(BaseModel):
    """Input for InsumerGetMerchantTool."""

    id: str = Field(description="Merchant ID to look up.")


class InsumerGetMerchantTool(BaseTool):
    """Get the full public profile of a merchant.

    Returns token tiers, NFT collections, discount mode, verification
    status, and location. No credits consumed.
    """

    name: str = "insumer_get_merchant"
    description: str = (
        "Get the full public profile of a specific merchant including token "
        "discount tiers, NFT collections, discount mode, and verification "
        "status. Use when you know the merchant ID and want details."
    )
    args_schema: Type[GetMerchantSchema] = GetMerchantSchema

    api_wrapper: InsumerAPIWrapper = Field(..., exclude=True)

    def __init__(self, api_wrapper: InsumerAPIWrapper) -> None:
        super().__init__(api_wrapper=api_wrapper)

    def _run(
        self,
        id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get merchant profile."""
        result = self.api_wrapper.get_merchant(merchant_id=id)
        return json.dumps(result, indent=2)
