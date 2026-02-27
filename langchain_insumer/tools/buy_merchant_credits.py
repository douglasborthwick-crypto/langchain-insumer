"""Tool for buying merchant-specific verification credits with USDC."""

import json
from typing import Any, Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_insumer.wrapper import InsumerAPIWrapper


class BuyMerchantCreditsSchema(BaseModel):
    """Input for InsumerBuyMerchantCreditsTool."""

    id: str = Field(description="Merchant ID to buy credits for.")
    tx_hash: str = Field(description="USDC transaction hash.")
    chain_id: Any = Field(
        description=(
            "Chain where USDC was sent: 1 (Ethereum), 8453 (Base), "
            '137 (Polygon), 42161 (Arbitrum), 10 (Optimism), 56 (BNB), '
            '43114 (Avalanche), or "solana".'
        ),
    )
    amount: float = Field(
        description="USDC amount sent. Minimum 5.",
        ge=5,
    )


class InsumerBuyMerchantCreditsTool(BaseTool):
    """Buy verification credits for a specific merchant with USDC. Owner only.

    Rate: 25 credits per 1 USDC ($0.04/credit). Minimum 5 USDC.
    Merchant credits are separate from API key credits.
    """

    name: str = "insumer_buy_merchant_credits"
    description: str = (
        "Buy verification credits for a specific merchant by submitting a "
        "USDC transaction hash. Rate: 25 credits per 1 USDC. Minimum "
        "5 USDC. Owner only. Merchant credits are separate from API key credits."
    )
    args_schema: Type[BuyMerchantCreditsSchema] = BuyMerchantCreditsSchema

    api_wrapper: InsumerAPIWrapper = Field(..., exclude=True)

    def __init__(self, api_wrapper: InsumerAPIWrapper) -> None:
        super().__init__(api_wrapper=api_wrapper)

    def _run(
        self,
        id: str,
        tx_hash: str,
        chain_id: Any,
        amount: float,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Buy merchant credits."""
        result = self.api_wrapper.buy_merchant_credits(
            merchant_id=id,
            tx_hash=tx_hash,
            chain_id=chain_id,
            amount=amount,
        )
        return json.dumps(result, indent=2)
