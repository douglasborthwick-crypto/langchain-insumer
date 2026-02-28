# langchain-insumer

LangChain tools for [InsumerAPI](https://insumermodel.com/developers/) -- on-chain verification across 31 blockchains. Returns ECDSA-signed booleans without exposing wallet balances. Up to 10 conditions per request, each with its own chainId. Optional Merkle storage proofs for trustless verification.

**In production:** [DJD Agent Score](https://github.com/jacobsd32-cpu/djdagentscore) (Coinbase x402 ecosystem) uses InsumerAPI for AI agent wallet trust scoring. [Case study](https://insumermodel.com/blog/djd-agent-score-insumer-api-integration.html).

Also available as: [MCP server](https://www.npmjs.com/package/mcp-server-insumer) (25 tools, npm) | [OpenAI GPT](https://chatgpt.com/g/g-699c5e43ce2481918b3f1e7f144c8a49-insumerapi-verify) (GPT Store) | [insumer-verify](https://www.npmjs.com/package/insumer-verify) (client-side verification, npm)

## Install

```bash
pip install langchain-insumer
```

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
      "id": "ATST-A7C3E",
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
          "conditionHash": "0x8a3b...",
          "blockNumber": "0x129e3f7",
          "blockTimestamp": "2026-02-28T12:34:56.000Z"
        }
      ],
      "passCount": 1,
      "failCount": 0,
      "attestedAt": "2026-02-28T12:34:57.000Z",
      "expiresAt": "2026-02-28T13:04:57.000Z"
    },
    "sig": "MEUCIQD...(base64 ECDSA signature)...",
    "kid": "insumer-attest-v1"
  },
  "meta": { "version": "1.0", "creditsCharged": 1, "creditsRemaining": 99 }
}
```

No balances. No amounts. Just a signed true/false per condition.

## Verify the Response

The attestation is ECDSA-signed. Your application should verify it before trusting it. Use [insumer-verify](https://www.npmjs.com/package/insumer-verify) in your Node.js backend or browser:

```bash
npm install insumer-verify
```

```typescript
import { verifyAttestation } from "insumer-verify";

// attestationResponse = the JSON returned by api.attest()
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

## Available Tools (25)

### Verification

| Tool | Description | Credits |
|------|-------------|---------|
| `InsumerAttestTool` | Verify on-chain conditions (token balances, NFT ownership, EAS attestations, Farcaster identity). Optional `proof="merkle"` for EIP-1186 Merkle proofs. | 1/call (2 with merkle) |
| `InsumerComplianceTemplatesTool` | List available EAS compliance templates (Coinbase Verifications on Base, Gitcoin Passport on Optimism). | Free |
| `InsumerWalletTrustTool` | Generate wallet trust fact profile (17 checks, 4 dimensions). | 3/call (6 with merkle) |
| `InsumerBatchWalletTrustTool` | Batch trust profiles for up to 10 wallets. 5-8x faster. | 3/wallet (6 with merkle) |
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
| `InsumerCreditsTool` | Check API key credit balance and tier. | Free |
| `InsumerBuyCreditsTool` | Buy API key credits with USDC (25 credits/$1). | -- |
| `InsumerBuyMerchantCreditsTool` | Buy merchant credits with USDC (25 credits/$1). | -- |

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
        print(f"Storage slot: {proof['mappingSlot']}")
        print(f"Proof nodes: {len(proof['accountProof'])} account, {len(proof['storageProof'])} storage")
    else:
        print(f"Proof unavailable: {proof.get('reason')}")
```

## Supported Chains (31)

Ethereum, BNB Chain, Base, Avalanche, Polygon, Arbitrum, Optimism, Solana, Chiliz, Soneium, Plume, Sonic, Gnosis, Mantle, Scroll, Linea, zkSync Era, Blast, Taiko, Ronin, Celo, Moonbeam, Moonriver, Viction, opBNB, World Chain, Unichain, Ink, Sei, Berachain, ApeChain.

## Get an API Key

- **Free** (10 credits): [insumermodel.com/developers](https://insumermodel.com/developers/)
- **Pro** (10,000/day): 29 USDC/month
- **Enterprise** (100,000/day): 99 USDC/month

## Links

- [API Documentation](https://insumermodel.com/developers/)
- [OpenAPI Spec](https://insumermodel.com/openapi.yaml)
- [Full API Reference](https://insumermodel.com/llms-full.txt)

## License

MIT
