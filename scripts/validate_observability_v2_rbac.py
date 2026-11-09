"""Reject changes that give the V2 reconciler storage, creation or deletion rights."""
import json
from pathlib import Path

objects=json.loads(Path('ops/kubernetes/argocd-observability-v2.json').read_text())['items']
assert {x['kind'] for x in objects} == {'Role','RoleBinding'} and len(objects)==2
role,binding=objects
assert role['metadata']==binding['metadata']=={'name':'cosmotech-argocd-observability-v2','namespace':'observability'}
assert binding['roleRef']=={'kind':'Role','name':role['metadata']['name'],'apiGroup':'rbac.authorization.k8s.io'}
assert binding['subjects']==[{'kind':'Group','name':'cosmotech-argocd-orders','apiGroup':'rbac.authorization.k8s.io'}]
assert len(role['rules'])==4
for group,resource in [('', 'configmaps'),('monitoring.coreos.com','prometheusrules')]:
    rules=[r for r in role['rules'] if r['apiGroups']==[group] and r['resources']==[resource]]
    assert len(rules)==2
    assert {'apiGroups':[group],'resources':[resource],'verbs':['get','list','watch']} in rules
    assert {'apiGroups':[group],'resources':[resource],'resourceNames':['cosmotech-v2-sqs-workers'],'verbs':['update','patch']} in rules
print('PASS: only two named V2 objects writable; no create/delete, workloads, storage, secrets or RBAC grants')
