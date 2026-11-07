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

workflow = Path('.github/workflows/lab-v2-rbac.yml')
if workflow.exists():
    delivery = yaml.safe_load(workflow.read_text())
    for job in delivery['jobs'].values():
        assert all('runner.' not in str(value) for value in job.get('env', {}).values()), 'runner context is not available in jobs.env'

import json
bootstrap = json.loads(Path('ops/kubernetes/lab-v2-bootstrap-authority.json').read_text())['items']
assert len(bootstrap) == 2 and {r['kind'] for r in bootstrap} == {'Role', 'RoleBinding'}
assert all(r['metadata']['namespace'] == 'observability' for r in bootstrap)
role = next(r for r in bootstrap if r['kind'] == 'Role')
for rule in role['rules']:
    assert '*' not in rule['apiGroups'] + rule['resources'] + rule['verbs']
    assert 'secrets' not in rule['resources']
    if rule['apiGroups'] != ['rbac.authorization.k8s.io']:
        assert set(rule['verbs']) <= {'get', 'list', 'watch'}
    else:
        assert set(rule['resources']) == {'roles', 'rolebindings'}
        assert set(rule['verbs']) <= {'get', 'list', 'watch', 'create', 'patch', 'update'}
binding = next(r for r in bootstrap if r['kind'] == 'RoleBinding')
assert binding['roleRef']['kind'] == 'Role' and binding['roleRef']['name'] == role['metadata']['name']
assert binding['subjects'] == [{'kind': 'Group', 'name': 'cosmotech-lab-v2-rbac-bootstrap', 'apiGroup': 'rbac.authorization.k8s.io'}]
