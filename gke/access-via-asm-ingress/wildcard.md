### Example for wildcard entry definition for multiple Redis Enterprise databases:
  
Assuming there are two databases namely redis-enterprise-database and redis-enterprise-database-2:
```
export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway \
       -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
export SECURE_INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway \
       -o jsonpath='{.spec.ports[?(@.name=="https")].port}')
export DB_PORT=$(kubectl get secrets -n redis redb-redis-enterprise-database \
       -o jsonpath="{.data.port}" | base64 --decode)
export DB_PORT_2=$(kubectl get secrets -n redis redb-redis-enterprise-database-2 \
       -o jsonpath="{.data.port}" | base64 --decode)
```
   
Gateway definition:
Assuming TLS/SSL certificate's common name in this form: *.rec.&lt;${INGRESS_HOST}&gt;.nip.io
```
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: redis-gateway-wc
spec:
  selector:
    istio: ingressgateway # use istio default ingress gateway
  servers:
  - port:
      number: ${SECURE_INGRESS_PORT}
      name: https
      protocol: HTTPS
    tls:
      mode: PASSTHROUGH
    hosts:
    - rec-ui.${INGRESS_HOST}.nip.io
    - "*.demo.rec.${INGRESS_HOST}.nip.io"
EOF
```
  
Routing definition:
```
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: redis-vs
spec:
  hosts:
  - "*.demo.rec.${INGRESS_HOST}.nip.io"
  gateways:
  - redis-gateway-wc
  tls:
  - match:
    - port: ${SECURE_INGRESS_PORT}
      sniHosts:
      - redis-${DB_PORT}.demo.rec.${INGRESS_HOST}.nip.io
    route:
    - destination:
        host: redis-enterprise-database
        port:
          number: ${DB_PORT}
  - match:
    - port: ${SECURE_INGRESS_PORT}
      sniHosts:
      - redis-${DB_PORT_2}.demo.rec.${INGRESS_HOST}.nip.io
    route:
    - destination:
        host: redis-enterprise-database-2
        port:
          number: ${DB_PORT_2}
EOF
```
