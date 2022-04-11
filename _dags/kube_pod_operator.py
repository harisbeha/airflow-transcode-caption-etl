kubernetes_full_pod = kubernetes_pod_operator.KubernetesPodOperator(
    task_id='ex-all-configs',
    name='pi',
    namespace='default',
    image='perl',
    # Entrypoint of the container, if not specified the Docker container's
    # entrypoint is used. The cmds parameter is templated.
    cmds=['ffmpeg'],
    # Arguments to the entrypoint. The docker image's CMD is used if this
    # is not provided. The arguments parameter is templated.
    arguments=['-Mbignum=bpi', '-wle', 'print bpi(2000)'],
    # The secrets to pass to Pod, the Pod will fail to create if the
    # secrets you specify in a Secret object do not exist in Kubernetes.
    secrets=[],
    # Labels to apply to the Pod.
    labels={'pod-label': 'label-name'},
    # Timeout to start up the Pod, default is 120.
    startup_timeout_seconds=120,
    # The environment variables to be initialized in the container
    # env_vars are templated.
    env_vars={'EXAMPLE_VAR': '/example/value'},
    # If true, logs stdout output of container. Defaults to True.
    get_logs=True,
    # Determines when to pull a fresh image, if 'IfNotPresent' will cause
    # the Kubelet to skip pulling an image if it already exists. If you
    # want to always pull a new image, set it to 'Always'.
    image_pull_policy='Always',
    # Annotations are non-identifying metadata you can attach to the Pod.
    # Can be a large range of data, and can include characters that are not
    # permitted by labels.
    annotations={'key1': 'value1'},
    # Resource specifications for Pod, this will allow you to set both cpu
    # and memory limits and requirements.
    # Prior to Airflow 1.10.4, resource specifications were
    # passed as a Pod Resources Class object,
    # If using this example on a version of Airflow prior to 1.10.4,
    # import the "pod" package from airflow.contrib.kubernetes and use
    # resources = pod.Resources() instead passing a dict
    # For more info see:
    # https://github.com/apache/airflow/pull/4551
    resources={'limit_memory': 1, 'limit_cpu': 1},
    # Specifies path to kubernetes config. If no config is specified will
    # default to '~/.kube/config'. The config_file is templated.
    config_file='/home/airflow/composer_kube_config',
    # If true, the content of /airflow/xcom/return.json from container will
    # also be pushed to an XCom when the container ends.
    xcom_push=False,
    # List of Volume objects to pass to the Pod.
    volumes=[],
    # List of VolumeMount objects to pass to the Pod.
    volume_mounts=[],
    # Affinity determines which nodes the Pod can run on based on the
    # config. For more information see:
    # https://kubernetes.io/docs/concepts/configuration/assign-pod-node/
    affinity={})