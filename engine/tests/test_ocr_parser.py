from app.services.ocr_parser import ReceiptParser

MOCK_RECEIPT = """
WHOLE FOODS MARKET
DATE: 2026-10-06
ORGANIC MILK 2L $4.50
ROLLED OATS 1KG $3.80
CHICKEN BREAST 1KG $11.50
SUBTOTAL $19.80
TAX $0.00
TOTAL $19.80
"""


def test_parses_merchant_date_and_items():
    result = ReceiptParser().parse_raw_receipt_text(MOCK_RECEIPT)

    assert result.merchant == "WHOLE FOODS MARKET"
    assert result.receipt_date == "2026-10-06"
    assert result.parsed_items_count == 3
    assert result.total_calculated_spend_usd == 19.80
    assert [i.raw_item_name for i in result.items] == [
        "ORGANIC MILK 2L",
        "ROLLED OATS 1KG",
        "CHICKEN BREAST 1KG",
    ]


def test_summary_lines_are_excluded():
    result = ReceiptParser().parse_raw_receipt_text(MOCK_RECEIPT)

    names = {i.raw_item_name for i in result.items}
    assert not names & {"SUBTOTAL", "TAX", "TOTAL"}


def test_long_item_names_get_high_confidence_and_no_review_flag():
    result = ReceiptParser().parse_raw_receipt_text(MOCK_RECEIPT)

    for item in result.items:
        assert item.confidence_score == 0.85
        assert item.requires_human_review is False


def test_short_item_names_get_low_confidence_and_require_review():
    receipt = "CORNER STORE\nABC $1.00\n"
    result = ReceiptParser(confidence_threshold=0.70).parse_raw_receipt_text(receipt)

    assert len(result.items) == 1
    assert result.items[0].confidence_score == 0.60
    assert result.items[0].requires_human_review is True


def test_no_date_in_text_falls_back_to_today():
    receipt = "SOME SHOP\nWIDGET $5.00\n"
    result = ReceiptParser().parse_raw_receipt_text(receipt)

    import datetime

    assert result.receipt_date == datetime.date.today().isoformat()
