"""Tool for publishing a merchant to the public directory."""

import json
from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_insumer.wrapper import InsumerAPIWrapper


class PublishDirectorySchema(BaseModel):
    """Input for InsumerPublishDirectoryTool."""

    id: str = Field(description="Merchant ID to publish.")


class InsumerPublishDirectoryTool(BaseTool):
    """Publish or refresh a merchant listing in the public directory. Owner only.

    Call this after creating a merchant and configuring tokens/NFTs/settings.
    Call again after any configuration change to refresh the listing.
    """

    name: str = "insumer_publish_directory"
    description: str = (
        "Publish or refresh a merchant's listing in the public directory. "
        "Call after creating a merchant and configuring tokens, NFTs, or "
        "settings. Call again after any update to refresh. Owner only."
    )
    args_schema: Type[PublishDirectorySchema] = PublishDirectorySchema

    api_wrapper: InsumerAPIWrapper = Field(..., exclude=True)

    def __init__(self, api_wrapper: InsumerAPIWrapper) -> None:
        super().__init__(api_wrapper=api_wrapper)

    def _run(
        self,
        id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Publish to directory."""
        result = self.api_wrapper.publish_directory(merchant_id=id)
        return json.dumps(result, indent=2)
