# OpenShift and Atomic Platform Ansible Contrib

This repo contains *unsupported* code that is to be used in conjunction with
the openshift-ansible repository

## Workflow:

### Create your environment

  Create Python virtual env

  Pip install boto, boto3, socket

  Install Ansible 2.2.0 from source / http://docs.ansible.com/ansible/intro_installation.html#running-from-source

  git clone https://github.com/feedhenry/fh-openshift

  git clone https://github.com/openshift/openshift-ansible.git

### Deploy rhm site infrastructure

```ansible-playbook playbooks/aws-infrastructure.yaml --tags grid (soon to be site)```

### Deploy rhm rhmap infrastructure

```ansible-playbook playbooks/aws-infrastructure.yaml --tags rhmap```

### Prepare infrastructure

```ansible-playbook playbooks/openshift-install.yaml```

  NOTE: Subscription account credentials and manager pool req'd!

### Install OpenShift

  Prepare ssh client / ~/.ssh/conf

  NOTE: that the static data values Hostname need to be dealt with manually at this time

```
Host US-TOM
     User                       ec2-user
     Hostname                   54.82.151.107
     User                       ec2-user
     StrictHostKeyChecking      no
     CheckHostIP                no
     ForwardAgent               yes
     ServerAliveInterval        30
     ServerAliveCountMax        120
     GSSAPIAuthentication       no
     GSSAPIDelegateCredentials  no
     IdentityFile               ~/.ssh/id_rsa

Host *.rhmpoc.com
     User                       ec2-user
     StrictHostKeyChecking      no
     CheckHostIP                no
     ForwardAgent               yes
     ServerAliveInterval        30
     ServerAliveCountMax        120
     GSSAPIAuthentication       no
     GSSAPIDelegateCredentials  no
     IdentityFile               ~/.ssh/id_rsa
     TCPKeepAlive           yes
     ProxyCommand           ssh -qaY ec2-user@US-TOM 'nc -w 14400ms %h %p'
     ControlMaster          auto
     ControlPath            ~/.ssh/mux-%r@%h:%p
     ControlPersist         8h
#CURRENTLY NEEDED FOR OPENSHIFT-ANSIBLE ANSIBLE PLAYBOOK
Host 10.*
     User                       ec2-user
     StrictHostKeyChecking      no
     CheckHostIP                no
     ForwardAgent               yes
     ServerAliveInterval        30
     ServerAliveCountMax        120
     GSSAPIAuthentication       no
     GSSAPIDelegateCredentials  no
     IdentityFile               ~/.ssh/id_rsa
     TCPKeepAlive           yes
     ProxyCommand           ssh -qaY ec2-user@US-TOM 'nc -w 14400ms %h %p'
     ControlMaster          auto
     ControlPath            ~/.ssh/mux-%r@%h:%p
     ControlPersist         8h
```

  Prepare Ansible client / ansible.cfg
```
# config file for ansible -- http://ansible.com/
# ==============================================
[defaults]
#callback_plugins = ../openshift-ansible/ansible-profile/callback_plugins
TMOUT=10
forks = 50
host_key_checking = False
hostfile = inventory/aws/hosts/ec2.py
remote_user = ec2-user
private_key_file = ~/.ssh/id_rsa
gathering = smart
retry_files_enabled = false
nocows = true
lookup_plugins: ./lookup_plugins

[privilege_escalation]
become = True

[ssh_connection]
ssh_args = -F /Users/ccallega/.ssh/config -o ForwardAgent=yes -o ControlMaster=auto -o ControlPersist=900s
#pipelining = True
#scp_if_ssh = True
control_path = ~/.ssh/mux-%%r@%%h:%%p
```

  Prepare Ansible dynamic inventory

```inventory/aws/hosts/ec2.py --refresh-cache```

  Prepare Ansible hosts file / inventory/aws/hosts/hosts

