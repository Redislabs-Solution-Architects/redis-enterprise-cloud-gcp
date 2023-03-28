# [WORK IN PROGRESS] Active-Active Setup with Anthos Service Mesh

## High Level Workflow
The following is the high level workflow which you will follow:
1. Clone this repo
2. Create two Active-Active participating GKE clusters
3. Install Anthos Service Mesh (ASM) and Ingress Gateway
4. Install/Configure Redis Enterprise Operator & Redis Enteprise Cluster
5. ..
6. ..


### 1. Clone this repo 
```shell script
git clone https://github.com/Redislabs-Solution-Architects/redis-enterprise-cloud-gcp
cd redis-enterprise-asm-ingress/gke/asm-active-active
```
    
### 2. Create two Active-Active participating GKE clusters
#### Create first GKE cluster:
```shell script
export PROJECT_ID=$(gcloud info --format='value(config.project)')
export CLUSTER_LOCATION_01=us-central1
export CLUSTER_NAME_01="glau-gke-cluster-$CLUSTER_LOCATION_01"
export VPC_NETWORK="glau-vpc-network"
export SUBNETWORK_01="us-central1-subnet"

gcloud container clusters create $CLUSTER_NAME_01 \
 --region=$CLUSTER_LOCATION_01 --num-nodes=1 \
 --image-type=COS_CONTAINERD \
 --machine-type=e2-standard-8 \
 --network=$VPC_NETWORK \
 --subnetwork=$SUBNETWORK_01 \
 --enable-ip-alias \
 --workload-pool=${PROJECT_ID}.svc.id.goog
```

#### Create second GKE cluster:
```shell script
export CLUSTER_LOCATION_02=us-west1
export CLUSTER_NAME_02="glau-gke-cluster-$CLUSTER_LOCATION_02"
export SUBNETWORK_02="us-west1-subnet"

gcloud container clusters create $CLUSTER_NAME_02 \
 --region=$CLUSTER_LOCATION_02 --num-nodes=1 \
 --image-type=COS_CONTAINERD \
 --machine-type=e2-standard-8 \
 --network=$VPC_NETWORK \
 --subnetwork=$SUBNETWORK_02 \
 --enable-ip-alias \
 --workload-pool=${PROJECT_ID}.svc.id.goog
```
    
### 3. Install Anthos Service Mesh (ASM) and Ingress Gateway
Download ASM install script:
```shell script
curl https://storage.googleapis.com/csm-artifacts/asm/asmcli_1.16 > asmcli
chmod +x asmcli
```

#### Set up first GKE cluster:
```shell script
gcloud container clusters get-credentials $CLUSTER_NAME_01 --region $CLUSTER_LOCATION_01 --project $PROJECT_ID
```
Run `asmcli validate` to make sure that your project and cluster are set up as required to install Anthos Service Mesh:
```shell script
./asmcli validate \
  --project_id $PROJECT_ID \
  --cluster_name $CLUSTER_NAME_01 \
  --cluster_location $CLUSTER_LOCATION_01 \
  --fleet_id $PROJECT_ID \
  --output_dir ./asm_output_01
```
Install Anthos Service Mesh:
```shell script
./asmcli install \
  --project_id $PROJECT_ID\
  --cluster_name $CLUSTER_NAME_01 \
  --cluster_location $CLUSTER_LOCATION_01\
  --output_dir ./asm_output_01 \
  --enable_all \
  --ca mesh_ca
```
On success, you should have output similar to the following:
```shell script
asmcli: ...done!
asmcli:
asmcli: *****************************
client version: 1.16.2-asm.2
control plane version: 1.16.2
data plane version: none
asmcli: *****************************
asmcli: The ASM control plane installation is now complete.
asmcli: To enable automatic sidecar injection on a namespace, you can use the following command:
asmcli: kubectl label namespace <NAMESPACE> istio-injection- istio.io/rev=asm-1162-2 --overwrite
asmcli: If you use 'istioctl install' afterwards to modify this installation, you will need
asmcli: to specify the option '--set revision=asm-1162-2' to target this control plane
asmcli: instead of installing a new one.
asmcli: To finish the installation, enable Istio sidecar injection and restart your workloads.
asmcli: For more information, see:
asmcli: https://cloud.google.com/service-mesh/docs/proxy-injection
asmcli: The ASM package used for installation can be found at:
asmcli: /home/gilbert_lau/work/asm_output_01/asm
asmcli: The version of istioctl that matches the installation can be found at:
asmcli: /home/gilbert_lau/work/asm_output_01/istio-1.16.2-asm.2/bin/istioctl
asmcli: A symlink to the istioctl binary can be found at:
asmcli: /home/gilbert_lau/work/asm_output_01/istioctl
asmcli: The combined configuration generated for installation can be found at:
asmcli: /home/gilbert_lau/work/asm_output_01/asm-1162-2-manifest-raw.yaml
asmcli: The full, expanded set of kubernetes resources can be found at:
asmcli: /home/gilbert_lau/work/asm_output_01/asm-1162-2-manifest-expanded.yaml
asmcli: *****************************
asmcli: Successfully installed ASM.
```
    
