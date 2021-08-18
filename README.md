# redis-enterprise-cloud-gcp

This repo contains anything about fully managed Redis Enterprise DBaaS on Google Cloud Platform

* [Pricing](/pricing/pricing.md) estimate for running fully managed Redis Enterprise DBaaS on GCP
* Provisioning a fully managed Redis Enterprise DBaaS on GCP subscription using [Terraform](/terraform//terraform.md)
* [Monitoring](/monitoring//monitoring.md) a fully managed Redis Enterprise DBaaS subscription using Promethues/Grafana
* Setting up [Active-Passive](/active-passive//active-passive-geo-distribution.md) Geo Distribution between fully managed Redis Enterprise DBaaS subscriptions
* Deployment of Redis Enterprise via GCP Marketplace on Anthos managed [AKS cluster](/marketplace/aks/aks-deploy.md)
* Deployment of Redis Enterprise via GCP Marketplace on Anthos managed [EKS cluster](/marketplace/eks/eks-deploy.md)
* Accessing a Redis Enterprise Cluster's [API endpoint](/gke/access-via-asm-ingress-rec/README.md) from outside a GKE cluster (Through Anthos Service Mesh Ingress) 
* Accessing a [non-TLS](/gke/access-via-asm-non-tls/README.md) enabled Redis Enterprise database from outside a GKE cluster through Anthos Service Mesh
* Accessing a [mTLS-enabled](/gke/access-via-asm-ingress/README.md) Redis Enterprise database from outside a GKE cluster through Anthos Service Mesh / Nginx
* Accessing a Redis Enterprise Database from outside a GKE cluster (Through Anthos Service Mesh Ingress) via [one-way SSL and user creds](/gke/access-via-asm-one-way-ssl%2Bcreds/README.md) (username/password)
* Accessing a Redis Enterprise Database from Google Cloud Platform's Kf environment through user provided service - [TLS Origination's Istio Egress Gateway Edition](/gke/access-via-asm-kf-tls-origination/README.md)
* Accessing a Redis Enterprise database from outside a GKE cluster through [Nginx](/gke/access-via-nginx/README.md)
* Setting up Active-Active geo replciation with GKE clusters (Coming...)

  
Redis Labs proprietary, subject to the Redis Enterprise Software and/or Cloud Services license
