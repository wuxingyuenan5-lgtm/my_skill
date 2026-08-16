from financial_data.futures import basis, calendar_spread, roll_adjustment, select_dominant_contract, term_structure

def test_select_dominant_contract_by_open_interest():
    rows=[{"contract_id":"CU2609","open_interest":100,"volume":500},{"contract_id":"CU2610","open_interest":200,"volume":100}]
    assert select_dominant_contract(rows)["contract_id"]=="CU2610"

def test_term_structure_sorts_delivery_month():
    rows=[{"contract_id":"CU2611","delivery_month":"2026-11","settlement":81000},{"contract_id":"CU2609","delivery_month":"2026-09","settlement":80000},{"contract_id":"CU2610","delivery_month":"2026-10","settlement":80500}]
    out=term_structure(rows); assert [x["contract_id"] for x in out]==["CU2609","CU2610","CU2611"]

def test_calendar_spread_and_basis_explicit_definition():
    near={"contract_id":"CU2609","settlement":80000}; far={"contract_id":"CU2610","settlement":80500}
    assert calendar_spread(near,far)["value"]==-500.0; assert basis(80300,80000)["value"]==300.0

def test_roll_adjustment_supports_difference_and_ratio():
    assert roll_adjustment(80000,81000,"difference")["value"]==1000.0; assert roll_adjustment(80000,81000,"ratio")["value"]==81000/80000
