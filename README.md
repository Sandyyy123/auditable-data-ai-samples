# Auditable data and AI evaluation samples

> **Proprietary - All Rights Reserved.** Licensed to Sandeep Grover. No reuse, copying, modification, or distribution without prior written permission. See LICENSE.

Small runnable demonstrations using entirely invented records. These are proposal
samples, not findings about a client's system and not prior client deliverables.

```sh
python -m pip install -r requirements.txt
python -m pytest -q
python main.py
```

`audits.py` contains:

* `clean_records`: schema-specific cleaning, exact duplicate handling, leading-zero
  IDs, immutable originals, exception quarantine and per-row change accounting.
* `temporal_answer`: valid-time facts, explicit date boundaries and conflict handling.
* `strict_score`: narrow declared normalisation, correct abstention, wrong-answer,
  substring and Unicode canaries. This is a demonstration oracle, not a universal
  natural-language scorer. Paraphrases need a separately specified rubric.
* `business_scenario`: demand/capacity constraints and incremental staffing costs.
* `maximum_purchase_price`: transparent margin arithmetic, not a valuation model.

The temporal demo is effective-time only; transaction-time and late corrections
require a separately agreed bitemporal model. No Graphiti/FalkorDB integration is
claimed. The public toy answers are NOT a client's private blind test set. Private
audit records and frozen answer keys must remain client-only.

The finance example excludes tax, financing, capital expenditure and working
capital. The cleaning schema is illustrative; real mappings and missing-value
rules require client agreement. No external API, real customer records, LLM API or
network access is used by these scripts.

## Prevalence and source-aware entity mapping

Run `python research_examples.py` for invented examples.

```text
Agreed case definition + assessed denominators -> validation -> prevalence + Wilson CI
Permitted source exports -> jurisdiction / registry-ID join -> conflict review -> provenance
```

The prevalence interval assumes independent, unweighted observations. Clustered or
weighted surveys require a design-aware estimator; a case/control sample cannot
estimate population prevalence. Missing outcomes are not negatives. The demo
pools three disjoint invented groups by event and denominator counts.

The mapping demo makes exact identifier joins and quarantines conflicts. It does
not prove beneficial ownership, infer corporate relationships, or resolve fuzzy
names. Source timestamps are retained. No paid subscriptions or API access are
claimed; production sources require client-provided rights or permitted public
access and an agreed schema.
