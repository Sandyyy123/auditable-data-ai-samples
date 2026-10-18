import json
from pathlib import Path
from audits import clean_records, temporal_answer, strict_score, freeze_key, business_scenario, maximum_purchase_price

def main():
    rows = [
        {'id':'001','date':'2026-01-05','amount':' 12.50 ','category':' parts '},
        {'id':'001','date':'2026-01-05','amount':'12.50','category':'parts'},
        {'id':'002','date':'01/02/2026','amount':'10','category':'parts'},
        {'id':'003','date':'2026-01-06','amount':'','category':'parts'},
        {'id':'004','date':'2026-01-07','amount':'10','category':'parts'},
        {'id':'004','date':'2026-01-07','amount':'11','category':'parts'},
        {'id':'005','date':'2026-01-08','amount':'25','category':'labour'},
    ]
    records = [
        {'entity':'Northstar','attribute':'owner','value':'Ada','valid_from':'2026-01-01','valid_to':'2026-02-01'},
        {'entity':'Northstar','attribute':'owner','value':'Bea','valid_from':'2026-02-01','valid_to':None},
    ]
    key = [temporal_answer(records,'Northstar','owner',d) for d in ['2025-12-31','2026-01-15','2026-02-01']]
    result = {'data':'entirely synthetic; not an audit of a client system', 'cleaning':clean_records(rows),
              'memory':{'answers':key,'key_sha256':freeze_key(key),
                        'wrong_superseded_answer_passes':strict_score({'status':'match','value':'Ada'},key[-1]),
                        'substring_attack_passes':strict_score({'status':'match','value':'Bea or Ada'},key[-1])},
              'finance':{'base':business_scenario(900,1000,100,60,20000),
                         'hire_without_demand':business_scenario(900,1250,100,60,20000,9000),
                         'hire_with_demand':business_scenario(1250,1250,100,60,20000,9000)},
              'vehicle':{'synthetic_sale_price':20000,'maximum_purchase_price':maximum_purchase_price(20000,1000,500,300,2000)}}
    Path('results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({'output':'results.json','clean_rows':len(result['cleaning']['clean']),
                      'exceptions':len(result['cleaning']['exceptions']),'key_hash':result['memory']['key_sha256']}))
if __name__ == '__main__':
    main()