Install Istio Ingress Gateway:
```shell script
kubectl config set-context --current --namespace=istio-system
export asm_version=$(kubectl get deploy -n istio-system -l app=istiod \
  -o=jsonpath='{.items[*].metadata.labels.istio\.io\/rev}''{"\n"}')
kubectl label namespace istio-system istio-injection=enabled istio.io/rev=$asm_version --overwrite
kubectl apply -f ./asm_output_01/samples/gateways/istio-ingressgateway
kubectl apply -f ./asm_output_01/samples/gateways/istio-ingressgateway/autoscalingv2/autoscaling-v2.yaml
```
    
Create a Private DNS zone in your Google Cloud envrionment:
```shell script
export DNS_ZONE=private-redis-zone
export DNS_SUFFIX=istio.k8s.redis.com
gcloud dns managed-zones create $DNS_ZONE \
    --description=$DNS_ZONE \
    --dns-name=$DNS_SUFFIX \
    --networks=$VPC_NETWORK \
    --labels=project=$PROJECT_ID \
    --visibility=private
```
Create DNS entry in your Google Cloud environment:
```shell script
export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway \
       -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
gcloud dns record-sets create *.${CLUSTER_LOCATION_01}.${DNS_SUFFIX}. \
    --type=A --ttl=300 --rrdatas=${INGRESS_HOST} --zone=$DNS_ZONE 
```
    
#### Set up second GKE cluster:
```shell script
gcloud container clusters get-credentials $CLUSTER_NAME_02 --region $CLUSTER_LOCATION_02 --project $PROJECT_ID
```
Run `asmcli validate` to make sure that your project and cluster are set up as required to install Anthos Service Mesh:
```shell script
./asmcli validate \
  --project_id $PROJECT_ID \
  --cluster_name $CLUSTER_NAME_02 \
  --cluster_location $CLUSTER_LOCATION_02 \
  --fleet_id $PROJECT_ID \
  --output_dir ./asm_output_02
```
Install Anthos Service Mesh:
```shell script
./asmcli install \
  --project_id $PROJECT_ID\
  --cluster_name $CLUSTER_NAME_02 \
  --cluster_location $CLUSTER_LOCATION_02\
  --output_dir ./asm_output_02 \
  --enable_all \
  --ca mesh_ca
  ```
    
Install Istio Ingress Gateway:
```shell script
kubectl config set-context --current --namespace=istio-system
export asm_version=$(kubectl get deploy -n istio-system -l app=istiod \
  -o=jsonpath='{.items[*].metadata.labels.istio\.io\/rev}''{"\n"}')
kubectl label namespace istio-system istio-injection=enabled istio.io/rev=$asm_version --overwrite
kubectl apply -f ./asm_output_02/samples/gateways/istio-ingressgateway
kubectl apply -f ./asm_output_02/samples/gateways/istio-ingressgateway/autoscalingv2/autoscaling-v2.yaml
```
    
Create DNS entry in your Google Cloud environment:
```shell script
export DNS_ZONE=private-redis-zone
export DNS_SUFFIX=istio.k8s.redis.com
export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway \
       -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
gcloud dns record-sets create *.${CLUSTER_LOCATION_02}.${DNS_SUFFIX}. \
    --type=A --ttl=300 --rrdatas=${INGRESS_HOST} --zone=$DNS_ZONE 
```
    
### 4. Install/Configure Redis Enterprise Operator & Redis Enteprise Cluster
#### Install Redis Enterprise Operator & Redis Enterprise Cluster on the first GKE cluster:
```shell script
gcloud container clusters get-credentials $CLUSTER_NAME_01 --region $CLUSTER_LOCATION_01 --project $PROJECT_ID

kubectl create namespace $CLUSTER_LOCATION_01
kubectl config set-context --current --namespace=$CLUSTER_LOCATION_01

VERSION=v6.4.2-4 
kubectl apply -f https://raw.githubusercontent.com/RedisLabs/redis-enterprise-k8s-docs/$VERSION/bundle.yaml

kubectl apply -f - <<EOF
apiVersion: "app.redislabs.com/v1"
kind: "RedisEnterpriseCluster"
metadata:
  name: redis-enterprise
spec:
  nodes: 3
EOF
```
    
