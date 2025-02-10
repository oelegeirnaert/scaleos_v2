The production stack
======================================================================

How to install & configure Docker Swarm with share
----------------------------------------------------------------------

Inspired by: https://dev.to/hackmamba/how-to-create-a-docker-swarm-of-appwrite-containers-and-ui-with-swarmpit-1nje
ATTENTION: When making the NFS share MANAGER and WORKER are used as USERS

**First Thing:** add the public IP of the server to the DNS records
scaleos.net domain is hosted at GoDaddy
https://dcc.godaddy.com/control/portfolio/scaleos.net/settings?tab=dns


Manager: 

    ::

        sudo apt install nfs-kernel-server
        sudo mkdir -p home/root/nfs/app -p
        sudo chown nobody:nogroup home/root/nfs/app
        sudo nano /etc/exports
            home/root/nfs/app    <WORKER_ip>(rw,sync,no_subtree_check)
        sudo systemctl restart nfs-kernel-server

Worker:

    ::

        sudo apt install nfs-common
        sudo mkdir -p /nfs/app
        sudo mount <MANAGER_ip>:/home/root/nfs/app /nfs/app

Manager:

    ::

        sudo docker swarm init --advertise-addr <MANAGER_TAILSCALE_ip>
            This will generate a command that needs to be executed on the worker.

BUT if you forgot the JOIN token for the WORKER:

    ::
    
        docker swarm join-token worker

Bring the stack up
----------------------------------------------------------------------

--with-registry-auth allows to download images from GHCR.io

    ::

        docker stack deploy --with-registry-auth -c docker-swarm-compose.yml scaleos 

Check if latest image version
----------------------------------------------------------------------

    ::

        docker images --digests

Stop a stack
----------------------------------------------------------------------

    ::

        docker stack rm scaleos

        

Install Swarmpit
----------------------------------------------------------------------

Install the Swarmpit by using the following code:

    ::

        sudo git clone https://github.com/swarmpit/swarmpit -b master && sudo docker stack deploy -c swarmpit/docker-compose.arm.yml swarmpit


Hostinger
----------------------------------------------------------------------

ssh root@147.93.122.129
LOGIN INTO GITHUB: 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
Installed Tailscale