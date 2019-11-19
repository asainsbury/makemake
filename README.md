# [MakeMAke](https://solarsystem.nasa.gov/planets/dwarf-planets/makemake/in-depth/)
Ansible playbook to create a project folder structure for rapid development.

This is a continuation of the work which can be found in vagrant-maker, but with some bigger bells and better whistles.

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


