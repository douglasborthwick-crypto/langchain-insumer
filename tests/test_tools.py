"""Tests for langchain-insumer tools."""

import json
from unittest.mock import MagicMock, patch

import pytest

from langchain_insumer import (
    InsumerAPIWrapper,
    InsumerAttestTool,
    InsumerCheckDiscountTool,
    InsumerCreditsTool,
    InsumerListMerchantsTool,
    InsumerListTokensTool,
    InsumerVerifyTool,
)


@pytest.fixture
def api():
    return InsumerAPIWrapper(api_key="insr_live_0000000000000000000000000000000000000000")


@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "ok": True,
        "data": {},
        "meta": {"version": "1.0", "timestamp": "2026-02-22T00:00:00.000Z"},
    }
    mock.raise_for_status = MagicMock()
    return mock


class TestInsumerAPIWrapper:
    def test_headers(self, api):
        headers = api._headers()
        assert headers["X-API-Key"] == "insr_live_0000000000000000000000000000000000000000"
        assert headers["Content-Type"] == "application/json"

    @patch("langchain_insumer.wrapper.requests.post")
    def test_attest(self, mock_post, api, mock_response):
        mock_response.json.return_value = {
            "ok": True,
            "data": {
                "attestation": {
                    "id": "ATST-A7C3E",
                    "pass": True,
                    "results": [{"condition": 0, "met": True}],
                    "passCount": 1,
                    "failCount": 0,
                },
                "sig": "base64sig...",
            },
            "meta": {"creditsRemaining": 9},
        }
        mock_post.return_value = mock_response

        result = api.attest(
            wallet="0x1234567890abcdef1234567890abcdef12345678",
            conditions=[
                {
                    "type": "token_balance",
                    "contractAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                    "chainId": 1,
                    "threshold": 100,
                    "decimals": 6,
                }
            ],
        )

        assert result["ok"] is True
        assert result["data"]["attestation"]["pass"] is True
        mock_post.assert_called_once()

    @patch("langchain_insumer.wrapper.requests.get")
    def test_get_credits(self, mock_get, api, mock_response):
        mock_response.json.return_value = {
            "ok": True,
            "data": {"apiKeyCredits": 42, "tier": "pro", "dailyLimit": 10000},
        }
        mock_get.return_value = mock_response

        result = api.get_credits()
        assert result["data"]["apiKeyCredits"] == 42

    @patch("langchain_insumer.wrapper.requests.get")
    def test_list_merchants(self, mock_get, api, mock_response):
        mock_response.json.return_value = {
            "ok": True,
            "data": [{"id": "test", "companyName": "Test Co"}],
            "meta": {"total": 1, "limit": 50, "offset": 0},
        }
        mock_get.return_value = mock_response

        result = api.list_merchants(token="UNI", limit=10)
        assert len(result["data"]) == 1

    @patch("langchain_insumer.wrapper.requests.get")
    def test_check_discount(self, mock_get, api, mock_response):
        mock_response.json.return_value = {
            "ok": True,
            "data": {"eligible": True, "totalDiscount": 15},
        }
        mock_get.return_value = mock_response

        result = api.check_discount(
            merchant_id="test",
            wallet="0x1234567890abcdef1234567890abcdef12345678",
        )
        assert result["data"]["totalDiscount"] == 15


class TestTools:
    @patch("langchain_insumer.wrapper.requests.post")
    def test_attest_tool(self, mock_post, api, mock_response):
        mock_response.json.return_value = {
            "ok": True,
            "data": {"attestation": {"pass": True}},
        }
        mock_post.return_value = mock_response

        tool = InsumerAttestTool(api_wrapper=api)
        assert tool.name == "insumer_attest"

        result = tool._run(
            conditions=json.dumps([{"type": "token_balance", "contractAddress": "0x...", "chainId": 1, "threshold": 100}]),
            wallet="0x1234567890abcdef1234567890abcdef12345678",
        )
        parsed = json.loads(result)
        assert parsed["ok"] is True

    def test_credits_tool_name(self, api):
        tool = InsumerCreditsTool(api_wrapper=api)
        assert tool.name == "insumer_credits"

    def test_list_merchants_tool_name(self, api):
        tool = InsumerListMerchantsTool(api_wrapper=api)
        assert tool.name == "insumer_list_merchants"

    def test_list_tokens_tool_name(self, api):
        tool = InsumerListTokensTool(api_wrapper=api)
        assert tool.name == "insumer_list_tokens"

    def test_check_discount_tool_name(self, api):
        tool = InsumerCheckDiscountTool(api_wrapper=api)
        assert tool.name == "insumer_check_discount"

    def test_verify_tool_name(self, api):
        tool = InsumerVerifyTool(api_wrapper=api)
        assert tool.name == "insumer_verify"
