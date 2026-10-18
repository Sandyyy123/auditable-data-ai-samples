import copy
import pytest
from audits import *

def row(**kwargs):
    return dict({'id':'001','date':'2026-01-05','amount':'12.50','category':'parts'}, **kwargs)

def test_leading_zero_and_original_preserved():
    rows=[row(amount=' 12.50 ')]; before=copy.deepcopy(rows)
    out=clean_records(rows)
    assert rows==before and out['clean'][0]['id']=='001'
    assert out['audit'][0]['original']['amount']==' 12.50 '

def test_exact_duplicate_and_accounting():
    out=clean_records([row(),row()])
    assert len(out['clean'])==1 and len(out['audit'])==2
    assert out['audit'][1]['action']=='exact_duplicate_removed'

@pytest.mark.parametrize('bad',['01/02/2026','2026-02-30','2026-1-1',''])
def test_ambiguous_dates_never_guessed(bad):
    assert not clean_records([row(date=bad)])['clean']

@pytest.mark.parametrize('bad',['','NaN','Infinity','1,200','abc'])
def test_bad_amount_never_imputed(bad):
    assert not clean_records([row(amount=bad)])['clean']

def test_conflicting_id_never_collapsed():
    out=clean_records([row(),row(amount='15')])
    assert len(out['exceptions'])==2 and not out['clean']

def test_idempotent_clean_output():
    clean=clean_records([row(category=' parts ')])['clean']
    assert clean_records(clean)['clean']==clean

@pytest.fixture
def records():
    return [dict(entity='X',attribute='owner',value='Ada',valid_from='2026-01-01',valid_to='2026-02-01'),
            dict(entity='X',attribute='owner',value='Bea',valid_from='2026-02-01',valid_to=None)]

def test_temporal_boundary(records):
    assert temporal_answer(records,'X','owner','2026-01-31')['value']=='Ada'
    assert temporal_answer(records,'X','owner','2026-02-01')['value']=='Bea'
    assert temporal_answer(records,'X','owner','2025-12-31')['status']=='no_match'

def test_wrong_entity_no_match(records):
    assert temporal_answer(records,'XX','owner','2026-03-01')['status']=='no_match'

def test_conflict_fails_closed(records):
    records.append(dict(records[1],value='Cara'))
    assert temporal_answer(records,'X','owner','2026-03-01')['status']=='conflict'

@pytest.mark.parametrize('wrong',['Bea or Ada','Not Bea','Bеa','Bea\u200b','Bea.','bea'])
def test_scorer_rejects_near_misses_and_unicode(wrong):
    assert not strict_score({'status':'match','value':wrong},{'status':'match','value':'Bea'})

def test_nfc_allowed_and_whitespace():
    assert strict_score({'status':'match','value':' Cafe\u0301 '},{'status':'match','value':'Café'})

def test_no_match_must_not_contain_an_answer():
    assert not strict_score({'status':'no_match','value':'Bea'},{'status':'no_match','value':None})

def test_key_hash_order_independent():
    assert freeze_key({'a':1,'b':2})==freeze_key({'b':2,'a':1})
    assert freeze_key({'a':1})!=freeze_key({'a':2})

def test_capacity_without_demand_cannot_increase_revenue():
    a=business_scenario(900,1000,100,60,20000)
    b=business_scenario(900,1250,100,60,20000,9000)
    assert a['revenue']==b['revenue'] and b['operating_profit']==a['operating_profit']-9000

def test_vehicle_margin_identity():
    assert maximum_purchase_price(20000,1000,500,300,2000)==16200

def test_negative_cost_refused():
    with pytest.raises(ValueError): maximum_purchase_price(20000,-1,500,300,2000)
