# Deploying Ray with ODH Jupyterhub

Integration of [Ray](https://docs.ray.io/en/latest/index.html) with Open Data Hub on OpenShift, using a singleuser profile to provision a ray cluster.
The ray operator and other components are based on https://docs.ray.io/en/releases-1.12.1/cluster/kubernetes.html

#### Components  of the Ray deployment

1. [Ray operator](./operator/ray-operator-deployment.yaml): The operator would process RayCluster resources and schedule ray head and worker pods based on requirements.
2. [Ray CR](./ray-custom-resources.yaml):  RayCluster CR would describe the desired state of ray cluster.
3. [Ray Single User profile](./ray-ml-profile-cm.yaml): The single user profile would enable jupyterhub to monitor Ray Notebook image and trigger Raycluster services.


#### Deploy the RayCluster Components:

Pre-requiste for RayCluster is to have it run along side Jupyterhub.

```
  - kustomizeConfig:
      parameters:
        - name: s3_endpoint_url
          value: "s3.odh.com"
      repoRef:
        name: manifests
        path: jupyterhub/jupyterhub
    name: jupyterhub
  - kustomizeConfig:
      overlays:
        - odh-ray-cluster
      repoRef:
        name: manifests
        path: jupyterhub/notebook-images
    name: notebook-images
```

#### Ensure RayCluster deployment:

Once the RayCluster is deployed, users can execute the `Ray ML Notebook` to connect to an raycluster instance. Following components can be checked to verify an healthy raycluster.

1. Log into the JupyterHub launcher. You should see a new notebook image option `ray-ml-notebook`. 
Note: If the ray notebook is still not visible, you will need to restart the `jupyterhub-xxxx` pod so that it reads the new profile you just installed. Simply deleting this pod will cause it to be restarted automatically.
2. Launch your JupyterHub environment. As part of the startup process, the ODH JupyterHub launcher should also start up a Ray cluster.
3. Run the notebook with Ray based content(For example: [ray-smoke-test](https://github.com/erikerlandson/ray-odh-demo/blob/main/source/ray-smoke-test.ipynb)) to confirm that it connects to your ray cluster and operates correctly.
4. You could also see the head and worker nodes created under pods as `ray-cluster-$USER-ray-cluster-$USER-head-xxxxx` and `ray-cluster-$USER-ray-cluster-$USER-worker-xxxxx` pods


### Reference

References of all images are as follows:
1. Ray-Operator: https://github.com/thoth-station/ray-operator
2. Ray-ml-worker: https://github.com/thoth-station/ray-ml-worker
3. Ray-ml-notebook: https://github.com/thoth-station/ray-ml-notebook
4. Demo: https://github.com/erikerlandson/ray-odh-demo
5. MOC-ray-demo: https://old.operate-first.cloud/community-handbook/moc-ray-demo/README.md
