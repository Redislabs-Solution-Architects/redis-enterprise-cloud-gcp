import pulumi
from pulumi import Output
import pulumi_gcp as gcp
import pulumi_rediscloud

config = pulumi.Config()

subscription = pulumi_rediscloud.Subscription(
    "my-subscription",
    name="my-subscription",
    payment_method="marketplace",
    memory_storage="ram",
    cloud_provider=pulumi_rediscloud.SubscriptionCloudProviderArgs(
        provider="GCP",
        regions=[
            pulumi_rediscloud.SubscriptionCloudProviderRegionArgs(
                region="us-west1",
                multiple_availability_zones=True,
                networking_deployment_cidr="10.0.0.0/24",
                preferred_availability_zones=["us-west1-a", "us-west1-b", "us-west1-c"],
            )
        ]
    ),
    creation_plan=pulumi_rediscloud.SubscriptionCreationPlanArgs(
        memory_limit_in_gb=1,
        quantity=1,
        replication=True,
        support_oss_cluster_api=False,
        throughput_measurement_by="operations-per-second",
        throughput_measurement_value=20000,
        modules=["RedisJSON"],
    ),
)

database = pulumi_rediscloud.SubscriptionDatabase(
    "my-db",
    name="my-db",
    subscription_id=subscription.id,
    protocol="redis",
    memory_limit_in_gb=1,
    data_persistence="aof-every-1-second",
    throughput_measurement_by="operations-per-second",
    throughput_measurement_value=20000,
    replication=True,
    modules=[
        pulumi_rediscloud.SubscriptionDatabaseModuleArgs(
            name="RedisJSON",
        )
    ],
)

network = gcp.compute.get_network(project="central-beach-194106", name="glau-vpc-network")

my_peering_subscription_peering = pulumi_rediscloud.SubscriptionPeering("examplepeeringSubscriptionPeering",
    subscription_id=subscription.id,
    provider_name="GCP",
    gcp_project_id=network.project,
    gcp_network_name=network.name)

peer_network = Output.all(project_id = my_peering_subscription_peering.gcp_redis_project_id, project_network=my_peering_subscription_peering.gcp_redis_network_name) \
    .apply(lambda args: f"https://www.googleapis.com/compute/v1/projects/{args['project_id']}/global/networks/{args['project_network']}")

my_peering_network_peering = gcp.compute.NetworkPeering("mypeeringnetworkpeering",
    network=network.self_link, peer_network=peer_network)`
