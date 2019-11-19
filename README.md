# [MakeMAke](https://solarsystem.nasa.gov/planets/dwarf-planets/makemake/in-depth/)
Ansible playbook to create a project folder structure for rapid development.

This is a continuation of the work which can be found in vagrant-maker, but with some bigger bells and better whistles.

- [[MakeMAke](https://solarsystem.nasa.gov/planets/dwarf-planets/makemake/in-depth/)](#-makemake--https---solarsystemnasagov-planets-dwarf-planets-makemake-in-depth--)
  * [Introduction](#introduction)
  * [Aims](#aims)
  * [Assumptions](#assumptions)
  * [Improvements](#improvements)
  * [Dependencies](#dependencies)
    + [Do's and Don'ts](#do-s-and-don-ts)
  * [Workflow](#workflow)
    + [Ansible](#ansible)
    + [Vagrant](#vagrant)
    + [Local SSHCONFIG](#local-sshconfig)
    + [Other folders](#other-folders)
  * [Final Tests](#final-tests)
- [Provisioning Process](#provisioning-process)
  * [Bootstrapping](#bootstrapping)
- [The Code](#the-code)
  * [VAR's](#var-s)
    + [Playbook top level](#playbook-top-level)
    + [Vagrant VARS Template](#vagrant-vars-template)
    + [Ansible Inventory Template](#ansible-inventory-template)
    + [SSH Config Template](#ssh-config-template)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>


## Introduction

I found myself constantly remaking the same folder structure over and over again, and then copying over files from lots of different places each time I wanted to make a new project.  I was also only running vagrant out of the one location, so I thought it would be better to make a playbook which is capable of replicating all my favorite structures and in a repeatable fashion.

## Aims

- Run the playbook and make a standard folder structure.
- From extra vars input do the following:
  - Make a vars file for Vagrant, specific to a project.
  - Make an inventory file for Ansible.
  - Update the local SSH Config file, to make it easy to shell into the VM's.
- Add default vars if nothing is supplied.
- Use some validation on the inputs, and exit if crap is found.
- Run Vagrant validate at the end to test it all worked.
- Use the Vagrant provisioning to create the VM's ready to be used in a new project.

## Assumptions

- You know a bit about:
  - Vagrant.
  - Ansible.
  - Ruby.
  - YAML.
  - Python.
  - Python virtual environments
  - Pip.

## Improvements

It would be nice to do the following:

- Install a new virtual environment into the project directory.
- Upgrade pip to the latest version.
- Install the latest versions of a bunch of my favorite modules.
- Break it up into roles, but I find a simple playbook, sometimes is the best approach.

## Dependencies

You need to have a few pip modules installed, otherwise the filters for working with IP addresses will fail.

- Netaddr.
- Probably more..

### Do's and Don'ts

- Don't quote the inputs when making a folder, or path.
- Don't include spaces in the title, spaces are bad.
- Do include a prefix with the starting IPAddr.

## Workflow

You simply have to call the playbook with the following extra vars:

```bash
ansible-playbook make_make.yml -e "title=myCool start_ip=1.1.1.20/24"  -v
```

You have to supply a title, as a minimum otherwise the playbook will fail. The rest of the vars can default into the data in the playbook, but it is probably worth putting in a new start IP range.

The playbook creates the following folder structure, and creates files specific for the project:

```bash
(python372)  ~/projects/scripts/mycool tree
.
├── ansible
│   ├── ansible.cfg
│   ├── group_vars
│   ├── host_vars
│   ├── inventory
│   │   └── hosts
│   └── roles
├── input
├── log
├── output
├── python
│   └── log
├── report
└── vagrant
    ├── Vagrantfile
    ├── bootstrap.yml
    ├── host_list.yml
    ├── id_rsa
    ├── id_rsa.pub
    ├── ssh_config
    └── stuff.yml

12 directories, 9 files
```

### Ansible

- Ansible hosts file for the nodes we created.
- Ansible.cfg file points to the host file.

### Vagrant

- Makes the host_list.yml variables specific to the input IPv4Addr.
- Stuff.yml is created for the bootstrap process.
- Public and private keys are copied over and are used for key access to the servers.

### Local SSHCONFIG

- For easy access into the new servers, better than using hosts file which needs sudo access.
- Ease of access without any passwords.

### Other folders

- Just sets up the other folders without any content.

## Final Tests

The playbook validates the vagrant file, at the end of the workflow, just to make sure everything is good before moving onto provisioning the VM's. 

```bash
cd {{projectname}} && vagrant validate 
```

# Provisioning Process

The actual end game, and reason for starting this all in the first place, is to stand up the VM's and start running a POC for something. To do this, we now move onto the Vagrantfile, and Ansible provisioning playbooks.

This nicely sets up a baseline configuration with all the parts ready to rock and roll. Security is not the focus of this project, and everything here is bare minimum on that front. Just calling it out, for what it is!

## Bootstrapping

This take care of the SSH keys, and a few other parts, so we can pick up and start writing more playbooks to do more fun stuff.

Look at that playbook for more details.

# The Code

OK, now for the fun stuff!

## VAR's


### Playbook top level
This is how you make defaults, and we can fill all of these via extra vars on the cli, or just leave it be.

Also used some lowercase, regex and IP address stuff:
```yaml
    var1: "{{ boxes     | default(3)  | int }}" 
    var2: "{{ start_ip  | default('1.1.1.10/24')   | ipaddr('host/prefix')}}"
    var3: "{{ root      | default('~/projects/scripts') }}"
    var4: "{{ title     | lower   | regex_replace(' ', '') }}"
    var5: "{{ files     | default(False)}}"
    var6: "{{ folders   | default(False)}}"
    var7: "{{ type      | default(centos7) }}"

    project: "{{ var3 }}/{{ var4 }}"
    ssh_config: "~/.ssh/config"
```

### Vagrant VARS Template

Started to get my teeth into the filters:

```jinja2
---
# Create by a Jinja2 template#
# https://docs.ansible.com/ansible/latest/user_guide/playbooks_filters_ipaddr.html#basic-tests
# Was a heap of fun making this template!

host_list:
{% set number = var1 | int -%}
{% for n in range( number ) %}
  - name: {{var4}}{{n +1}}
    provider: virtualbox
    group: {{var4}}
    ip: {{ var2 | ipaddr('address') | ipmath(n) }}
    vm_name: {{var4}}{{n +1}}
    mem: 512
    cpus: 1
    box: "{{var7[0]}}"
    box_url: "{{var7[1]}}"
    bootstrap: "bootstrap.yml"
    type: "linux"
    state: "present"

{% endfor %}


```

### Ansible Inventory Template

```jinja2
---
# Create by a Jinja2 template#
# https://docs.ansible.com/ansible/latest/user_guide/playbooks_filters_ipaddr.html#basic-tests
# Was a heap of fun making this template!

[local]
localhost ansible_connection=local

[{{var4}}]
{% set number = var1 | int -%}
{% for n in range( number ) %}
{{var4}}{{n +1}} ansible_ssh_host={{ var2 | ipaddr('address') | ipmath(n) }}
{% endfor %}
```

### SSH Config Template

```jinja2
# Create by a Jinja2 template
# https://docs.ansible.com/ansible/latest/user_guide/playbooks_filters_ipaddr.html#basic-tests
# Was a heap of fun making this template!

{% set number = var1 | int -%}
{% for n in range( number ) %}
Host {{var4}}{{n +1}} *.test.local
  hostname {{ var2 | ipaddr('address') | ipmath(n) }}
  StrictHostKeyChecking no
  UserKnownHostsFile=/dev/null
  User user
  LogLevel ERROR

{% endfor %}
```


