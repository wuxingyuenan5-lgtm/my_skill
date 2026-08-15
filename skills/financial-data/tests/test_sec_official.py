from datetime import date
from financial_data.sec_official import parse_sec_frame_payload, parse_sec_master_index, sec_master_index_url


def test_parse_sec_frame_payload_preserves_identity_and_filing_fields():
    payload = {"taxonomy":"us-gaap","tag":"ResearchAndDevelopmentExpense","label":"R&D","description":"x","ccp":"CY2025Q1","uom":"USD","data":[{"accn":"0001-25-000001","cik":320193,"entityName":"Apple Inc.","loc":"US-CA","end":"2025-03-29","val":8550000000,"fy":2025,"fp":"Q2","form":"10-Q","filed":"2025-05-02","frame":"CY2025Q1"}]}
    out = parse_sec_frame_payload(payload)
    assert out["taxonomy"] == "us-gaap"
    assert out["unit"] == "USD"
    assert out["period"] == "CY2025Q1"
    assert out["data"][0]["cik"] == "0000320193"
    assert out["data"][0]["value"] == 8550000000
    assert out["data"][0]["filed"] == "2025-05-02"


def test_parse_sec_master_index_skips_header_and_parses_pipe_rows():
    text = "Description: Master Index of EDGAR Dissemination Feed\nCIK|Company Name|Form Type|Date Filed|Filename\n320193|Apple Inc.|8-K|2026-08-14|edgar/data/320193/x.txt\n"
    rows = parse_sec_master_index(text)
    assert rows == [{"cik":"0000320193","company":"Apple Inc.","form":"8-K","filed":"2026-08-14","filename":"edgar/data/320193/x.txt"}]


def test_sec_master_index_url_uses_quarter_and_date():
    assert sec_master_index_url(date(2026, 8, 14)).endswith("/2026/QTR3/master.20260814.idx")
