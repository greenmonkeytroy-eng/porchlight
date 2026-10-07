"""
Porchlight OS — OCR Receipt Parser & Pantry Ingestion Pipeline (v3)
System: Porchlight Digital Twin Engine
Function: Converts scanned paper/digital receipts into structured item logs with
confidence scoring and DR-AIS logging for human-in-the-loop review.
"""

from __future__ import annotations

import datetime
import logging
import re

from pydantic import BaseModel

from app.config import settings
from app.services.drais_logger import DecisionRecord, emit_decision_record

logger = logging.getLogger("PorchlightOCR")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [Porchlight-OCR] - %(levelname)s - %(message)s")

_DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})")
_ITEM_PATTERN = re.compile(r"^([A-Za-z0-9\s\(\)\.\-]+)\s+\$?(\d+\.\d{2})$")
_SUMMARY_KEYWORDS = ("SUBTOTAL", "TOTAL", "TAX", "BALANCE", "CHANGE", "VISA", "MASTERCARD", "DEBIT")


class ReceiptItem(BaseModel):
    raw_item_name: str
    price_usd: float
    confidence_score: float
    requires_human_review: bool


class ParsedReceipt(BaseModel):
    merchant: str
    receipt_date: str
    parsed_items_count: int
    total_calculated_spend_usd: float
    items: list[ReceiptItem]


class ReceiptParser:
    def __init__(self, confidence_threshold: float | None = None) -> None:
        self.confidence_threshold = confidence_threshold if confidence_threshold is not None else settings.confidence_threshold

    def parse_raw_receipt_text(self, text: str) -> ParsedReceipt:
        """Parses raw receipt OCR text into structured merchant, date, and line items."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        merchant = lines[0] if lines else "Unknown Merchant"

        date_match = _DATE_PATTERN.search(text)
        receipt_date = date_match.group(1) if date_match else datetime.date.today().isoformat()

        items: list[ReceiptItem] = []
        for line in lines[1:]:
            match = _ITEM_PATTERN.match(line)
            if not match:
                continue

            item_name = match.group(1).strip()
            if any(kw in item_name.upper() for kw in _SUMMARY_KEYWORDS):
                continue

            confidence = round(0.85 if len(item_name) > 3 else 0.60, 2)
            items.append(
                ReceiptItem(
                    raw_item_name=item_name,
                    price_usd=float(match.group(2)),
                    confidence_score=confidence,
                    requires_human_review=confidence < self.confidence_threshold,
                )
            )

        return ParsedReceipt(
            merchant=merchant,
            receipt_date=receipt_date,
            parsed_items_count=len(items),
            total_calculated_spend_usd=round(sum(i.price_usd for i in items), 2),
            items=items,
        )

    def parse_and_log(self, text: str) -> ParsedReceipt:
        """Parses a receipt and emits the DR-AIS Decision Record for governance."""
        parsed = self.parse_raw_receipt_text(text)

        emit_decision_record(
            DecisionRecord(
                component="ocr",
                action_type="RECEIPT_OCR_PARSING_AND_INGESTION",
                decision_logic="REGEX_PATTERN_CONFIDENCE_SCORING",
                inputs={"merchant": parsed.merchant, "receipt_date": parsed.receipt_date},
                output=parsed.model_dump(),
                human_override_available=any(i.requires_human_review for i in parsed.items),
            )
        )
        return parsed


if __name__ == "__main__":
    parser = ReceiptParser()

    mock_ocr_receipt = """
    WHOLE FOODS MARKET
    DATE: 2026-10-06
    ORGANIC MILK 2L $4.50
    ROLLED OATS 1KG $3.80
    CHICKEN BREAST 1KG $11.50
    SUBTOTAL $19.80
    TAX $0.00
    TOTAL $19.80
    """

    result = parser.parse_and_log(mock_ocr_receipt)
    print("\n=== Porchlight OCR Receipt Ingestion ===")
    print(f"Merchant: {result.merchant}")
    print(f"Date:     {result.receipt_date}")
    print(f"Items:    {result.parsed_items_count}")
    print(f"Total:    ${result.total_calculated_spend_usd}\n")

    for item in result.items:
        print(f"• {item.raw_item_name} -> ${item.price_usd} (Confidence: {item.confidence_score})")
