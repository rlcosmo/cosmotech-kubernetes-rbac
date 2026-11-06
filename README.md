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
