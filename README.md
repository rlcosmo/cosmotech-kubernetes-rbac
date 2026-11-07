# CosmoTech — Controle de acesso Kubernetes (RBAC)

Este repositório é a **fonte oficial das permissões RBAC** do Kubernetes para as aplicações do laboratório. As permissões são aplicadas por operações de manutenção revisadas, separadamente da entrega das aplicações pelo Argo CD.

## O que é permitido

- O Argo CD gerencia, nos namespaces `orders-api` e `orders-worker`, Deployments, ConfigMaps, Services, HPA (`autoscaling/v2`) e Ingress.
- A consulta a ReplicaSets, Pods, eventos e endpoints é somente leitura.
- A leitura de logs dos Pods é permitida para diagnóstico.
- **Não há concessão de `cluster-admin`**, acesso a Secrets ou permissões sobre recursos de todo o cluster.
- As identidades IAM não são modificadas por este repositório.

## Procedimento de alteração

1. Revise os manifests RBAC e confirme os namespaces afetados.
2. Antes de publicar alterações de HPA ou Ingress pelo GitOps, instale as permissões necessárias em uma janela autorizada.
3. Verifique as autorizações com `kubectl auth can-i` e valide os manifests com `kubectl apply --dry-run=server`, utilizando os arquivos apropriados.
4. Se necessário, ajuste separadamente, no K3s de gerenciamento, a lista de namespaces autorizados no Secret de conexão do cluster usado pelo Argo CD. **Não registre valores de Secrets neste repositório.**
5. Confirme o funcionamento do Argo CD e das aplicações após a alteração.

## Reversão

Para desfazer as permissões adicionais, primeiro suspenda a sincronização do worker e remova seus recursos GitOps por meio do procedimento revisado. Em seguida, reverta as regras RBAC específicas dos namespaces. Não altere filas, retenção de dados ou infraestrutura sem necessidade.

## Origem

Extraído de [aws-serverless-lab](https://github.com/rlcosmo/aws-serverless-lab) no commit `6f3e67f9e93d626393b23b6884b031767a63fea0`, preservando o histórico. Os arquivos anteriores são apenas registros da migração; a extração não recriou infraestrutura.

## Lab V2 — manutenção de observabilidade

`ops/kubernetes/lab-v2-observability-reader.yaml` corrige o Forbidden da manutenção somente para leitura de ConfigMap, PodMonitor, ServiceMonitor e PrometheusRule no namespace observability. Não altera o ClusterRole existente, não lê Secrets e não concede create/patch/update/delete ou administração RBAC.

Instalar apenas por executor com autorização RBAC nesse namespace, com server dry-run antes do apply dos dois objetos revisados. A role de manutenção não pode instalar a própria permissão: um Forbidden não autoriza escalada. Validar com a sessão temporária dessa role: `kubectl auth can-i list prometheusrules.monitoring.coreos.com -n observability` deve permitir, e `kubectl auth can-i get secrets -n observability` deve continuar negado. CI estático não comprova instalação.

O workflow `lab-v2-rbac.yml` instala somente esses dois objetos a partir de main, após validação local e server dry-run. Exige `LAB_V2_RBAC_BOOTSTRAP_ROLE_ARN`, uma identidade temporária previamente autorizada nesse namespace e com caminho de rede já autorizado ao EKS. Não cria acesso de rede, não muda trust/IAM, não usa fallback administrativo nem modifica o RBAC Orders. Falta de role, acesso à API ou autorização de bind/escalate causa falha antes/durante o server dry-run; não é contornada. O kubeconfig temporário usa exec credential da role OIDC, sem tokens permanentes. Merge/CI não comprovam instalação; confirmar depois com a sessão real de manutenção.
