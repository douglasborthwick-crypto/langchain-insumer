"""Tool for listing merchants in the public directory."""

import json
from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_insumer.wrapper import InsumerAPIWrapper


class ListMerchantsSchema(BaseModel):
    """Input for InsumerListMerchantsTool."""

    token: Optional[str] = Field(
        default=None,
        description="Filter by accepted token symbol (e.g. UNI, SHIB).",
    )
    verified: Optional[bool] = Field(
        default=None,
        description="Filter by domain verification status.",
    )
    limit: int = Field(
        default=50,
        le=200,
        description="Results per page (max 200).",
    )
    offset: int = Field(
        default=0,
        description="Pagination offset.",
    )


class InsumerListMerchantsTool(BaseTool):
    """Browse merchants that offer token-gated discounts."""

    name: str = "insumer_list_merchants"
    description: str = (
        "List merchants in The Insumer Model directory that offer discounts "
        "to token holders. Optionally filter by accepted token symbol or "
        "verification status. Returns merchant names, locations, accepted "
        "tokens, and discount structures."
    )
    args_schema: Type[ListMerchantsSchema] = ListMerchantsSchema

    api_wrapper: InsumerAPIWrapper = Field(..., exclude=True)

    def __init__(self, api_wrapper: InsumerAPIWrapper) -> None:
        super().__init__(api_wrapper=api_wrapper)

    def _run(
        self,
        token: Optional[str] = None,
        verified: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """List merchants."""
        result = self.api_wrapper.list_merchants(
            token=token,
            verified=verified,
            limit=limit,
            offset=offset,
        )
        return json.dumps(result, indent=2)