```
# Create an OSEv3 group that contains the masters and nodes groups
[OSEv3:children]
masters
nodes
etcd
registry
routers

[masters:children]
tag_Role_oscpmaster

[etcd:children]
tag_Role_oscpmaster

[registry:children]
tag_Role_oscpmaster

[nodes:children]
master_nodes
app_nodes
routers

[master_nodes:children]
tag_Role_oscpmaster

[master_nodes:vars]
openshift_node_labels="{'region'='infra', 'zone'='default'}"
containerized=false
openshift_schedulable=true

[app_nodes:children]
tag_Role_oscpnode

[app_nodes:vars]
openshift_node_labels="{'region'='primary', 'zone'='default'}"
containerized=false

[routers:children]
tag_Role_oscpinfra

[routers:vars]
openshift_node_labels="{'region'='infra', 'zone'='default'}"
containerized=false

[tag_Role_oscpmaster]
[tag_Role_oscpinfra]
[tag_Role_oscpnode]


[OSEv3:vars]
# SSH user, this user should allow ssh based auth without requiring a password
ansible_ssh_user=ec2-user

# If ansible_ssh_user is not root, ansible_become must be set to true
ansible_become=true
deployment_type=openshift-enterprise

# openshift-ansible will wait indefinitely for your input when it detects that the
# value of openshift_hostname resolves to an IP address not bound to any local
# interfaces. This mis-configuration is problematic for any pod leveraging host
# networking and liveness or readiness probes.
# Setting this variable to true will override that check.
openshift_override_hostname_check=true

openshift_master_identity_providers=[{'name': 'htpasswd_auth', 'login': 'true', 'challenge': 'true', 'kind': 'HTPasswdPasswordIdentityProvider', 'filename': '/etc/origin/master/htpasswd'}]
openshift_master_htpasswd_users={ 'admin':'$apr1$LYvKbAv6$C.XK7SOYHLhBzL3qp7bsJ/' }

openshift_master_cluster_method=native
osm_cluster_network_cidr=10.1.0.0/16
openshift_portal_net=172.30.0.0/16
#TODO: ELB values need to be auto generated
openshift_master_cluster_hostname=internal-ustommasterapiint-113532355.us-east-1.elb.amazonaws.com
openshift_master_cluster_public_hostname=ustommasterapiext-1882102569.us-east-1.elb.amazonaws.com
#
openshift_master_named_certificates=[{"cafile": "/tmp/rootCA.crt", "certfile": "/tmp/us-tom-rhmpoc.com.crt", "keyfile": "/tmp/us-tom-rhmpoc.com.key", "names": ["internal-ustommasterapiint-113532355.us-east-1.elb.amazonaws.com", "ustommasterapiext-1882102569.us-east-1.elb.amazonaws.com"]}]
openshift_master_overwrite_named_certificates=false

openshift_registry_selector='type=infra'
openshift_hosted_router_selector='type=infra'

#DO NOT USE openshift_cloudprovider_kind
#openshift_cloudprovider_kind=aws
#openshift_cloudprovider_aws_access_key=
#openshift_cloudprovider_aws_secret_key=

openshift_hosted_registry_storage_kind=object
openshift_hosted_registry_storage_provider=s3
openshift_hosted_registry_storage_s3_accesskey=
openshift_hosted_registry_storage_s3_secretkey=
openshift_hosted_registry_storage_s3_bucket=rhm-site
openshift_hosted_registry_storage_s3_region=us-east
openshift_hosted_registry_storage_s3_chunksize=26214400
openshift_hosted_registry_storage_s3_rootdirectory=/registry
openshift_hosted_registry_pullthrough=true
openshift_hosted_registry_acceptschema2=true
openshift_hosted_registry_enforcequota=true
```


  Execute Ansible playbook

```ansible-playbook -i inventory/aws/hosts playbooks/byo/openshift-cluster/config.yml```


### Install RHMAP onto OpenShift
