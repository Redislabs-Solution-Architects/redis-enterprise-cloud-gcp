package main

import (
	"github.com/RedisLabs/pulumi-rediscloud/sdk/go/rediscloud"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi/config"
)

func main() {
	pulumi.Run(func(ctx *pulumi.Context) error {
		config := config.New(ctx, "")

		cardType := config.Require("cardType")
		lastFourNumbers := config.Require("lastFourNumbers")

		card, err := rediscloud.GetPaymentMethod(ctx, &rediscloud.GetPaymentMethodArgs{
			CardType:        &cardType,
			LastFourNumbers: &lastFourNumbers,
		}, nil)

		if err != nil {
			return err
		}

		cardId := card.Id

		subscription, err := rediscloud.NewSubscription(ctx, "subscription", &rediscloud.SubscriptionArgs{
                        Name:            pulumi.String("pulumi-sub"),
			PaymentMethod:   pulumi.String("credit-card"),
			PaymentMethodId: pulumi.String(cardId),
			CloudProvider: &rediscloud.SubscriptionCloudProviderArgs{
                                Provider: pulumi.String("GCP"),
				Regions: rediscloud.SubscriptionCloudProviderRegionArray{
					&rediscloud.SubscriptionCloudProviderRegionArgs{
						Region:                    pulumi.String("us-west1"),
						NetworkingDeploymentCidr:  pulumi.String("10.0.0.0/24"),
						MultipleAvailabilityZones: pulumi.Bool(true),
						PreferredAvailabilityZones: pulumi.StringArray{
							pulumi.String("us-west1-a"),
							pulumi.String("us-west1-b"),
							pulumi.String("us-west1-c"),
						},
					},
				},
			},
			CreationPlan: &rediscloud.SubscriptionCreationPlanArgs{
				MemoryLimitInGb:            pulumi.Float64(10),
				Quantity:                   pulumi.Int(1),
				Replication:                pulumi.Bool(true),
				SupportOssClusterApi:       pulumi.Bool(false),
				ThroughputMeasurementBy:    pulumi.String("operations-per-second"),
				ThroughputMeasurementValue: pulumi.Int(20000),
				Modules:                    pulumi.StringArray{pulumi.String("RedisJSON")},
			},
		})
		if err != nil {
			return err
		}
		_, err = rediscloud.NewSubscriptionDatabase(ctx, "database", &rediscloud.SubscriptionDatabaseArgs{
			SubscriptionId:             subscription.ID(),
			Protocol:                   pulumi.String("redis"),
			MemoryLimitInGb:            pulumi.Float64(10),
			DataPersistence:            pulumi.String("aof-every-1-second"),
			ThroughputMeasurementBy:    pulumi.String("operations-per-second"),
			ThroughputMeasurementValue: pulumi.Int(20000),
			SupportOssClusterApi:       pulumi.Bool(false),
			Replication:                pulumi.Bool(true),
		})
		if err != nil {
			return err
		}
		return nil
	})
}
