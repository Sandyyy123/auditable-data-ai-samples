import pytest
from research_examples import prevalence, map_entities, demo


def test_wilson_reference():
    r = prevalence(120, 1000)
    assert r['proportion'] == .12
    assert r['lower95'] == pytest.approx(.1013, abs=.0001)
    assert r['upper95'] == pytest.approx(.1416, abs=.0001)


@pytest.mark.parametrize('k,n', [(0,100), (100,100)])
def test_boundary_intervals(k, n):
    r = prevalence(k,n)
    assert 0 <= r['lower95'] < r['upper95'] <= 1


@pytest.mark.parametrize('k,n', [(1,0), (-1,10), (11,10), (1.5,10), (True,10)])
def test_invalid_denominators_and_counts(k,n):
    with pytest.raises(ValueError): prevalence(k,n)


def test_unequal_group_sizes_pooled_by_counts():
    assert demo()['overall']['proportion'] == .12
    assert demo()['overall']['assessed'] == 1000


def test_mapping_preserves_provenance_and_abstains():
    rows = demo()['mapping']
    assert [x['status'] for x in rows] == ['exact_id_match','unresolved','domain_conflict_review']
    assert rows[0]['evidence'][0]['source'] == 'invented-registry'


def test_duplicate_id_and_jurisdiction_safety():
    registry = [{'jurisdiction':'EX','registry_id':'001','name':'A','source':'toy','as_of':'2026-10-18'}]*2
    rows = [{'jurisdiction':'EX','registry_id':'001'}, {'jurisdiction':'OTHER','registry_id':'001'}]
    assert [x['status'] for x in map_entities(rows, registry)] == ['ambiguous_registry_key','unresolved']
