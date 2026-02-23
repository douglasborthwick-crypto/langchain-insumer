# langchain-insumer

LangChain integration for [The Insumer Model](https://insumermodel.com) On-Chain Verification API.

Privacy-preserving on-chain verification and attestation across 31 blockchains. Submit arbitrary conditions against on-chain state, receive an ECDSA-signed boolean — no balances or private data revealed.

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
| `InsumerAttestTool` | Verify on-chain conditions with signed verification | 1/call |
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
    InsumerListMerchantsTool,
    InsumerListTokensTool,
    InsumerVerifyTool,
)

api = InsumerAPIWrapper(api_key="insr_live_YOUR_KEY_HERE")

tools = [
    InsumerAttestTool(api_wrapper=api),
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
