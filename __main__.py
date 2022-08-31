import iam
import vpc
import utils
import pulumi
from pulumi_aws import eks
from pulumi_kubernetes import (
    Provider,
    helm,
)

## EKS Cluster

eks_cluster = eks.Cluster(
    'eks-cluster',
    role_arn=iam.eks_role.arn,
    tags={
        'Name': 'pulumi-eks-cluster',
    },
    vpc_config=eks.ClusterVpcConfigArgs(
        public_access_cidrs=['0.0.0.0/0'],
        security_group_ids=[vpc.eks_security_group.id],
        subnet_ids=vpc.subnet_ids,
    ),
)

eks_node_group = eks.NodeGroup(
    'eks-node-group',
    cluster_name=eks_cluster.name,
    node_group_name='pulumi-eks-nodegroup',
    node_role_arn=iam.ec2_role.arn,
    subnet_ids=vpc.subnet_ids,
    tags={
        'Name': 'pulumi-cluster-nodeGroup',
    },
    scaling_config=eks.NodeGroupScalingConfigArgs(
        desired_size=2,
        max_size=2,
        min_size=1,
    ),
)

kube_config = utils.generate_kube_config(eks_cluster)

k8s_provider = Provider("k8s", kubeconfig=kube_config)
chart = helm.v3.Chart(
    "chart",
    helm.v3.ChartOpts(
        chart="nginx-ingress",
        fetch_opts=helm.v3.FetchOpts(
            repo="https://charts.helm.sh/stable",
        ),
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

pulumi.export('cluster-name', eks_cluster.name)
pulumi.export('kubeconfig', kube_config)
