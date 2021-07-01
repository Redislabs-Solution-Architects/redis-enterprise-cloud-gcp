# redis-enterprise-cloud-gcp

This repo contains anything about fully managed Redis Enterprise DBaaS on Google Cloud Platform

* [Pricing](./pricing.md) estimate for running fully managed Redis Enterprise DBaaS on GCP
* Provisioning a fully managed Redis Enterprise DBaaS on GCP subscription using [Terraform](./terraform.md)
* [Monitoring](./monitoring.md) a fully managed Redis Enterprise DBaaS subscription using Promethues/Grafana
* Setting up [Active-Passive](./active-passive-geo-distribution.md) Geo Distribution between fully managed Redis Enterprise DBaaS subscriptions
* Deployment of Redis Enterprise via GCP Marketplace on Anthos managed [AKS cluster](./aks/aks-deploy.md)
* Deployment of Redis Enterprise via GCP Marketplace on Anthos managed [EKS cluster](./eks/eks-deploy.md)
* Accessing a [non-TLS](./access-via-asm-non-tls/README.md) enabled Redis Enterprise database from outside a GKE cluster through Anthos Service Mesh
* Accessing a [TLS-enabled](./access-via-asm-ingress/README.md) Redis Enterprise database from outside a GKE cluster through Anthos Service Mesh / Nginx
* Accessing a Redis Enterprise database from outside a GKE cluster through [Nginx](./access-via-nginx/README.md)
* Setting up Active-Active geo replciation with GKE clusters (Coming...)

  
Redis Labs proprietary, subject to the Redis Enterprise Software and/or Cloud Services license
