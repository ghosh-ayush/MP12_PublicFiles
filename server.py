from kubernetes import client, config
from flask import Flask,request
from os import path
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
app = Flask(__name__)
# app.run(debug = True)

@app.route('/config', methods=['GET'])
def get_config():
    pods = []

    # your code here

    output = {"pods": pods}
    output = json.dumps(output)

    return output

@app.route('/img-classification/free',methods=['POST'])
def post_free():
    # your code here

    return "success"


@app.route('/img-classification/premium', methods=['POST'])
def post_premium():
    # your code here

    return "success"

    
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
