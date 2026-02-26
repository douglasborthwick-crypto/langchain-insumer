# langchain-insumer

LangChain tools for [InsumerAPI](https://insumermodel.com/developers/) -- on-chain verification across 31 blockchains. Returns ECDSA-signed booleans without exposing wallet balances. Up to 10 conditions per request, each with its own chainId. Optional Merkle storage proofs for trustless verification.

**In production:** [DJD Agent Score](https://github.com/jacobsd32-cpu/djdagentscore) (Coinbase x402 ecosystem) uses InsumerAPI for AI agent wallet trust scoring. [Case study](https://insumermodel.com/blog/djd-agent-score-insumer-api-integration.html).

Also available as: [MCP server](https://www.npmjs.com/package/mcp-server-insumer) (16 tools, npm) | [OpenAI GPT](https://chatgpt.com/g/g-699c5e43ce2481918b3f1e7f144c8a49-insumerapi-verify) (GPT Store) | [insumer-verify](https://www.npmjs.com/package/insumer-verify) (client-side verification, npm)

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

## Available Tools

| Tool | Description | Credits |
|------|-------------|---------|
| `InsumerAttestTool` | Verify on-chain conditions with signed verification. Response includes `kid` for key identification. Optional `proof="merkle"` for EIP-1186 Merkle proofs. | 1/call (2 with merkle) |
| `InsumerJwksTool` | Get the JWKS with InsumerAPI's ECDSA P-256 public signing key. Match `kid` from attestation responses. | Free |
| `InsumerCheckDiscountTool` | Calculate discount for wallet at merchant | Free |
| `InsumerListMerchantsTool` | Browse merchant directory | Free |
| `InsumerListTokensTool` | List registered tokens and NFTs | Free |
| `InsumerVerifyTool` | Create signed discount code (INSR-XXXXX) | 1/call |
| `InsumerCreditsTool` | Check API key credit balance | Free |

## Using All Tools

```python
from langchain_insumer import (
    InsumerAPIWrapper,
    InsumerAttestTool,
    InsumerCheckDiscountTool,
    InsumerCreditsTool,
    InsumerJwksTool,
    InsumerListMerchantsTool,
    InsumerListTokensTool,
    InsumerVerifyTool,
)

api = InsumerAPIWrapper(api_key="insr_live_YOUR_KEY_HERE")

tools = [
    InsumerAttestTool(api_wrapper=api),
    InsumerJwksTool(api_wrapper=api),
    InsumerCheckDiscountTool(api_wrapper=api),
    InsumerCreditsTool(api_wrapper=api),
    InsumerListMerchantsTool(api_wrapper=api),
    InsumerListTokensTool(api_wrapper=api),
    InsumerVerifyTool(api_wrapper=api),
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
