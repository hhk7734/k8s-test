```shell
  Type     Reason       Age                   From                Message
  ----     ------       ----                  ----                -------
  Normal   Scheduled    7m46s                 default-scheduler   Successfully assigned istio-system/istio-ingressgateway-7f64fb5f7b-zz7sh to tfg7597xg
  Warning  FailedMount  3m25s                 kubelet, tfg7597xg  Unable to attach or mount volumes: unmounted volumes=[istiod-ca-cert istio-token], unattached volumes=[istio-envoy podinfo ingressgateway-ca-certs istiod-ca-cert ingressgateway-certs istio-token istio-data config-volume istio-ingressgateway-service-account-token-ckwrp]: timed out waiting for the condition
  Warning  FailedMount  94s (x11 over 7m46s)  kubelet, tfg7597xg  MountVolume.SetUp failed for volume "istiod-ca-cert" : configmap "istio-ca-root-cert" not found
  Warning  FailedMount  93s (x11 over 7m45s)  kubelet, tfg7597xg  MountVolume.SetUp failed for volume "istio-token" : failed to fetch token: the API server does not have TokenRequest endpoints enabled
```

```shell
sudo vim /etc/kubernetes/manifests/kube-apiserver.yaml
```

```yaml
spec:
  containers:
    - command:
        - kube-apiserver
        # ...
        - --service-account-signing-key-file=/etc/kubernetes/pki/sa.key
        - --service-account-issuer=kubernetes.default.svc
```
