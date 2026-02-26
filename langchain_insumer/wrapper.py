"""API wrapper for The Insumer Model On-Chain Verification API."""

from typing import Any, Optional

import requests
from pydantic import BaseModel, Field

BASE_URL = "https://us-central1-insumer-merchant.cloudfunctions.net/insumerApi/v1"


class InsumerAPIWrapper(BaseModel):
    """Wrapper around The Insumer Model API.

    Provides privacy-preserving on-chain verification and token-gated commerce
    across 31 blockchains. Verifies token balances and NFT ownership without
    exposing actual wallet balances.

    Args:
        api_key: API key in format ``insr_live_`` followed by 40 hex characters.
            Get a free key at https://insumermodel.com/developers/
        timeout: Request timeout in seconds. Default 30.
    """

    api_key: str = Field(description="Insumer API key (insr_live_...)")
    timeout: int = Field(default=30, description="Request timeout in seconds")

    def _headers(self) -> dict:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        resp = requests.get(
            f"{BASE_URL}{path}",
            headers=self._headers(),
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, json_body: Optional[dict] = None) -> dict:
        resp = requests.post(
            f"{BASE_URL}{path}",
            headers=self._headers(),
            json=json_body or {},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def attest(
        self,
        conditions: list[dict[str, Any]],
        wallet: Optional[str] = None,
        solana_wallet: Optional[str] = None,
        proof: Optional[str] = None,
    ) -> dict:
        """Create a privacy-preserving on-chain verification.

        Verifies 1-10 conditions (token balances, NFT ownership) and returns
        a cryptographically signed true/false result. Never exposes actual
        balances. Costs 1 verification credit (standard) or 2 credits (with
        proof="merkle").

        Args:
            conditions: List of condition dicts, each with:
                - type: "token_balance" or "nft_ownership"
                - contractAddress: Token/NFT contract address
                - chainId: EVM chain ID (int) or "solana"
                - threshold: Min balance (for token_balance)
                - decimals: Token decimals (default 18)
                - label: Human-readable label
            wallet: EVM wallet address (0x...)
            solana_wallet: Solana wallet address (base58)
            proof: Set to "merkle" for EIP-1186 Merkle storage proofs.
                Available for token_balance conditions on RPC chains only.
                Costs 2 credits. Reveals raw balance to the caller.

        Returns:
            API response with verification results and ECDSA signature.
            When proof="merkle", each result includes a proof object with
            accountProof, storageProof, storageHash, blockNumber, and
            mappingSlot fields.
        """
        body: dict[str, Any] = {"conditions": conditions}
        if wallet:
            body["wallet"] = wallet
        if solana_wallet:
            body["solanaWallet"] = solana_wallet
        if proof:
            body["proof"] = proof
        return self._post("/attest", body)

    def get_credits(self) -> dict:
        """Check verification credit balance for the API key."""
        return self._get("/credits")

    def list_merchants(
        self,
        token: Optional[str] = None,
        verified: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        """List merchants in the public directory."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if token:
            params["token"] = token
        if verified is not None:
            params["verified"] = str(verified).lower()
        return self._get("/merchants", params)

    def get_merchant(self, merchant_id: str) -> dict:
        """Get full public merchant profile with tier structures."""
        return self._get(f"/merchants/{merchant_id}")

    def list_tokens(
        self,
        chain: Optional[Any] = None,
        symbol: Optional[str] = None,
        asset_type: Optional[str] = None,
    ) -> dict:
        """List registered tokens and NFT collections."""
        params: dict[str, Any] = {}
        if chain is not None:
            params["chain"] = chain
        if symbol:
            params["symbol"] = symbol
        if asset_type:
            params["type"] = asset_type
        return self._get("/tokens", params)

    def check_discount(
        self,
        merchant_id: str,
        wallet: Optional[str] = None,
        solana_wallet: Optional[str] = None,
    ) -> dict:
        """Calculate discount for a wallet at a merchant. Free, no credits consumed."""
        params: dict[str, Any] = {"merchant": merchant_id}
        if wallet:
            params["wallet"] = wallet
        if solana_wallet:
            params["solanaWallet"] = solana_wallet
        return self._get("/discount/check", params)

    def verify(
        self,
        merchant_id: str,
        wallet: Optional[str] = None,
        solana_wallet: Optional[str] = None,
    ) -> dict:
        """Create a signed discount code (INSR-XXXXX), valid 30 minutes. Costs 1 credit."""
        body: dict[str, Any] = {"merchantId": merchant_id}
        if wallet:
            body["wallet"] = wallet
        if solana_wallet:
            body["solanaWallet"] = solana_wallet
        return self._post("/verify", body)
