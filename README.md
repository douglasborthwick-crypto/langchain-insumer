# langchain-insumer

LangChain tools for [InsumerAPI](https://insumermodel.com/developers/) -- wallet auth across 33 blockchains. Returns ECDSA-signed booleans without exposing wallet balances. Up to 10 conditions per request, each with its own chainId. Optional Merkle storage proofs for trustless verification.

**In production:** [DJD Agent Score](https://github.com/jacobsd32-cpu/djdagentscore) (Coinbase x402 ecosystem) uses InsumerAPI for AI agent wallet trust scoring. [Case study](https://insumermodel.com/blog/djd-agent-score-insumer-api-integration.html).

Also available as: [MCP server](https://www.npmjs.com/package/mcp-server-insumer) (26 tools, npm) | [ElizaOS](https://www.npmjs.com/package/eliza-plugin-insumer) (10 actions, npm) | [OpenAI GPT](https://chatgpt.com/g/g-699c5e43ce2481918b3f1e7f144c8a49-insumerapi-verify) (GPT Store) | [insumer-verify](https://www.npmjs.com/package/insumer-verify) (client-side verification, npm)

**[Full AI Agent Verification API guide](https://insumermodel.com/ai-agent-verification-api/)** — covers all 33 chains, trust profiles, commerce protocols, and signature verification.

## Install

```bash
pip install langchain-insumer
```

## Get an API Key

```bash
curl -X POST \
  https://api.insumermodel.com/v1/keys/create \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "appName": "my-agent", "tier": "free"}'
```

Returns an `insr_live_...` key instantly with 10 verification credits. Or get one at [insumermodel.com/developers](https://insumermodel.com/developers/#pricing).

## Quick Start

```python
from langchain_insumer import InsumerAPIWrapper

api = InsumerAPIWrapper(api_key="insr_live_your_key_here")

# Verify a wallet holds >= 1000 USDC on Ethereum
result = api.attest(
    wallet="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    conditions=[
        {
            "type": "token_balance",
            "contractAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "chainId": 1,
            "threshold": 1000,
            "decimals": 6,
            "label": "USDC >= 1000 on Ethereum",
        }
    ],
)

attestation = result["data"]["attestation"]
print(f"Pass: {attestation['pass']}")
for r in attestation["results"]:
    print(f"  {r['label']}: {'met' if r['met'] else 'not met'}")
print(f"Signature: {result['data']['sig']}")
print(f"Key ID: {result['data']['kid']}")
```

### What you get back

```json
{
  "ok": true,
  "data": {
    "attestation": {
      "id": "ATST-A7C3E1B2D4F56789",
      "pass": true,
      "results": [
        {
          "condition": 0,
          "met": true,
          "label": "USDC >= 1000 on Ethereum",
          "type": "token_balance",
          "chainId": 1,
          "evaluatedCondition": {
            "chainId": 1,
            "contractAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "decimals": 6,
            "operator": "gte",
            "threshold": 1000,
            "type": "token_balance"
          },
          "conditionHash": "0x554251734232c8b43062f1cf2bb51b76650d13268104d74c645f4893e67ef69c",
          "blockNumber": "0x129e3f7",
          "blockTimestamp": "2026-02-28T12:34:56.000Z"
        }
      ],
      "passCount": 1,
      "failCount": 0,
      "attestedAt": "2026-02-28T12:34:57.000Z",
      "expiresAt": "2026-02-28T13:04:57.000Z"
    },
    "sig": "dmNJKqnGZ9f47qpWax9gxgw1DhUKHKHrbLspTop8NWzYhv2fNpVAt1gAuhUfU4xPsgXTCdrmTXI4vEE50dcfEA==",
    "kid": "insumer-attest-v1"
  },
  "meta": { "version": "1.0", "timestamp": "2026-02-28T12:34:57.000Z", "creditsRemaining": 99, "creditsCharged": 1 }
}
```

No balances. No amounts. Just a signed true/false per condition.

### Wallet Auth (JWT)

Add `format="jwt"` to receive the attestation as a standard JWT bearer token:

```python
result = api.attest(
    wallet="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    conditions=[...],
    format="jwt"
)

print(result["data"]["jwt"])  # ES256-signed JWT
```

The response includes an additional `jwt` field. This token is verifiable by any standard JWT library via the JWKS endpoint at `GET /v1/jwks` — compatible with Kong, Nginx, Cloudflare Access, AWS API Gateway, and other JWT middleware.

### XRPL Verification

```python
# Verify native XRP balance
result = api.attest(
    xrpl_wallet="rG1QQv2nh2gr7RCZ1P8YYcBUKCCN633jCn",
    conditions=[
        {
            "type": "token_balance",
            "contractAddress": "native",
            "chainId": "xrpl",
            "threshold": 100,
            "label": "XRP >= 100",
        }
    ],
)

# Verify RLUSD trust line token
result = api.attest(
    xrpl_wallet="rG1QQv2nh2gr7RCZ1P8YYcBUKCCN633jCn",
    conditions=[
        {
            "type": "token_balance",
            "contractAddress": "rMxCKbEDwqr76QuheSUMdEGf4B9xJ8m5De",
            "chainId": "xrpl",
            "currency": "RLUSD",
            "threshold": 10,
            "label": "RLUSD >= 10 on XRPL",
        }
    ],
)

# Wallet trust profile with XRPL dimensions
result = api.wallet_trust(
    wallet="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    xrpl_wallet="rG1QQv2nh2gr7RCZ1P8YYcBUKCCN633jCn",
)
```

XRPL attestation results include `ledgerIndex` and `ledgerHash` (validated ledger hash) instead of `blockNumber`/`blockTimestamp`. Trust line token results also include `trustLineState: { frozen: bool }` — a frozen trust line causes `met: false` regardless of balance. Native XRP results include `ledgerHash` but not `trustLineState`.

## Verify the Response

The attestation is ECDSA-signed. Your application should verify it before trusting it. Use [insumer-verify](https://www.npmjs.com/package/insumer-verify) in your Node.js backend or browser:

```bash
npm install insumer-verify
```

```typescript
import { verifyAttestation } from "insumer-verify";

// attestationResponse = the full API envelope {ok, data: {attestation, sig, kid}, meta}
// Do NOT pass attestationResponse.data — the function expects the outer envelope
const result = await verifyAttestation(attestationResponse, {
  jwksUrl: "https://insumermodel.com/.well-known/jwks.json",
  maxAge: 120,
});

if (result.valid) {
  // Signature verified, condition hashes match, not expired
  console.log("Attestation verified");
} else {
  console.log("Verification failed:", result.checks);
}
```

This verifies the ECDSA P-256 signature, condition hash integrity, block freshness, and attestation expiry. The signing key is fetched from the JWKS endpoint and matched by `kid`, so it handles key rotation automatically.

## With a LangChain Agent

```python
from langchain_insumer import InsumerAPIWrapper, InsumerAttestTool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

api = InsumerAPIWrapper(api_key="insr_live_your_key_here")
tools = [InsumerAttestTool(api_wrapper=api)]

llm = ChatOpenAI(model="gpt-4o")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You verify on-chain token holdings using InsumerAPI."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
result = executor.invoke({"input": "Does vitalik.eth hold at least 100 USDC on Ethereum?"})
print(result["output"])
```

## Available Tools (26)

### Verification

| Tool | Description | Credits |
|------|-------------|---------|
| `InsumerAttestTool` | Verify on-chain conditions (token balances, NFT ownership, EAS attestations, Farcaster identity). Optional `proof="merkle"` for EIP-1186 Merkle proofs. | 1/call (2 with merkle) |
| `InsumerComplianceTemplatesTool` | List available EAS compliance templates (Coinbase Verifications on Base, Gitcoin Passport on Optimism). | Free |
| `InsumerWalletTrustTool` | Generate wallet trust fact profile (36 base checks, 4 dimensions; up to 40 across 7 dimensions with optional Solana, XRPL, and Bitcoin). | 3/call (6 with merkle) |
| `InsumerBatchWalletTrustTool` | Batch trust profiles for up to 10 wallets. 5-8x faster. Each wallet can include optional `solanaWallet` and `xrplWallet`. | 3/wallet (6 with merkle) |
| `InsumerVerifyTool` | Create signed discount code (INSR-XXXXX), valid 30 min. | 1/call |
| `InsumerConfirmPaymentTool` | Confirm USDC payment for a discount code. | Free |
| `InsumerJwksTool` | Get ECDSA P-256 public signing key (JWKS). | Free |

### Discovery

| Tool | Description | Credits |
|------|-------------|---------|
| `InsumerListMerchantsTool` | Browse merchant directory, filter by token/status. | Free |
| `InsumerGetMerchantTool` | Get full public merchant profile with tier structures. | Free |
| `InsumerListTokensTool` | List registered tokens and NFTs, filter by chain/symbol. | Free |
| `InsumerCheckDiscountTool` | Calculate discount for a wallet at a merchant. | Free |

### Credits

| Tool | Description | Credits |
|------|-------------|---------|
| `InsumerBuyKeyTool` | Buy a new API key with USDC, USDT, or BTC (no auth required). Wallet becomes identity. | -- |
| `InsumerCreditsTool` | Check API key credit balance and tier. | Free |
| `InsumerBuyCreditsTool` | Buy API key credits with USDC, USDT, or BTC (25 credits/$1). | -- |
| `InsumerBuyMerchantCreditsTool` | Buy merchant credits with USDC, USDT, or BTC (25 credits/$1). | -- |

### Merchant Onboarding

| Tool | Description | Credits |
|------|-------------|---------|
| `InsumerCreateMerchantTool` | Create a new merchant (100 free credits). | Free |
| `InsumerMerchantStatusTool` | Get private merchant details (owner only). | Free |
| `InsumerConfigureTokensTool` | Configure token discount tiers (max 8 tokens). | Free |
| `InsumerConfigureNftsTool` | Configure NFT collection discounts (max 4). | Free |
| `InsumerConfigureSettingsTool` | Update discount mode, cap, USDC payments. | Free |
| `InsumerPublishDirectoryTool` | Publish merchant to public directory. | Free |

### Domain Verification

| Tool | Description | Credits |
|------|-------------|---------|
| `InsumerRequestDomainVerificationTool` | Request a verification token for a merchant's domain. Returns token and 3 methods (DNS TXT, meta tag, file upload). | Free |
| `InsumerVerifyDomainTool` | Complete domain verification after placing the token. Verified merchants get a trust badge. | Free |

### Commerce Protocol Integration

| Tool | Description | Credits |
|------|-------------|---------|
| `InsumerAcpDiscountTool` | Check discount eligibility in OpenAI/Stripe ACP format. Returns coupon objects and per-item allocations. | 1/call |
| `InsumerUcpDiscountTool` | Check discount eligibility in Google UCP format. Returns title, extension field, and applied array. | 1/call |
| `InsumerValidateCodeTool` | Validate an INSR-XXXXX discount code. Returns validity, discount percent, expiry. | Free |

## Using All Tools

```python
from langchain_insumer import (
    InsumerAPIWrapper,
    InsumerAcpDiscountTool,
    InsumerAttestTool,
    InsumerBatchWalletTrustTool,
    InsumerBuyCreditsTool,
    InsumerBuyKeyTool,
    InsumerBuyMerchantCreditsTool,
    InsumerCheckDiscountTool,
    InsumerComplianceTemplatesTool,
    InsumerConfigureNftsTool,
    InsumerConfigureSettingsTool,
    InsumerConfigureTokensTool,
    InsumerConfirmPaymentTool,
    InsumerCreateMerchantTool,
    InsumerCreditsTool,
    InsumerGetMerchantTool,
    InsumerJwksTool,
    InsumerListMerchantsTool,
    InsumerListTokensTool,
    InsumerMerchantStatusTool,
    InsumerPublishDirectoryTool,
    InsumerRequestDomainVerificationTool,
    InsumerUcpDiscountTool,
    InsumerValidateCodeTool,
    InsumerVerifyDomainTool,
    InsumerVerifyTool,
    InsumerWalletTrustTool,
)

api = InsumerAPIWrapper(api_key="insr_live_your_key_here")

tools = [
    InsumerAttestTool(api_wrapper=api),
    InsumerComplianceTemplatesTool(api_wrapper=api),
    InsumerWalletTrustTool(api_wrapper=api),
    InsumerBatchWalletTrustTool(api_wrapper=api),
    InsumerVerifyTool(api_wrapper=api),
    InsumerConfirmPaymentTool(api_wrapper=api),
    InsumerJwksTool(api_wrapper=api),
    InsumerListMerchantsTool(api_wrapper=api),
    InsumerGetMerchantTool(api_wrapper=api),
    InsumerListTokensTool(api_wrapper=api),
    InsumerCheckDiscountTool(api_wrapper=api),
    InsumerCreditsTool(api_wrapper=api),
    InsumerBuyKeyTool(api_wrapper=api),
    InsumerBuyCreditsTool(api_wrapper=api),
    InsumerBuyMerchantCreditsTool(api_wrapper=api),
    InsumerCreateMerchantTool(api_wrapper=api),
    InsumerMerchantStatusTool(api_wrapper=api),
    InsumerConfigureTokensTool(api_wrapper=api),
    InsumerConfigureNftsTool(api_wrapper=api),
    InsumerConfigureSettingsTool(api_wrapper=api),
    InsumerPublishDirectoryTool(api_wrapper=api),
    InsumerRequestDomainVerificationTool(api_wrapper=api),
    InsumerVerifyDomainTool(api_wrapper=api),
    InsumerAcpDiscountTool(api_wrapper=api),
    InsumerUcpDiscountTool(api_wrapper=api),
    InsumerValidateCodeTool(api_wrapper=api),
]
```

## Merchant Onboarding Example

```python
api = InsumerAPIWrapper(api_key="insr_live_your_key_here")

# 1. Create merchant
merchant = api.create_merchant(
    company_name="My Coffee Shop",
    company_id="my-coffee-shop",
    location="New York",
)

# 2. Configure token tiers
api.configure_tokens(
    merchant_id="my-coffee-shop",
    own_token={
        "symbol": "COFFEE",
        "chainId": 8453,
        "contractAddress": "0x...",
        "decimals": 18,
        "tiers": [
            {"name": "Bronze", "threshold": 100, "discount": 5},
            {"name": "Gold", "threshold": 1000, "discount": 15},
        ],
    },
)

# 3. Publish to directory
api.publish_directory(merchant_id="my-coffee-shop")
```

## Merkle Proof Example

```python
# Request EIP-1186 Merkle storage proofs for trustless verification
result = api.attest(
    wallet="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    proof="merkle",
    conditions=[
        {
            "type": "token_balance",
            "contractAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "chainId": 1,
            "threshold": 1000,
            "decimals": 6,
            "label": "USDC >= 1000",
        }
    ],
)

# Each result includes a proof object
for r in result["data"]["attestation"]["results"]:
    proof = r.get("proof", {})
    if proof.get("available"):
        print(f"Block: {proof['blockNumber']}")
        print(f"Mapping slot: {proof['mappingSlot']}")
        print(f"Proof nodes: {len(proof['accountProof'])} account, {len(proof['storageProof'])} storage")
    else:
        print(f"Proof unavailable: {proof.get('reason')}")
```

## Handling `rpc_failure` Errors

If the API cannot reach one or more blockchain data sources after retries, endpoints that produce signed attestations (`create_attestation`, `wallet_trust`, `batch_wallet_trust`) return `ok: false` with error code `rpc_failure`. No signature, no JWT, no credits charged. This is a retryable error — retry after 2-5 seconds.

**Important:** `rpc_failure` is NOT a verification failure. Do not treat it as `pass: false`. It means the data source was temporarily unavailable and the API refused to sign an unverified result.

```python
result = api.attest(wallet="0x...", conditions=[...])
if not result.get("ok") and result.get("error", {}).get("code") == "rpc_failure":
    # Retryable — wait and retry
    print("RPC failure:", result["error"]["failedConditions"])
```

## Supported Chains (33)

30 EVM chains + Solana + XRP Ledger + Bitcoin. Includes Ethereum, Base, Polygon, Arbitrum, Optimism, BNB Chain, Avalanche, and 23 more. [Full list →](https://insumermodel.com/developers/api-reference/)

## Get an API Key

Generate one from your terminal — no browser needed:

```bash
curl -s -X POST https://api.insumermodel.com/v1/keys/create \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "appName": "LangChain Agent", "tier": "free"}' | jq .
```

Returns an `insr_live_...` key with 100 reads/day and 10 verification credits. One free key per email.

Or get one at [insumermodel.com/developers](https://insumermodel.com/developers/).

**Tiers:** Free (100 reads/day, 10 credits) | Pro $9/mo (10,000/day) | Enterprise $29/mo (100,000/day)

## Links

- [API Documentation](https://insumermodel.com/developers/)
- [OpenAPI Spec](https://insumermodel.com/openapi.yaml)
- [Full API Reference](https://insumermodel.com/llms-full.txt)

## License

MIT
