# 🤖 gnosis-multisig-monitor
Grab your bot's token from [https://discord.com/developers/applications](https://discord.com/developers/applications) and export it:
```
export BOT_TOKEN=<**********>
```
With docker engine running, build the container and run it:
```
docker build -t gnosis-multisig-monitor .
```
```
docker run -t gnosis-multisig-monitor
```

### Deploying

New container will be built and pushed to ECR on push to main. K8s manifest will be updated in badger-kube-manifests with new container and ArgoCD will pick up and deploy to EKS cluster.
