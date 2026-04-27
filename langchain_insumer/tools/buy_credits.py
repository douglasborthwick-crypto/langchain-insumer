"""Tool for buying verification credits with USDC, USDT, or BTC."""

import json
from typing import Any, Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_insumer.wrapper import InsumerAPIWrapper


class BuyCreditsSchema(BaseModel):
    """Input for InsumerBuyCreditsTool."""

    tx_hash: str = Field(description="Transaction hash of the USDC, USDT, or BTC payment to the platform wallet.")
    chain_id: Any = Field(
        description=(
            "Chain where payment was sent: 1 (Ethereum), 8453 (Base), "
            '137 (Polygon), 42161 (Arbitrum), 10 (Optimism), 56 (BNB), '
            '43114 (Avalanche), "solana", or "bitcoin".'
        ),
    )
    amount: float = Field(
        description="Stablecoin amount sent (min 5). Not required for BTC — USD value derived from on-chain BTC amount at market rate.",
        ge=5,
    )
    update_wallet: bool = Field(
        default=False,
        description="Set true to update the registered sender wallet to this transaction's sender.",
    )


class InsumerBuyCreditsTool(BaseTool):
    """Buy verification credits with USDC, USDT, or BTC.

    Rate: 25 credits per $1 ($0.04/credit). Minimum purchase: 5
    (125 credits). The server verifies the on-chain transaction receipt.
    """

    name: str = "insumer_buy_credits"
    description: str = (
        "Buy verification credits for the API key by submitting a USDC, "
        "USDT, or BTC transaction hash. Rate: 25 credits per $1. "
        "Minimum 5. Supports 7 EVM chains, Solana, and Bitcoin."
    )
    args_schema: Type[BuyCreditsSchema] = BuyCreditsSchema

    api_wrapper: InsumerAPIWrapper = Field(..., exclude=True)

    def __init__(self, api_wrapper: InsumerAPIWrapper) -> None:
        super().__init__(api_wrapper=api_wrapper)

    def _run(
        self,
        tx_hash: str,
        chain_id: Any,
        amount: float,
        update_wallet: bool = False,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Buy credits."""
        result = self.api_wrapper.buy_credits(
            tx_hash=tx_hash,
            chain_id=chain_id,
            amount=amount,
            update_wallet=update_wallet,
        )
        return json.dumps(result, indent=2)
