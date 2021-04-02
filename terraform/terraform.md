### This folder contains terraform scripts to provision fully managed Redis Enterprise by Redis Labs on Google Cloud Platform (GCP)

There are two ways to consume fully managed Redis Enterprise on GCP:
1. Through Google Cloud Platform Marketplace
2. Through Redis Enterprise Cloud

You will find two terraform scripts one for each way of consumption in this repo
* The [terraform script](./gcp-mp/gcp-mp.tf) to provision in a GCP Marketplace subscription at https://console.cloud.google.com/
* The [terraform script](./rec-gcp/rec-gcp.tf) to provision through Redis Enterprise Cloud at https://app.redislabs.com/

The following links provide additional information w.r.t Redis Enterprise Cloud's Terraform provider
1. The github [repo](https://github.com/RedisLabs/terraform-provider-rediscloud) for the Redis Enterprise Cloud's Terraform provider
2. The Redis Enterprise Cloud's Terraform Provider [listing](https://registry.terraform.io/providers/RedisLabs/rediscloud/latest) in official Terraform Registry
3. A [blog](https://redislabs.com/blog/provision-manage-redis-enterprise-cloud-hashicorp-terraform/) written by a Redis Labs' product manager demonstrating an example of how to use the Redis Enterprise Cloud's Terraform provider.

