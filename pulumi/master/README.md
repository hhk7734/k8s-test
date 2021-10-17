```shell
export PULUMI_CONFIG_PASSPHRASE=<passwd>
```

```shell
pulumi up
```

```shell
ansible-playbook ansible/after_pulumi.yaml
```

```shell
ssh ubuntu@$(pulumi stack output k8s_master_0_public_ip) -i ~/.ssh/hhk7734.pem
```

```shell
pulumi destroy
```

## Reference

-[https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html)
