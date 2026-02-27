# langchain-insumer

LangChain tools for [InsumerAPI](https://insumermodel.com/developers/) -- on-chain verification across 31 blockchains. Returns ECDSA-signed booleans without exposing wallet balances. Up to 10 conditions per request, each with its own chainId. Optional Merkle storage proofs for trustless verification.

**In production:** [DJD Agent Score](https://github.com/jacobsd32-cpu/djdagentscore) (Coinbase x402 ecosystem) uses InsumerAPI for AI agent wallet trust scoring. [Case study](https://insumermodel.com/blog/djd-agent-score-insumer-api-integration.html).

Also available as: [MCP server](https://www.npmjs.com/package/mcp-server-insumer) (23 tools, npm) | [OpenAI GPT](https://chatgpt.com/g/g-699c5e43ce2481918b3f1e7f144c8a49-insumerapi-verify) (GPT Store) | [insumer-verify](https://www.npmjs.com/package/insumer-verify) (client-side verification, npm)

## Installation

```bash
pip install langchain-insumer
```

## Quick Start

```python
from langchain_insumer import InsumerAPIWrapper, InsumerAttestTool

# Initialize the API wrapper
api = InsumerAPIWrapper(api_key="insr_live_YOUR_KEY_HERE")

# Create tools for your agent
attest_tool = InsumerAttestTool(api_wrapper=api)

# Use with a LangChain agent
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
tools = [attest_tool]
agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS)

agent.run("Does wallet 0x1234... hold at least 100 USDC on Ethereum?")
```

## Available Tools (23)

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
| `InsumerBuyCreditsTool` | Buy API key credits with USDC (25 credits/$1). | — |
| `InsumerBuyMerchantCreditsTool` | Buy merchant credits with USDC (25 credits/$1). | — |

### Merchant Onboarding

| Tool | Description | Credits |
|------|-------------|---------|
| `InsumerCreateMerchantTool` | Create a new merchant (100 free credits). | Free |
| `InsumerMerchantStatusTool` | Get private merchant details (owner only). | Free |
| `InsumerConfigureTokensTool` | Configure token discount tiers (max 8 tokens). | Free |
| `InsumerConfigureNftsTool` | Configure NFT collection discounts (max 4). | Free |
| `InsumerConfigureSettingsTool` | Update discount mode, cap, USDC payments. | Free |
| `InsumerPublishDirectoryTool` | Publish merchant to public directory. | Free |

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
    InsumerUcpDiscountTool,
    InsumerValidateCodeTool,
    InsumerVerifyTool,
    InsumerWalletTrustTool,
)

api = InsumerAPIWrapper(api_key="insr_live_YOUR_KEY_HERE")

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
    InsumerAcpDiscountTool(api_wrapper=api),
    InsumerUcpDiscountTool(api_wrapper=api),
    InsumerValidateCodeTool(api_wrapper=api),
]
```

## Verification Example

```python
import json

api = InsumerAPIWrapper(api_key="insr_live_YOUR_KEY_HERE")

result = api.attest(
    wallet="0x1234567890abcdef1234567890abcdef12345678",
    conditions=[
        {
            "type": "token_balance",
            "contractAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "chainId": 1,
            "threshold": 1000,
            "decimals": 6,
            "label": "USDC >= 1000 on Ethereum",
        },
        {
            "type": "nft_ownership",
            "contractAddress": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
            "chainId": 1,
            "label": "Bored Ape Yacht Club holder",
        },
    ],
)

attestation = result["data"]["attestation"]
print(f"Pass: {attestation['pass']}")
for r in attestation["results"]:
    print(f"  {r['label']}: {'met' if r['met'] else 'not met'}")
print(f"Signature: {result['data']['sig']}")
print(f"Key ID: {result['data']['kid']}")
```

## Merchant Onboarding Example

```python
api = InsumerAPIWrapper(api_key="insr_live_YOUR_KEY_HERE")

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
    wallet="0x1234567890abcdef1234567890abcdef12345678",
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
