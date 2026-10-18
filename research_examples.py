"""Illustrative prevalence and entity-mapping examples; invented data only."""
import json
from math import sqrt


def prevalence(events, assessed):
    """Wilson 95% interval for independent Bernoulli observations, unweighted."""
    if type(events) is not int or type(assessed) is not int:
        raise ValueError("Counts must be integers")
    if assessed <= 0 or not 0 <= events <= assessed:
        raise ValueError("Require 0 <= events <= assessed and assessed > 0")
    p = events / assessed
    z = 1.959963984540054
    denominator = 1 + z*z/assessed
    center = (p + z*z/(2*assessed))/denominator
    half = z*sqrt(p*(1-p)/assessed + z*z/(4*assessed**2))/denominator
    return {"events": events, "assessed": assessed, "proportion": p,
            "lower95": max(0, center-half), "upper95": min(1, center+half)}


def map_entities(records, registry):
    """Exact jurisdiction + registry-ID join. Names alone never establish identity."""
    index = {}
    for entity in registry:
        key = (entity.get("jurisdiction"), entity.get("registry_id"))
        if all(key):
            index.setdefault(key, []).append(entity)
    results = []
    for row in records:
        key = (row.get("jurisdiction"), row.get("registry_id"))
        matches = index.get(key, []) if all(key) else []
        result = {"input": dict(row), "status": "unresolved", "evidence": []}
        if len(matches) > 1:
            result["status"] = "ambiguous_registry_key"
        elif len(matches) == 1:
            match = matches[0]
            result["evidence"] = [{"source": match["source"], "as_of": match["as_of"]}]
            if row.get("domain") and row["domain"] != match.get("domain"):
                result["status"] = "domain_conflict_review"
            else:
                result.update(status="exact_id_match", canonical_name=match["name"])
        results.append(result)
    return results


def demo():
    groups = [("A", 20, 250), ("B", 60, 500), ("C", 40, 250)]
    registry = [{"jurisdiction": "EX", "registry_id": "00101",
                 "name": "Northstar Example", "domain": "northstar.example",
                 "source": "invented-registry", "as_of": "2026-10-18"}]
    rows = [{"jurisdiction": "EX", "registry_id": "00101", "domain": "northstar.example"},
            {"name": "Northstar Example"},
            {"jurisdiction": "EX", "registry_id": "00101", "domain": "different.example"}]
    return {"notice": "Invented data; not client findings. No external API access.",
            "groups": [{"group": name, **prevalence(k, n)} for name, k, n in groups],
            "overall": prevalence(sum(x[1] for x in groups), sum(x[2] for x in groups)),
            "mapping": map_entities(rows, registry)}


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2))
