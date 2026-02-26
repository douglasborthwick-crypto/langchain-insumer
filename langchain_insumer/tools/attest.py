"""Tool for creating privacy-preserving on-chain verifications."""

import json
from typing import Any, Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_insumer.wrapper import InsumerAPIWrapper


class AttestSchema(BaseModel):
    """Input for InsumerAttestTool."""

    wallet: Optional[str] = Field(
        default=None,
        description="EVM wallet address (0x...) to verify.",
    )
    solana_wallet: Optional[str] = Field(
        default=None,
        description="Solana wallet address (base58) to verify.",
    )
    proof: Optional[str] = Field(
        default=None,
        description=(
            'Set to "merkle" to include EIP-1186 Merkle storage proofs in results. '
            "Proofs available for token_balance conditions on RPC chains "
            "(1, 56, 8453, 43114, 137, 42161, 10, 88888, 1868, 98866). "
            "Costs 2 credits instead of 1. Reveals raw balance to caller."
        ),
    )
    conditions: str = Field(
        description=(
            'JSON array of conditions. Each condition: {"type": "token_balance" or '
            '"nft_ownership", "contractAddress": "0x...", "chainId": 1, '
            '"threshold": 1000, "decimals": 6, "label": "USDC >= 1000"}. '
            "Supported chains: Ethereum (1), BNB (56), Base (8453), Polygon (137), "
            "Arbitrum (42161), Optimism (10), Avalanche (43114), Solana (\"solana\"), "
            "and 23 more. Max 10 conditions per call."
        ),
    )


class InsumerAttestTool(BaseTool):
    """Verify on-chain token balances or NFT ownership with a signed verification.

    Returns only true/false per condition -- never exposes actual balances.
    The response includes an ECDSA P-256 signature for cryptographic proof.
    Costs 1 verification credit per call, or 2 credits with proof="merkle".
    """

    name: str = "insumer_attest"
    description: str = (
        "Verify on-chain conditions (token balances, NFT ownership) across 31 "
        "blockchains. Returns a cryptographically signed true/false verification "
        "without exposing actual wallet balances. Use this when you need to check "
        "if a wallet holds a specific token or NFT. Costs 1 verification credit. "
        'Pass proof="merkle" for EIP-1186 Merkle storage proofs (2 credits).'
    )
    args_schema: Type[AttestSchema] = AttestSchema

    api_wrapper: InsumerAPIWrapper = Field(..., exclude=True)

    def __init__(self, api_wrapper: InsumerAPIWrapper) -> None:
        super().__init__(api_wrapper=api_wrapper)

    def _run(
        self,
        conditions: str,
        wallet: Optional[str] = None,
        solana_wallet: Optional[str] = None,
        proof: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the on-chain verification."""
        parsed_conditions: list[dict[str, Any]] = json.loads(conditions)
        result = self.api_wrapper.attest(
            conditions=parsed_conditions,
            wallet=wallet,
            solana_wallet=solana_wallet,
            proof=proof,
        )
        return json.dumps(result, indent=2)
