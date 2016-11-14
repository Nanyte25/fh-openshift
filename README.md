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
  ansible-playbook playbooks/aws-infrastructure.yaml --tags grid (soon to be site)

### Deploy rhm rhmap infrastructure
  ansible-playbook playbooks/aws-infrastructure.yaml --tags rhmap

### Prepare infrastructure
  ansible-playbook playbooks/openshift-install.yaml
  Subscription account credentials and manager pool req'd!

### Install OpenShift
  Prepare ssh client / vi ~/.ssh/conf
  Note that the static data values Hostname need to be dealt with manually at this time
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
    inventory/aws/hosts/ec2.py --refresh-cache

  Prepare Ansible hosts file / inventory/aws/hosts/hosts
    More to come here

  Execute Ansible playbook
    ansible-playbook -i inventory/aws/hosts playbooks/byo/openshift-cluster/config.yml
