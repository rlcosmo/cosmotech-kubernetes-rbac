"""Validate namespace boundaries before reviewing Argo delivery permissions."""
from pathlib import Path

import yaml

resources = list(yaml.safe_load_all(Path('ops/kubernetes/argocd-orders-rbac.yaml').read_text()))
assert len(resources) == 4
for namespace in ('orders-api', 'orders-worker'):
    scoped = [r for r in resources if r['metadata']['namespace'] == namespace]
    assert {r['kind'] for r in scoped} == {'Role', 'RoleBinding'}
    role = next(r for r in scoped if r['kind'] == 'Role')
    binding = next(r for r in scoped if r['kind'] == 'RoleBinding')
    assert binding['roleRef']['name'] == role['metadata']['name']
    assert binding['subjects'] == [{'kind': 'Group', 'name': 'cosmotech-argocd-orders', 'apiGroup': 'rbac.authorization.k8s.io'}]
    permitted = set()
    for rule in role['rules']:
        assert '*' not in rule['apiGroups'] + rule['resources'] + rule['verbs']
        assert not set(rule['resources']) & {'secrets', 'roles', 'rolebindings', 'namespaces', 'serviceaccounts'}
        for group in rule['apiGroups']:
            for resource in rule['resources']:
                permitted.add((group, resource))
        if set(rule['resources']) & {'pods', 'pods/log', 'replicasets', 'events', 'endpoints'}:
            assert set(rule['verbs']) <= {'get', 'list', 'watch'}
    assert ('autoscaling', 'horizontalpodautoscalers') in permitted
    assert ('networking.k8s.io', 'ingresses') in permitted
    assert ('', 'pods/log') in permitted
    print(f'{namespace}: scoped permissions validated')
