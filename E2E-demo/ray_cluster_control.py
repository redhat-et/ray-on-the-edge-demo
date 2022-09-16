import openshift as oc
import os
from jinja2 import Template
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv(), override=True)


server = os.environ["SERVER"]
project = os.environ["PROJECT"]
token = os.environ["TOKEN"]
user_name = os.environ["USER_NAME"]
cluster_name = os.environ["RAY_CLUSTER_NAME"]
cpu_request = os.environ["CPU_REQUEST"]
cpu_limit = os.environ["CPU_LIMIT"]
memory_request = os.environ["MEMORY_REQUEST"]
memory_limit = os.environ["MEMORY_LIMIT"]
gpu_limit = os.environ["GPU_LIMIT"]


def start_ray_cluster(cluster_name=cluster_name):
    os.environ["RAY_CLUSTER_NAME"] = cluster_name
    with oc.api_server(server):
        with oc.token(token):
            with oc.project(project):
                response = oc.invoke('get', ["pods", "-l",
                                             f"jupyterhub.opendatahub.io/user={user_name}-40redhat-2ecom",
                                             "-o", "jsonpath='{$.items[*].metadata.uid}'"])
                pod_uid = response.as_dict()["actions"][0]["out"].strip("'")
                response = oc.invoke('get', ["pods", "-l",
                                             f"jupyterhub.opendatahub.io/user={user_name}-40redhat-2ecom",
                                             "-o", "jsonpath='{$.items[*].metadata.name}'"])
                pod_name = response.as_dict()["actions"][0]["out"].strip("'")

    template_data = {"cluster_name": cluster_name,
                     "cpu_request": cpu_request,
                     "cpu_limit": cpu_limit,
                     "memory_request": memory_request,
                     "memory_limit": memory_limit,
                     "gpu_limit": gpu_limit,
                     "jupyter_pod_name": pod_name,
                     "jupyter_pod_uid": pod_uid,
                     }

    applied_template = Template(open("../deploy/cluster_collection/cluster_template.yaml").read())
    applied_serving_route = Template(open("../deploy/cluster_collection/serving_route_template.yaml").read())
    applied_dashboard_route = Template(open("../deploy/cluster_collection/dashboard_route_template.yaml").read())
    

    with oc.api_server(server):
        with oc.token(token):
            with oc.project(project):
                oc.apply(applied_template.render(template_data))
                oc.apply(applied_serving_route.render(template_data))
                oc.apply(applied_dashboard_route.render(template_data))
                serve_response = oc.invoke('get', ["route", f"ray-serving-{cluster_name}",
                                             "-o","jsonpath='{$.spec.host}'"])
                dashboard_response = oc.invoke('get', ["route", f"ray-dashboard-{cluster_name}",
                                             "-o","jsonpath='{$.spec.host}'"])
   
    os.environ["SERVING_ENDPOINT"] = serve_response.as_dict()["actions"][0]["out"].strip("'")            
    os.environ["DASHBOARD_ENDPOINT"] = dashboard_response.as_dict()["actions"][0]["out"].strip("'")     
    
    print(f'RayCluster "{cluster_name}" has started')
    print(f'Access your cluster dashboard at http://{os.environ["DASHBOARD_ENDPOINT"]}')


def stop_ray_cluster(cluster_name=cluster_name):
    with oc.api_server(server):
        with oc.token(token):
            with oc.project(project):
                oc.invoke('delete', ["RayCluster", cluster_name])
                oc.invoke('delete', ["Route", f"ray-serving-{cluster_name}"])
                oc.invoke('delete', [ "Route", f"ray-dashboard-{cluster_name}"])
                print("done")