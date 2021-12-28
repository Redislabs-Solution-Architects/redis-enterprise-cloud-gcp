# Accessing a TLS-enabled Redis Enterprise database (REDB) in GCP Marketplace from an ASM GKE cluster via Istio proxy sidecar's TLS origination

## High Level Workflow
The following is the high level workflow which you will follow:
1. Clone this repo
2. Create a GKE cluster
3. Install Anthos Service Mesh (ASM)
4. Create a TLS-enabled Redis Enterprise database (REDB) from GCP Marketplace
5. Create a K8 secret to store the client certificate, client key and server certificate for mutual TLS connection
6. Deploy a Redis client on the GKE cluster
7. Create Istio resources (ServiceEntry and DestinationRule) for the TLS-enabled REDB
8. Validate Istio proxy sidecar's TLS origination for a secured mTLS REDB connection


#### 1. Clone this repo 
```
git clone https://github.com/Redislabs-Solution-Architects/redis-enterprise-cloud-gcp
cd redis-enterprise-asm-ingress/gke/access-via-asm-gcp-mp-tls-redb
```


#### 2. Create a GKE cluster
```
export PROJECT_ID=$(gcloud info --format='value(config.project)')
export CLUSTER_NAME="glau-asm-gke-cluster"
export CLUSTER_LOCATION=us-west1-a

./create_cluster.sh $CLUSTER_NAME $CLUSTER_LOCATION
```


#### 3. Install Anthos Service Mesh (ASM)
Download ASM installation script
```
curl https://storage.googleapis.com/csm-artifacts/asm/install_asm_1.10 > install_asm
curl https://storage.googleapis.com/csm-artifacts/asm/install_asm_1.10.sha256 > install_asm.sha256
sha256sum -c --ignore-missing install_asm.sha256
chmod +x install_asm
```  
Note: If you are running the ASM install on MacOS, you will need to install kpt as follows:  
```
gcloud components install kpt
```  
Install Anthos Service Mesh (ASM)  
Please make sure you have all the required [GCP IAM permissions](https://cloud.google.com/service-mesh/docs/installation-permissions) before running the script below.  
```
./install_asm \
  --project_id $PROJECT_ID \
  --cluster_name $CLUSTER_NAME  \
  --cluster_location $CLUSTER_LOCATION  \
  --mode install \
  --output_dir ./asm-downloads \
  --enable_all
```


#### 4. Create a TLS-enabled Redis Enterprise database (REDB) from GCP Marketplace
Assuming you have created a REDB instance in GCP Marketplace. The following will demonstrate to enable mTLS and download the required key and certificates for secure connection.  
&nbsp;  
- Turn On "Transport layer security (TLS)" and check "Required TLS client authentiation"  
![TLS One](./img/tls_1.png)
   
- Click the "Generate certificate" button
![TLS Two](./img/tls_2.png)
  
- Click the "Download Redis' certificate authority" link"
![TLS Three](./img/tls_3.png)
  
- Click the "Save database" button
![TLS Four](./img/tls_4.png)
   
- Collect the following connection parameters for the TLS-enabled REDB:  
  - Public endpoint  
  - Default user password   
  

#### 5. Create a K8 secret to store the client certificate, client key and server certificate for mutual TLS connection
Unzip the redislabs_credentials.zip file:
```
unzip redislabs_credentials.zip

Archive:  redislabs_credentials.zip
 extracting: redislabs_user.crt      
 extracting: redislabs_user_private.key  
 extracting: redislabs_ca.pem   
```
Create a "redis" namespace:
```
kubectl create ns redis
```
Create a secret to store the client certificate, client key and service certificate:
```
kubectl -n redis create secret generic \
redis-client --from-file=redislabs_user_private.key \
--from-file=redislabs_user.crt --from-file=redislabs_ca.pem
```


#### 6. Deploy a Redis client on the GKE cluster
```
cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-client
  namespace: redis
  labels:
    app: redis-client
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis-client
  template:
    metadata:
      labels:
        app: redis-client
      annotations:
        sidecar.istio.io/logLevel: debug
        sidecar.istio.io/inject: "true"                                                                                     
        sidecar.istio.io/userVolumeMount: '[{"name":"redis-client", "mountPath":"/etc/ssl/redis/certs", "readonly":true}]'
        sidecar.istio.io/userVolume: '[{"name":"redis-client", "secret":{"secretName":"redis-client"}}]'
    spec:
      containers:
        - image: redis
          name: redis-client
          command: [ "/bin/bash", "-c", "--" ]
          args: [ "while true; do sleep 30; done;" ]
EOF
```
  

#### 7. Create Istio resources (ServiceEntry and DestinationRule) for the TLS-enabled REDB
Set the following environment variables:
```
In my example,
export REDIS_HOST=redis-10365.c17257.us-west1-mz.gcp.cloud.rlrcp.com
export REDIS_PORT=10365
```  
Create ServiceEntry resource:
```
cat <<EOF | kubectl apply --namespace=redis -f -
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-tls-redis
spec:
  hosts:
  - $REDIS_HOST
  location: MESH_EXTERNAL
  resolution: DNS
  ports:
  - number: $REDIS_PORT
    name: tcp-redis
    protocol: TCP
EOF
```
Create DestinationRule resource:
```
cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: external-tls-redis
  namespace: redis
spec:
  host: $REDIS_HOST
  trafficPolicy:
    tls:
      mode: MUTUAL
      clientCertificate: /etc/ssl/redis/certs/redislabs_user.crt
      privateKey: /etc/ssl/redis/certs/redislabs_user_private.key
      caCertificates: /etc/ssl/redis/certs/redislabs_ca.pem
EOF
```
    

#### 8. Validate Istio proxy sidecar's TLS origination for a secured mTLS REDB connection
Get a shell to the redis-client container:
```
kubectl exec -ti deploy/redis-client -c redis-client -- bash
```
Connect to the TLS-enabled REDB instance with TLS origination configured in the Istio proxy sidecar:
```
redis-cli -h <REPLACE_WITH_REDB_IP> -p <REPLACE_WITH_REDB_PORT>T -a <REPLACE_WITH_DEFAULT_USER_PASSWORD>
set "watch" "rolex"
get "watch"

It shoud return "rolex"
```


