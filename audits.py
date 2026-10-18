"""Small, synthetic proposal demonstrations. No client data or production claims."""
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
import unicodedata


def clean_records(rows):
    """Explicit demo schema; preserve IDs, reject ambiguity, retain an audit trail."""
    accepted, exceptions, audit, seen, candidates = [], [], [], set(), []
    for index, raw in enumerate(rows, 1):
        item = {k: str(raw.get(k, '')).strip() for k in ('id', 'date', 'amount', 'category')}
        issues = []
        if not item['id']:
            issues.append('missing_id')
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', item['date']):
                raise ValueError('ISO date required')
            date.fromisoformat(item['date'])
        except ValueError:
            issues.append('invalid_or_ambiguous_date')
        try:
            amount = Decimal(item['amount'])
            if not amount.is_finite():
                raise InvalidOperation
            item['amount'] = format(amount, 'f')
        except InvalidOperation:
            issues.append('invalid_or_missing_amount')
        if not item['category']:
            issues.append('missing_category')
        if issues:
            exceptions.append({'source_row': index, 'original': raw, 'issues': issues})
            audit.append({'source_row': index, 'action': 'quarantine', 'issues': issues})
            continue
        key = tuple(item.values())
        if key in seen:
            audit.append({'source_row': index, 'action': 'exact_duplicate_removed', 'original': raw})
            continue
        seen.add(key)
        candidates.append((index, raw, item))
    counts = {}
    for _, _, item in candidates:
        counts[item['id']] = counts.get(item['id'], 0) + 1
    for index, raw, item in candidates:
        if counts[item['id']] > 1:
            exceptions.append({'source_row': index, 'original': raw, 'issues': ['conflicting_id']})
            audit.append({'source_row': index, 'action': 'quarantine', 'issues': ['conflicting_id']})
        else:
            accepted.append(item)
            audit.append({'source_row': index, 'action': 'accepted', 'original': raw, 'cleaned': item})
    return {'clean': accepted, 'exceptions': exceptions, 'audit': sorted(audit, key=lambda x: x['source_row']),
            'input_rows': len(rows)}


def temporal_answer(records, entity, attribute, as_of):
    """Effective date semantics; conflicts fail closed. No fuzzy entity matching."""
    cutoff = date.fromisoformat(as_of)
    eligible = [r for r in records if r['entity'] == entity and r['attribute'] == attribute
                and date.fromisoformat(r['valid_from']) <= cutoff
                and (not r.get('valid_to') or cutoff < date.fromisoformat(r['valid_to']))]
    if not eligible:
        return {'status': 'no_match', 'value': None}
    latest = max(r['valid_from'] for r in eligible)
    values = {r['value'] for r in eligible if r['valid_from'] == latest}
    if len(values) != 1:
        return {'status': 'conflict', 'value': None}
    return {'status': 'match', 'value': values.pop()}


def strict_score(actual, expected):
    """Example strict contract: NFC + outer whitespace only, no substrings/casefold."""
    if not isinstance(actual, dict) or set(actual) != {'status', 'value'}:
        return False
    if actual['status'] != expected['status']:
        return False
    if expected['value'] is None:
        return actual['value'] is None
    if not isinstance(actual['value'], str):
        return False
    return unicodedata.normalize('NFC', actual['value'].strip()) == unicodedata.normalize('NFC', expected['value'])


def freeze_key(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def business_scenario(demand, capacity, unit_price, variable_unit_cost, fixed_cost, staff_cost=0):
    """One-period synthetic operating scenario, excluding tax/working capital/capex."""
    if any(x < 0 for x in [demand, capacity, unit_price, variable_unit_cost, fixed_cost, staff_cost]):
        raise ValueError('Inputs must be nonnegative')
    sold = min(demand, capacity)
    return {'units_sold': sold, 'revenue': sold * unit_price,
            'operating_profit': sold * (unit_price - variable_unit_cost) - fixed_cost - staff_cost}


def maximum_purchase_price(sale_price, reconditioning, selling_cost, holding_cost, target_profit):
    if any(x < 0 for x in [sale_price, reconditioning, selling_cost, holding_cost, target_profit]):
        raise ValueError('Negative inputs are unsupported')
    return sale_price - reconditioning - selling_cost - holding_cost - target_profit
