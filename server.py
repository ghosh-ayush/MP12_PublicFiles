from kubernetes import client, config
from flask import Flask,request
import os
import yaml, random, string, json
import sys
import json
from kubernetes.config.config_exception import ConfigException


# Configs can be set in Configuration class directly or using helper utility
#config.load_kube_config()
try:
    config.load_incluster_config()
    print("✅ Loaded in-cluster Kubernetes config")
except ConfigException:
    kube_cfg = os.environ.get("KUBECONFIG", os.path.expanduser("~/.kube/config"))
    config.load_kube_config(config_file=kube_cfg)
    print(f"✅ Loaded local kubeconfig from {kube_cfg}")
v1 = client.CoreV1Api()
batch_v1 = client.BatchV1Api()
app = Flask(__name__)
# app.run(debug = True)

@app.route('/config', methods=['GET'])
def get_config():
    print("GET /config called")
    pods = []
    all_pods = v1.list_pod_for_all_namespaces().items
    for p in all_pods:
        pods.append({
            "node": p.spec.node_name,
            "ip": p.status.pod_ip,
            "namespace": p.metadata.namespace,
            "name": p.metadata.name,
            "status": p.status.phase
        })
    # your code here

    output = {"pods": pods}
    output = json.dumps(output)

    return output

# Helper to build job manifest


def make_job_manifest(namespace, job_name, dataset, mtype, image, parallelism=None, completions=None):
    spec = {
        'template': {
            'spec': {
                'containers': [{
                    'name': 'classifier',
                    'image': image,
                    'imagePullPolicy': 'IfNotPresent',
                    'command': ['python', 'classify.py'],
                    'env': [
                        {'name': 'DATASET', 'value': dataset},
                        {'name': 'TYPE',    'value': mtype}
                    ],
                    'resources': {'requests': {'cpu': '0.9'}, 'limits': {'cpu': '0.9'}}
                }],
                'restartPolicy': 'Never'
            }
        },
        'backoffLimit': 0
    }
    # inject parallelism/completions if requested
    if parallelism is not None:
        spec['parallelism'] = parallelism
    if completions is not None:
        spec['completions'] = completions

    return {
        'apiVersion': 'batch/v1',
        'kind': 'Job',
        'metadata': {'name': job_name, 'namespace': namespace},
        'spec': spec
    }
@app.route('/img-classification/free', methods=['POST'])
def post_free():
    # free tier: 2 pods in parallel, 2 completions
    print("POST /img-classification/free called")
    namespace = 'free-service'
    job_name = 'free-job-' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    image = 'ayushghoshdocker/mp12_image:latest'
    manifest = make_job_manifest(
        namespace, job_name,
        dataset='mnist', mtype='ff', image=image,
        #parallelism=2,
        #completions=2
    )
    batch_v1.create_namespaced_job(body=manifest, namespace=namespace)
    return "success", 200

@app.route('/img-classification/premium', methods=['POST'])
def post_premium():
    # premium tier: default (1 pod)
    print("POST /img-classification/premium called")
    namespace = 'default'
    job_name = 'premium-job-' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    image = 'ayushghoshdocker/mp12_image:latest'
    manifest = make_job_manifest(
        namespace, job_name,
        dataset='kmnist', mtype='cnn', image=image,
        #parallelism=2,
        #completions=2
        # no parallelism/completions => defaults to 1
    )
    batch_v1.create_namespaced_job(body=manifest, namespace=namespace)
    return "success", 200

    
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