##### Enable Active-Active controllers:
```shell script
kubectl apply -f https://raw.githubusercontent.com/RedisLabs/redis-enterprise-k8s-docs/master/crds/reaadb_crd.yaml
kubectl apply -f https://raw.githubusercontent.com/RedisLabs/redis-enterprise-k8s-docs/master/crds/rerc_crd.yaml
kubectl patch cm  operator-environment-config --type merge --patch "{\"data\": \
    {\"ACTIVE_ACTIVE_DATABASE_CONTROLLER_ENABLED\":\"true\", \
    \"REMOTE_CLUSTER_CONTROLLER_ENABLED\":\"true\"}}"
```
    
##### Configure Istio for Redis Enterprise Kubernetes operator to allow external access to Redis Enterprise databases:
```shell script
export DNS_SUFFIX=istio.k8s.redis.com

kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: redis-gateway
spec:
  selector:
    istio: ingressgateway 
  servers:
  - hosts:
    - '*.${CLUSTER_LOCATION_01}.${DNS_SUFFIX}'
    port:
      name: https
      number: 443
      protocol: HTTPS
    tls:
      mode: PASSTHROUGH
EOF
```
```shell script
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: redis-vs
spec:
  gateways:
  - redis-gateway
  hosts:
  - '*.${CLUSTER_LOCATION_01}.${DNS_SUFFIX}'
  tls:
  - match:
    - port: 443
      sniHosts:
      - api.${CLUSTER_LOCATION_01}.${DNS_SUFFIX}
    route:
    - destination:
        host: redis-enterprise
        port:
          number: 9443
  - match:
    - port: 443
      sniHosts:
      - redis-enterprise-ui.${CLUSTER_LOCATION_01}.${DNS_SUFFIX}
    route:
    - destination:
        host: redis-enterprise-ui
        port:
          number: 8443
EOF
```
Verify Redis Enterprise endpoints are accessible through gateway:
```shell script
kubectl describe svc istio-ingressgateway -n istio-system
```
Make sure Endpoints lines are not empty from the output:
```shell script
Name:                     istio-ingressgateway
Namespace:                istio-system
Labels:                   app=istio-ingressgateway
                          istio=ingressgateway
Annotations:              cloud.google.com/neg: {"ingress":true}
Selector:                 app=istio-ingressgateway,istio=ingressgateway
Type:                     LoadBalancer
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.88.4.232
IPs:                      10.88.4.232
LoadBalancer Ingress:     34.71.227.19
Port:                     status-port  15021/TCP
TargetPort:               15021/TCP
NodePort:                 status-port  31523/TCP
Endpoints:                10.84.0.6:15021,10.84.1.10:15021,10.84.2.5:15021
Port:                     http2  80/TCP
TargetPort:               80/TCP
NodePort:                 http2  30237/TCP
Endpoints:                10.84.0.6:80,10.84.1.10:80,10.84.2.5:80
Port:                     https  443/TCP
TargetPort:               443/TCP
NodePort:                 https  31669/TCP
Endpoints:                10.84.0.6:443,10.84.1.10:443,10.84.2.5:443
Session Affinity:         None
External Traffic Policy:  Cluster
Events:
  Type    Reason                Age   From                Message
  ----    ------                ----  ----                -------
  Normal  EnsuringLoadBalancer  17m   service-controller  Ensuring load balancer
  Normal  EnsuredLoadBalancer   17m   service-controller  Ensured load balancer
```
    
##### Hooking up the Admission controller directly with Kubernetes:
Wait for the secret to be created
```shell script
kubectl get secret admission-tls
NAME            TYPE     DATA   AGE
admission-tls   Opaque   2      2m43s
```
Enable the Kubernetes webhook using the generated certificate stored in a kubernetes secret:
**NOTE**: One must replace REPLACE_WITH_NAMESPACE in the following command with the namespace the REC was installed into.

```shell script
# save cert
wget https://raw.githubusercontent.com/RedisLabs/redis-enterprise-k8s-docs/master/admission/webhook.yaml
CERT=`kubectl get secret admission-tls -o jsonpath='{.data.cert}'`
sed "s/NAMESPACE_OF_SERVICE_ACCOUNT/$CLUSTER_LOCATION_01/g" webhook.yaml | kubectl create -f -
# create patch file
cat > modified-webhook.yaml <<EOF
webhooks:
- name: redisenterprise.admission.redislabs
  clientConfig:
    caBundle: $CERT
  admissionReviewVersions: ["v1beta1"]
EOF
# patch webhook with caBundle
kubectl patch ValidatingWebhookConfiguration redis-enterprise-admission --patch "$(cat modified-webhook.yaml)"
```
                
