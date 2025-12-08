# Architecture de la Plateforme d'Harmonisation SRM-CS

!!! info "À Propos de Cette Documentation"
Ce document fournit un aperçu détaillé de l'architecture de la plateforme déployée par le projet d'Harmonisation SRM-CS. La plateforme est un système complexe composé de plusieurs couches, incluant l'infrastructure, les middlewares et les applications, tous gérés et déployés via un moteur d'automation centralisé.

## Architecture Globale

L'architecture déployée est une plateforme complète sur site, basée sur des microservices construits sur Kubernetes. Elle est conçue pour être hautement disponible, sécurisée et évolutive, fournissant une pile complète de middlewares et de services pour exécuter des applications modernes.

L'architecture est déployée sur un hyperviseur (VMware ou Nutanix) et est segmentée en plusieurs zones réseau pour la sécurité et l'isolation. Elle exploite **Kubernetes (RKE2)** pour l'orchestration de conteneurs, **Rancher** pour la gestion de clusters, et une large gamme de middlewares open source populaires pour supporter les applications déployées. L'ensemble de la plateforme est géré en utilisant une approche GitOps avec **Argo CD** et **Gogs**.

Le processus de déploiement est entièrement automatisé et suit une séquence spécifique pour assurer une configuration cohérente et fiable.

### Principes Architecturaux Clés

- **Basé sur les Microservices** : Les applications sont décomposées en services indépendamment déployables
- **Haute Disponibilité** : Composants redondants et clusters multi-nœuds assurent la disponibilité
- **Isolation Sécuritaire** : Segmentation réseau via VLANs (zones LAN, INFRA, DMZ)
- **Workflow GitOps** : Toute configuration gérée comme du code dans des dépôts Git
- **Évolutivité** : Mise à l'échelle dynamique des VMs basée sur le nombre d'utilisateurs concurrents (100, 500, 1000, 10000)
- **Automation d'Abord** : Déploiement entièrement automatisé avec Ansible Runner

### Couches Architecturales

La plateforme se compose de trois couches principales :

#### 1. Couche Infrastructure

- Hyperviseur (VMware vSphere/ESXi ou Nutanix AHV)
- Machines virtuelles provisionnées pour différents rôles
- Segmentation réseau (VLANs, sous-réseaux, DNS)
- Load balancers HAProxy pour la distribution du trafic

#### 2. Couche Middleware

- **Orchestration de Conteneurs** : Trois clusters Kubernetes RKE2 (APPS, MIDDLEWARE, DMZ)
- **Gestion de Clusters** : Rancher pour une gestion unifiée
- **Stockage** : Longhorn (stockage bloc distribué) + MinIO (stockage objet compatible S3)
- **Sécurité** : HashiCorp Vault, Cert-manager, Neuvector, Keycloak
- **Messagerie** : Apache Kafka
- **Gestion d'API** : Gravitee (instances LAN et DMZ)
- **CI/CD** : Gogs + Argo CD pour GitOps
- **Surveillance** : Coroot pour l'observabilité
- **Automation de Workflows** : n8n
- **Moteur BPM** : Flowable (lorsque le produit eServices est sélectionné)

#### 3. Couche Application

Applications utilisateur final déployées sur la plateforme :

- **EServices** : Plateforme de services e-gouvernement pour les citoyens
- **GCO** : Portail de gestion des opérations

### Zones Réseau

L'architecture est segmentée en trois zones réseau :

| Zone      | Objectif                                         | Composants Clés                                              |
| --------- | ------------------------------------------------ | ------------------------------------------------------------ |
| **LAN**   | Hébergement interne d'applications et middleware | Cluster RKEAPPS, cluster RKEMIDDLEWARE, LBLAN, LBINTEGRATION |
| **INFRA** | Services d'infrastructure de base                | Gogs, Docker Registry, HashiCorp Vault, Monitoring           |
| **DMZ**   | Services exposés à l'extérieur                   | Cluster RKEDMZ, Gravitee DMZ, LBDMZ                          |

Chaque zone a son propre VLAN, sous-réseau, passerelle et configuration DNS pour une isolation complète.

### Trois Clusters Kubernetes

La plateforme déploie trois clusters RKE2 Kubernetes séparés :

1. **RKE2-APPS** : Exécute les applications métier (eServices, GCO)
2. **RKE2-MIDDLEWARE** : Exécute les services middleware de support (Keycloak, Kafka, MinIO, n8n, Flowable)
3. **RKE2-DMZ** : Exécute l'API Gateway (Gravitee DMZ) dans la zone DMZ pour le trafic externe

Les trois clusters sont gérés par une seule instance **Rancher** pour des opérations unifiées.

---

!!! tip "Prochaines Étapes"
Continuez vers le [Processus de Déploiement](deployment-process.md) pour comprendre comment la plateforme est construite de bout en bout.
