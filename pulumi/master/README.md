```shell
export PULUMI_CONFIG_PASSPHRASE=<passwd>
```

```shell
pulumi up
```

```shell
ansible-playbook ansible/master.yaml
```

```shell
ssh ubuntu@$(pulumi stack output k8s_master_0_public_ip) -i ~/.ssh/hhk7734.pem
```

```shell
wget https://docs.projectcalico.org/manifests/tigera-operator.yaml
```

```shell
kubectl create -f tigera-operator.yaml
```

```shell
watch kubectl get pods -n calico-system
```

```yaml title="calico.yaml"
# This section includes base Calico installation configuration.
# For more information, see: https://docs.projectcalico.org/v3.19/reference/installation/api#operator.tigera.io/v1.Installation
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  # Configures Calico networking.
  calicoNetwork:
    # Note: The ipPools section cannot be modified post-install.
    ipPools:
      - blockSize: 26
        cidr: 10.235.0.0/16
        encapsulation: VXLANCrossSubnet
        natOutgoing: Enabled
        nodeSelector: all()
```

```shell
kubectl taint nodes --all node-role.kubernetes.io/master-
```

```shell
ansible-playbook ansible/worker.yaml
```

```yaml title="aws-storage-class.yaml"
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
  annotations:
    storageclass.kubernetes.io/is-default-class: 'true'
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
reclaimPolicy: Retain
allowVolumeExpansion: true
mountOptions:
  - debug
volumeBindingMode: Immediate
```

```shell
kubectl apply -f aws-storage-class.yaml
```

```shell
pulumi destroy
```

## Reference

-[https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html)
