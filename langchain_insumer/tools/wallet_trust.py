"""Tool for generating wallet trust fact profiles."""

import json
from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_insumer.wrapper import InsumerAPIWrapper


class WalletTrustSchema(BaseModel):
    """Input for InsumerWalletTrustTool."""

    wallet: str = Field(
        description="EVM wallet address (0x...) to profile.",
    )
    solana_wallet: Optional[str] = Field(
        default=None,
        description="Solana wallet address (base58). If provided, adds USDC on Solana check.",
    )
    proof: Optional[str] = Field(
        default=None,
        description=(
            'Set to "merkle" to include EIP-1186 Merkle storage proofs. '
            "Costs 6 credits instead of 3. Proofs available for stablecoin "
            "and governance checks on RPC chains."
        ),
    )


class InsumerWalletTrustTool(BaseTool):
    """Generate a structured, ECDSA-signed wallet trust fact profile.

    Checks 14 curated conditions across stablecoins (7 chains), governance
    tokens (4), and NFTs (3). Returns per-dimension pass/fail counts and
    overall summary. No score, no opinion — just cryptographically verifiable
    evidence. Costs 3 credits (standard) or 6 credits (with proof="merkle").
    """

    name: str = "insumer_wallet_trust"
    description: str = (
        "Generate a wallet trust fact profile across stablecoins, governance "
        "tokens, and NFTs. Send a wallet address, get 14 curated checks across "
        "7 chains organized by dimension. Returns ECDSA-signed evidence — no "
        "score, just facts. Use this when you need a comprehensive wallet "
        "assessment without specifying individual conditions. Costs 3 credits "
        '(standard) or 6 credits (proof="merkle").'
    )
    args_schema: Type[WalletTrustSchema] = WalletTrustSchema

    api_wrapper: InsumerAPIWrapper = Field(..., exclude=True)

    def __init__(self, api_wrapper: InsumerAPIWrapper) -> None:
        super().__init__(api_wrapper=api_wrapper)

    def _run(
        self,
        wallet: str,
        solana_wallet: Optional[str] = None,
        proof: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Generate the wallet trust fact profile."""
        result = self.api_wrapper.wallet_trust(
            wallet=wallet,
            solana_wallet=solana_wallet,
            proof=proof,
        )
        return json.dumps(result, indent=2)