#### Install Redis Enterprise Operator & Redis Enterprise Cluster on the second GKE cluster:
```shell script
gcloud container clusters get-credentials $CLUSTER_NAME_02 --region $CLUSTER_LOCATION_02 --project $PROJECT_ID

kubectl create namespace $CLUSTER_LOCATION_02
kubectl config set-context --current --namespace=$CLUSTER_LOCATION_02

VERSION=v6.4.2-4
kubectl apply -f https://raw.githubusercontent.com/RedisLabs/redis-enterprise-k8s-docs/$VERSION/bundle.yaml

kubectl apply -f - <<EOF
apiVersion: "app.redislabs.com/v1"
kind: "RedisEnterpriseCluster"
metadata:
  name: redis-enterprise
spec:
  nodes: 3
EOF
```
         
##### Enable Active-Active controllers:
```shell script
kubectl apply -f https://raw.githubusercontent.com/RedisLabs/redis-enterprise-k8s-docs/master/crds/reaadb_crd.yaml
kubectl apply -f https://raw.githubusercontent.com/RedisLabs/redis-enterprise-k8s-docs/master/crds/rerc_crd.yaml
kubectl patch cm  operator-environment-config --type merge --patch "{\"data\": \
    {\"ACTIVE_ACTIVE_DATABASE_CONTROLLER_ENABLED\":\"true\", \
    \"REMOTE_CLUSTER_CONTROLLER_ENABLED\":\"true\"}}"
```
    
##### Configure Istio for Redis Enterprise Kubernetes operator to allow external access to Redis Enterprise databases:
```shell script
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: redis-gateway
spec:
  selector:
    istio: ingressgateway 
  servers:
  - hosts:
    - '*.${CLUSTER_LOCATION_02}.${DNS_SUFFIX}'
    port:
      name: https
      number: 443
      protocol: HTTPS
    tls:
      mode: PASSTHROUGH
EOF
```
```shell script
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: redis-vs
spec:
  gateways:
  - redis-gateway
  hosts:
  - '*.${CLUSTER_LOCATION_02}.${DNS_SUFFIX}'
  tls:
  - match:
    - port: 443
      sniHosts:
      - api.${CLUSTER_LOCATION_02}.${DNS_SUFFIX}
    route:
    - destination:
        host: redis-enterprise
        port:
          number: 9443
  - match:
    - port: 443
      sniHosts:
      - redis-enterprise-ui.${CLUSTER_LOCATION_02}.${DNS_SUFFIX}
    route:
    - destination:
        host: redis-enterprise-ui
        port:
          number: 8443
EOF
```
Verify Redis Enterprise endpoints are accessible through gateway:
```shell script
kubectl describe svc istio-ingressgateway -n istio-system
```
    
##### Hooking up the Admission controller directly with Kubernetes:
Wait for the secret to be created
```shell script
kubectl get secret admission-tls
NAME            TYPE     DATA   AGE
admission-tls   Opaque   2      2m43s
```
Enable the Kubernetes webhook using the generated certificate stored in a kubernetes secret:
**NOTE**: One must replace REPLACE_WITH_NAMESPACE in the following command with the namespace the REC was installed into.

```shell script
# save cert
wget https://raw.githubusercontent.com/RedisLabs/redis-enterprise-k8s-docs/master/admission/webhook.yaml
CERT=`kubectl get secret admission-tls -o jsonpath='{.data.cert}'`
sed "s/NAMESPACE_OF_SERVICE_ACCOUNT/$CLUSTER_LOCATION_02/g" webhook.yaml | kubectl create -f -
# create patch file
cat > modified-webhook.yaml <<EOF
webhooks:
- name: redisenterprise.admission.redislabs
  clientConfig:
    caBundle: $CERT
  admissionReviewVersions: ["v1beta1"]
EOF
# patch webhook with caBundle
kubectl patch ValidatingWebhookConfiguration redis-enterprise-admission --patch "$(cat modified-webhook.yaml)"
```
    
