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
        description="Solana wallet address (base58). Adds USDC on Solana and institutional EURCV/USDCV on Solana checks.",
    )
    xrpl_wallet: Optional[str] = Field(
        default=None,
        description="XRPL wallet address (r-address). Adds RLUSD, USDC, and institutional EURCV on XRPL checks.",
    )
    bitcoin_wallet: Optional[str] = Field(
        default=None,
        description="Bitcoin address. Adds Bitcoin Holdings dimension (native BTC balance).",
    )
    tron_wallet: Optional[str] = Field(
        default=None,
        description="Tron wallet address (T-prefixed). Adds USDT-TRC20 on Tron check.",
    )
    stellar_wallet: Optional[str] = Field(
        default=None,
        description="Stellar wallet address (G-prefixed). Adds institutional USDC and BENJI on Stellar checks (classic trustlines).",
    )
    sui_wallet: Optional[str] = Field(
        default=None,
        description="Sui wallet address (0x + 64 hex). Adds institutional USDC on Sui check.",
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

    Checks 44 curated conditions across 25 chains in 5 dimensions: stablecoins
    (USDC + USDT, 26 checks), governance tokens (4), NFTs (3), staking positions
    (stETH, rETH, cbETH), and institutional stablecoins (8, across Ethereum,
    Solana, XRPL, Stellar, and Sui). Up to 49 checks across 27 chains in 9
    dimensions with optional Solana, XRPL, Bitcoin, Tron, Stellar, and Sui
    wallets. Checks whose chain wallet was not supplied carry evaluated: false
    and are counted in notEvaluatedCount, never as passed or failed.
    Returns per-dimension pass/fail counts and overall summary. No score, no
    opinion — just cryptographically verifiable evidence. Costs 3 credits
    (standard) or 6 credits (with proof="merkle").
    """

    name: str = "insumer_wallet_trust"
    description: str = (
        "Generate a wallet trust fact profile. 44 base checks across 25 chains "
        "in 5 dimensions: stablecoins (USDC + USDT), governance tokens (UNI, AAVE, "
        "ARB, OP), NFTs (BAYC, Pudgy Penguins, Wrapped CryptoPunks), staking "
        "positions (stETH, rETH, cbETH), and institutional stablecoins. Up to "
        "49 checks across 27 chains in 9 dimensions with optional Solana, XRPL, "
        "Bitcoin, Tron, Stellar, and Sui wallets; a check whose chain wallet was "
        "not supplied is reported as evaluated: false, not as a failure. "
        "Returns per-dimension pass/fail counts and ECDSA-signed evidence — no "
        "score, just facts. Use this when you need a comprehensive wallet "
        'assessment without specifying individual conditions. Costs 3 credits '
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
        xrpl_wallet: Optional[str] = None,
        bitcoin_wallet: Optional[str] = None,
        tron_wallet: Optional[str] = None,
        stellar_wallet: Optional[str] = None,
        sui_wallet: Optional[str] = None,
        proof: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Generate the wallet trust fact profile."""
        result = self.api_wrapper.wallet_trust(
            wallet=wallet,
            solana_wallet=solana_wallet,
            xrpl_wallet=xrpl_wallet,
            bitcoin_wallet=bitcoin_wallet,
            tron_wallet=tron_wallet,
            stellar_wallet=stellar_wallet,
            sui_wallet=sui_wallet,
            proof=proof,
        )
        return json.dumps(result, indent=2)
