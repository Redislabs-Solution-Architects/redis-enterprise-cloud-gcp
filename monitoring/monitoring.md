## Set up Prometheus/Grafana to monitor your Google Cloud Platform Marketplace (GCP MP) subscription

### Prerequisites
1. A subscription has been created through your GCP MP's Redis Enterprise purchase 
2. One or more databases have been created in the subscription
3. Network peering has been set up between your GCP project's VPC and the subscription project VPC

### Procedures
1. Set up firewall rules allowing SSH and traffic to Prometheus and Grafana
2. Create a VM in your GCP project to install Prometheus and Grafana 
3. Install and configure Prometheus to ingest monitoring data from the subscription
4. Install Grafana and configure monitoring dashboards

#### Set up firewal rules allowing SSH and traffic to Prometheus and Grafana
The firewall rules for your GCP project's VPC should look like the following:
![firewall rules](./img/firewall_rules.png)

#### Create a VM in your GCP project to install Prometheus and Grafana
First off, make sure your VM is in the VPC network peered with your Redis Enterprise for GCP MP subscription. See below.
![monitoring vm](./img/monitoring_vm.png)