### 5. Create secrets for RedisEnterpriseRemoteCluster resources
#### Create secret for the first Redis Enterprise (Remote) cluster
```shell script
# Connect to the first GKE cluster and Redis Enterprise namespace
gcloud container clusters get-credentials $CLUSTER_NAME_01 --region $CLUSTER_LOCATION_01 --project $PROJECT_ID
kubectl config set-context --current --namespace=$CLUSTER_LOCATION_01

# Retrieve Redis Enterprise Cluster's creds
export REDIS_ENTERPRISE_PWD_01=$(kubectl get secrets -n $CLUSTER_LOCATION_01 redis-enterprise -o jsonpath="{.data.password}")
export REDIS_ENTERPRISE_USERNAME_01=$(kubectl get secrets -n $CLUSTER_LOCATION_01 redis-enterprise -o jsonpath="{.data.username}")
export REDIS_ENTERPRISE_REMOTE_CLUSTER_01=redis-enterprise-rerc-$CLUSTER_LOCATION_01

# Store creds in a secret
kubectl apply -f - <<EOF
apiVersion: v1
data:
  password: $REDIS_ENTERPRISE_PWD_01
  username: $REDIS_ENTERPRISE_USERNAME_01
kind: Secret
metadata:
  name: $REDIS_ENTERPRISE_REMOTE_CLUSTER_01
type: Opaque
EOF
```
   
#### Create secret for the second Redis Enterprise (Remote) cluster
```shell script
# Connect to the second GKE cluster and Redis Enterprise namespace
gcloud container clusters get-credentials $CLUSTER_NAME_02 --region $CLUSTER_LOCATION_02 --project $PROJECT_ID
kubectl config set-context --current --namespace=$CLUSTER_LOCATION_02

# Retrieve Redis Enterprise Cluster's creds
export REDIS_ENTERPRISE_PWD_02=$(kubectl get secrets -n $CLUSTER_LOCATION_02 redis-enterprise -o jsonpath="{.data.password}")
export REDIS_ENTERPRISE_USERNAME_02=$(kubectl get secrets -n $CLUSTER_LOCATION_02 redis-enterprise -o jsonpath="{.data.username}")
export REDIS_ENTERPRISE_REMOTE_CLUSTER_02=redis-enterprise-rerc-$CLUSTER_LOCATION_02

# Store creds in a secret
kubectl apply -f - <<EOF
apiVersion: v1
data:
  password: $REDIS_ENTERPRISE_PWD_02
  username: $REDIS_ENTERPRISE_USERNAME_02
kind: Secret
metadata:
  name: $REDIS_ENTERPRISE_REMOTE_CLUSTER_02
type: Opaque
EOF
```
    
    
### 6. Create RedisEnterpriseRemoteCluster resources
#### Create Redis Enterprise Remote Cluster resource for the first REC
```shell script
# Connect to the first GKE cluster and Redis Enterprise namespace
gcloud container clusters get-credentials $CLUSTER_NAME_01 --region $CLUSTER_LOCATION_01 --project $PROJECT_ID
kubectl config set-context --current --namespace=$CLUSTER_LOCATION_01
export DNS_SUFFIX=istio.k8s.redis.com

kubectl apply -f - <<EOF
apiVersion: app.redislabs.com/v1alpha1
kind: RedisEnterpriseRemoteCluster
metadata:
  name: $REDIS_ENTERPRISE_REMOTE_CLUSTER_01
spec:
  recName: redis-enterprise
  recNamespace: $CLUSTER_LOCATION_01
  apiFqdnUrl: api.${CLUSTER_LOCATION_01}.${DNS_SUFFIX}
  dbFqdnSuffix: -db.${CLUSTER_LOCATION_01}.${DNS_SUFFIX}
  secretName: $REDIS_ENTERPRISE_REMOTE_CLUSTER_01
EOF
```
    
#### Create Redis Enterprise Remote Cluster resource for the second REC
```shell script
# Connect to the second GKE cluster and Redis Enterprise namespace
gcloud container clusters get-credentials $CLUSTER_NAME_01 --region $CLUSTER_LOCATION_02 --project $PROJECT_ID
kubectl config set-context --current --namespace=$CLUSTER_LOCATION_02
export DNS_SUFFIX=istio.k8s.redis.com

kubectl apply -f - <<EOF
apiVersion: app.redislabs.com/v1alpha1
kind: RedisEnterpriseRemoteCluster
metadata:
  name: $REDIS_ENTERPRISE_REMOTE_CLUSTER_02
spec:
  recName: redis-enterprise
  recNamespace: $CLUSTER_LOCATION_02
  apiFqdnUrl: api.${CLUSTER_LOCATION_02}.${DNS_SUFFIX}
  dbFqdnSuffix: -db.${CLUSTER_LOCATION_02}.${DNS_SUFFIX}
  secretName: $REDIS_ENTERPRISE_REMOTE_CLUSTER_02
EOF
```
    
### 7. Create Active-Active database (REAADB) 
https://docs.redis.com/latest/kubernetes/active-active/preview/create-reaadb/ 