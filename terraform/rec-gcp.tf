#
# Set the following variables in your shell environment:
# export GOOGLE_APPLICATION_CREDENTIALS=<your Google APIs credentials>
# export REDISCLOUD_ACCESS_KEY=<your Redis Enterrpise Cloud api access key>
# export REDISCLOUD_SECRET_KEY=<your Redis Enterprise Cloud secret key>
#
# How to deploy:
# % terraform init
# % terraform plan
# % terraform apply
#
# How to tear down:
# % terraform destroy
# 

terraform {
 required_providers {
   rediscloud = {
     source = "RedisLabs/rediscloud"
     version = "0.2.1"
   }
 }
}

# Provide your credit card details
data "rediscloud_payment_method" "card" {
 card_type = "Visa"
 last_four_numbers = "1234"
}
 
# Generates a random password for the database
resource "random_password" "passwords" {
 count = 2
 length = 20
 upper = true
 lower = true
 number = true
 special = false
}
 
resource "rediscloud_subscription" "example" {
 name = "gilbert-demo-tf-subscription"
 payment_method_id = data.rediscloud_payment_method.card.id
 memory_storage = "ram"
 
 cloud_provider {
   #Running in GCP on Redis Labs resources
   provider = "GCP"
   cloud_account_id = 1
   region {
     region = "us-west1"
     networking_deployment_cidr = "192.168.0.0/24"
     preferred_availability_zones = ["us-west1-a"]
   }
 }
 database {
   name = "db-json"
   protocol = "redis"
   memory_limit_in_gb = 1
   replication = true
   data_persistence = "aof-every-1-second"
   module {
       name = "RedisJSON"
   }
   throughput_measurement_by = "operations-per-second"
   throughput_measurement_value = 10000
   password = random_password.passwords[1].result
 }
}

data "google_compute_network" "network" {
  project = "my-project-id"
  name = "my-vpc-network"
}

resource "rediscloud_subscription_peering" "example-peering" {
  subscription_id = rediscloud_subscription.example.id
  provider_name = "GCP"
  gcp_project_id = data.google_compute_network.network.project
  gcp_network_name = data.google_compute_network.network.name
}

resource "google_compute_network_peering" "example-peering" {
  name         = "glau-peering-gcp-example"
  network      = data.google_compute_network.network.self_link
  peer_network = "https://www.googleapis.com/compute/v1/projects/${rediscloud_subscription_peering.example-peering.gcp_redis_project_id}/global/networks/${rediscloud_subscription_peering.example-peering.gcp_redis_network_name}"
}

