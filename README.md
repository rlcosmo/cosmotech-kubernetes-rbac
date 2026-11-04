# cosmotech-kubernetes-rbac

Canonical Kubernetes RBAC. Argo CD manages application resources only; no cluster-admin grant. Apply RBAC through reviewed maintenance operations.

Extracted from [aws-serverless-lab](https://github.com/rlcosmo/aws-serverless-lab) at `6f3e67f9e93d626393b23b6884b031767a63fea0` with original commit ancestry preserved. Original files remain available there as migration snapshots. No infrastructure was recreated by extraction.

## Orders delivery

The Argo role/binding is declared independently in orders-api and orders-worker.
It manages Deployments, ConfigMaps, Services, autoscaling/v2 HPA and Ingress in
those namespaces only. ReplicaSets, Pods, events and endpoints remain read-only;
get pods/log preserves the existing UI log-viewing fix. No Secret or
cluster-scoped permission is granted. IAM identities do not change here.

Review and install these permissions before merging GitOps HPA/Ingress changes.
Also extend Argo's existing cluster Secret namespace list on management K3s;
that management operation is outside these EKS roles. No secret values belong
in this repository. Check auth can-i and server dry-run during authorized
delivery. Roll back the added namespaced rules after pausing worker sync and
removing its GitOps resources through reviewed delivery. No data, retries,
retention or fixed infrastructure costs change with RBAC.
