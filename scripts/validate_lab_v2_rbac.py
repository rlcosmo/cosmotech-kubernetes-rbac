"""Assert the maintenance extension is read-only and limited to observability."""
from pathlib import Path
import yaml

resources = list(yaml.safe_load_all(Path('ops/kubernetes/lab-v2-observability-reader.yaml').read_text()))
assert len(resources) == 2
assert {r['kind'] for r in resources} == {'Role', 'RoleBinding'}
assert all(r['metadata']['namespace'] == 'observability' for r in resources)
role = next(r for r in resources if r['kind'] == 'Role')
binding = next(r for r in resources if r['kind'] == 'RoleBinding')
assert binding['subjects'] == [{'kind': 'Group', 'name': 'cosmotech-maintenance-readers', 'apiGroup': 'rbac.authorization.k8s.io'}]
assert binding['roleRef']['kind'] == 'Role' and binding['roleRef']['name'] == role['metadata']['name']
assert {(group, resource) for rule in role['rules'] for group in rule['apiGroups'] for resource in rule['resources']} == {('', 'configmaps'), ('monitoring.coreos.com', 'podmonitors'), ('monitoring.coreos.com', 'servicemonitors'), ('monitoring.coreos.com', 'prometheusrules')}
assert all(set(rule['verbs']) == {'get', 'list', 'watch'} for rule in role['rules'])
print('Lab V2 maintenance: namespaced read-only scope validated; no Secrets or write permissions')
