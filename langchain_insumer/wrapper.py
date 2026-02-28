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

    def _put(self, path: str, json_body: Optional[dict] = None) -> dict:
        resp = requests.put(
            f"{BASE_URL}{path}",
            headers=self._headers(),
            json=json_body or {},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def get_jwks(self) -> dict:
        """Get the JWKS containing InsumerAPI's ECDSA P-256 public signing key.

        No authentication required. The ``kid`` field matches the ``kid`` in
        attestation responses, enabling automatic key rotation.

        Returns:
            JWKS document with the public signing key.
        """
        resp = requests.get(
            f"{BASE_URL}/jwks",
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def get_compliance_templates(self) -> dict:
        """List available compliance templates for EAS attestation verification.

        Returns pre-configured templates for KYC/identity providers (e.g.
        Coinbase Verifications on Base). No authentication required.

        Returns:
            Template catalog with provider, description, chainId, and chainName.
        """
        resp = requests.get(
            f"{BASE_URL}/compliance/templates",
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

        Verifies 1-10 conditions (token balances, NFT ownership, EAS
        attestations) and returns a cryptographically signed true/false result.
        Never exposes actual balances. Costs 1 verification credit (standard)
        or 2 credits (with proof="merkle").

        Args:
            conditions: List of condition dicts, each with:
                - type: "token_balance", "nft_ownership", "eas_attestation", or "farcaster_id"
                - contractAddress: Token/NFT contract address (for token_balance/nft_ownership)
                - chainId: EVM chain ID (int) or "solana"
                - threshold: Min balance (for token_balance)
                - decimals: Token decimals (default 18)
                - label: Human-readable label
                - template: Compliance template name (for eas_attestation, e.g.
                  "coinbase_verified_account", "gitcoin_passport_score", "gitcoin_passport_active")
                - schemaId: EAS schema ID (for eas_attestation, if not using template)
                - attester: Expected attester address (optional, for eas_attestation)
                - indexer: EAS indexer contract (optional, for eas_attestation)
            wallet: EVM wallet address (0x...)
            solana_wallet: Solana wallet address (base58)
            proof: Set to "merkle" for EIP-1186 Merkle storage proofs.
                Available for token_balance conditions on RPC chains only.
                Costs 2 credits. Reveals raw balance to the caller.

        Returns:
            API response with verification results, ECDSA signature (``sig``),
            and key ID (``kid``) identifying the signing key. Fetch the public
            key via ``get_jwks()`` to verify signatures.
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

    def wallet_trust(
        self,
        wallet: str,
        solana_wallet: Optional[str] = None,
        proof: Optional[str] = None,
    ) -> dict:
        """Generate a structured wallet trust fact profile.

        Checks 17 curated conditions across stablecoins (7 chains), governance
        tokens (4), NFTs (3), and staking positions (stETH, rETH, cbETH).
        Returns per-dimension pass/fail counts and an overall summary. No score
        — just cryptographically verifiable evidence. Costs 3 credits (standard)
        or 6 credits (with proof="merkle").

        Args:
            wallet: EVM wallet address (0x...) to profile.
            solana_wallet: Solana wallet address (base58). If provided, adds
                USDC on Solana check (18th check).
            proof: Set to "merkle" for EIP-1186 Merkle storage proofs on
                stablecoin and governance checks. Costs 6 credits.

        Returns:
            API response with trust profile, ECDSA signature (``sig``),
            and key ID (``kid``).
        """
        body: dict[str, Any] = {"wallet": wallet}
        if solana_wallet:
            body["solanaWallet"] = solana_wallet
        if proof:
            body["proof"] = proof
        return self._post("/trust", body)

    def batch_wallet_trust(
        self,
        wallets: list[dict[str, Any]],
        proof: Optional[str] = None,
    ) -> dict:
        """Generate wallet trust fact profiles for up to 10 wallets in one request.

        Shared block fetches make this 5-8x faster than sequential
        ``wallet_trust()`` calls. Each wallet gets an independently
        ECDSA-signed profile. Supports partial success — failed wallets get
        error entries while successful ones return full profiles. Credits
        only charged for successful profiles.

        Args:
            wallets: List of 1-10 dicts, each with ``wallet`` (EVM address,
                required) and optional ``solanaWallet`` (base58).
            proof: Set to ``"merkle"`` for EIP-1186 Merkle storage proofs.
                Costs 6 credits per wallet instead of 3.

        Returns:
            API response with ``results`` array (success/error entries),
            ``summary`` (requested/succeeded/failed counts), and ``meta``
            (creditsCharged, creditsRemaining).
        """
        body: dict[str, Any] = {"wallets": wallets}
        if proof:
            body["proof"] = proof
        return self._post("/trust/batch", body)

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

    def buy_credits(
        self,
        tx_hash: str,
        chain_id: Any,
        amount: float,
    ) -> dict:
        """Buy verification credits with USDC. Rate: 25 credits per 1 USDC. Minimum 5 USDC."""
        return self._post("/credits/buy", {
            "txHash": tx_hash,
            "chainId": chain_id,
            "amount": amount,
        })

    def confirm_payment(
        self,
        code: str,
        tx_hash: str,
        chain_id: Any,
        amount: Any,
    ) -> dict:
        """Confirm USDC payment for a discount code. Server verifies the transaction."""
        return self._post("/payment/confirm", {
            "code": code,
            "txHash": tx_hash,
            "chainId": chain_id,
            "amount": amount,
        })

    def create_merchant(
        self,
        company_name: str,
        company_id: str,
        location: Optional[str] = None,
    ) -> dict:
        """Create a new merchant. Receives 100 free verification credits. Max 10 per API key."""
        body: dict[str, Any] = {
            "companyName": company_name,
            "companyId": company_id,
        }
        if location:
            body["location"] = location
        return self._post("/merchants", body)

    def get_merchant_status(self, merchant_id: str) -> dict:
        """Get full private merchant details: credits, configs, directory status. Owner only."""
        return self._get(f"/merchants/{merchant_id}/status")

    def configure_tokens(
        self,
        merchant_id: str,
        own_token: Optional[dict] = None,
        partner_tokens: Optional[list] = None,
    ) -> dict:
        """Configure merchant token discount tiers. Max 8 tokens total. Owner only."""
        body: dict[str, Any] = {}
        if own_token is not None:
            body["ownToken"] = own_token
        if partner_tokens is not None:
            body["partnerTokens"] = partner_tokens
        return self._put(f"/merchants/{merchant_id}/tokens", body)

    def configure_nfts(
        self,
        merchant_id: str,
        nft_collections: list,
    ) -> dict:
        """Configure NFT collections that grant discounts. Max 4 collections. Owner only."""
        return self._put(f"/merchants/{merchant_id}/nfts", {
            "nftCollections": nft_collections,
        })

    def configure_settings(
        self,
        merchant_id: str,
        discount_mode: Optional[str] = None,
        discount_cap: Optional[int] = None,
        usdc_payment: Optional[dict] = None,
    ) -> dict:
        """Update merchant settings: discount mode, cap, USDC payments. Owner only."""
        body: dict[str, Any] = {}
        if discount_mode is not None:
            body["discountMode"] = discount_mode
        if discount_cap is not None:
            body["discountCap"] = discount_cap
        if usdc_payment is not None:
            body["usdcPayment"] = usdc_payment
        return self._put(f"/merchants/{merchant_id}/settings", body)

    def publish_directory(self, merchant_id: str) -> dict:
        """Publish or refresh merchant listing in the public directory. Owner only."""
        return self._post(f"/merchants/{merchant_id}/directory", {})

    def buy_merchant_credits(
        self,
        merchant_id: str,
        tx_hash: str,
        chain_id: Any,
        amount: float,
    ) -> dict:
        """Buy merchant verification credits with USDC. Rate: 25 credits per 1 USDC. Min 5 USDC. Owner only."""
        return self._post(f"/merchants/{merchant_id}/credits", {
            "txHash": tx_hash,
            "chainId": chain_id,
            "amount": amount,
        })

    def acp_discount(
        self,
        merchant_id: str,
        wallet: Optional[str] = None,
        solana_wallet: Optional[str] = None,
        items: Optional[list] = None,
    ) -> dict:
        """Check discount eligibility in ACP (OpenAI/Stripe Agentic Commerce Protocol) format.

        Returns coupon objects, applied/rejected arrays, and per-item allocations
        compatible with ACP checkout flows. Same verification as ``verify()``,
        wrapped in ACP format. Costs 1 merchant credit.

        Args:
            merchant_id: Merchant identifier.
            wallet: EVM wallet address (0x...).
            solana_wallet: Solana wallet address (base58).
            items: Optional line items for per-item allocations. Each dict has
                ``path`` (JSONPath, e.g. '$.line_items[0]') and ``amount`` (cents).

        Returns:
            ACP-format response with discounts.applied, discounts.rejected,
            coupon objects, and ECDSA-signed verification block.
        """
        body: dict[str, Any] = {"merchantId": merchant_id}
        if wallet:
            body["wallet"] = wallet
        if solana_wallet:
            body["solanaWallet"] = solana_wallet
        if items is not None:
            body["items"] = items
        return self._post("/acp/discount", body)

    def ucp_discount(
        self,
        merchant_id: str,
        wallet: Optional[str] = None,
        solana_wallet: Optional[str] = None,
        items: Optional[list] = None,
    ) -> dict:
        """Check discount eligibility in UCP (Google Universal Commerce Protocol) format.

        Returns title, extension field, and applied array compatible with UCP
        checkout flows. Same verification as ``verify()``, wrapped in UCP format.
        Costs 1 merchant credit.

        Args:
            merchant_id: Merchant identifier.
            wallet: EVM wallet address (0x...).
            solana_wallet: Solana wallet address (base58).
            items: Optional line items for per-item allocations. Each dict has
                ``path`` (JSONPath, e.g. '$.line_items[0]') and ``amount`` (cents).

        Returns:
            UCP-format response with discounts.applied, extension field,
            and ECDSA-signed verification block.
        """
        body: dict[str, Any] = {"merchantId": merchant_id}
        if wallet:
            body["wallet"] = wallet
        if solana_wallet:
            body["solanaWallet"] = solana_wallet
        if items is not None:
            body["items"] = items
        return self._post("/ucp/discount", body)

    def request_domain_verification(
        self,
        merchant_id: str,
        domain: str,
    ) -> dict:
        """Request a domain verification token for a merchant.

        Returns a token and three verification methods (DNS TXT record,
        HTML meta tag, or file upload). After placing the token, call
        ``verify_domain()`` to complete verification. Owner only.

        Args:
            merchant_id: Merchant identifier.
            domain: Domain to verify (e.g. 'example.com').

        Returns:
            Verification token and instructions for all three methods.
        """
        return self._post(f"/merchants/{merchant_id}/domain-verification", {
            "domain": domain,
        })

    def verify_domain(self, merchant_id: str) -> dict:
        """Verify domain ownership for a merchant.

        Call after placing the verification token (from
        ``request_domain_verification()``) via DNS TXT, meta tag, or file.
        The server checks all three methods automatically. Rate limited
        to 5 attempts per hour. Owner only.

        Args:
            merchant_id: Merchant identifier.

        Returns:
            Verification result with ``verified`` (bool), ``domain``,
            and ``method`` (if successful) or ``attemptsRemaining``.
        """
        return self._put(f"/merchants/{merchant_id}/domain-verification")

    def validate_code(self, code: str) -> dict:
        """Validate an INSR-XXXXX discount code.

        For merchant backends during ACP/UCP checkout to confirm code validity,
        discount percent, and expiry. No authentication required, no credits
        consumed. Does not expose wallet or token data.

        Args:
            code: Discount code in INSR-XXXXX format.

        Returns:
            Validation result with ``valid`` (bool), ``code``, and either
            merchant/discount details (if valid) or ``reason`` (if invalid).
        """
        resp = requests.get(
            f"{BASE_URL}/codes/{code}",
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()
