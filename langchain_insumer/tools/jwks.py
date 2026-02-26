"""Tool for fetching the InsumerAPI JWKS (public signing key)."""

import json
from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_insumer.wrapper import InsumerAPIWrapper


class JwksSchema(BaseModel):
    """Input for InsumerJwksTool (no parameters required)."""

    pass


class InsumerJwksTool(BaseTool):
    """Fetch the JWKS containing InsumerAPI's ECDSA P-256 public signing key.

    The kid field in attestation responses identifies which key signed the
    response. Use this tool to fetch the public key for signature verification.
    No authentication required.
    """

    name: str = "insumer_jwks"
    description: str = (
        "Get the JWKS (JSON Web Key Set) containing InsumerAPI's ECDSA P-256 "
        "public signing key. Use the kid field from attestation responses to "
        "match the correct key. Enables signature verification and automatic "
        "key rotation. Free, no credits consumed."
    )
    args_schema: Type[JwksSchema] = JwksSchema

    api_wrapper: InsumerAPIWrapper = Field(..., exclude=True)

    def __init__(self, api_wrapper: InsumerAPIWrapper) -> None:
        super().__init__(api_wrapper=api_wrapper)

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Fetch the JWKS document."""
        result = self.api_wrapper.get_jwks()
        return json.dumps(result, indent=2)
