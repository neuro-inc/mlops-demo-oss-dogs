# startup-package-test

The project description is here.

## Quick Start

Sign up at [app.neu.ro](https://app.neu.ro) and setup your local machine according to [these instructions](https://docs.neu.ro/getting-started#installing-the-cli).

This guide assumes that you already have a deployed Pachyderm cluster that's ready to create and run pipelines.

To get access to the sandbox environment that contains all the components installed and configured, please [contact our team](team@neu.ro).

## Preparation

```shell
neuro login
```

Build all images used in the flow:

```shell
neuro-flow build ALL
```

Create a secret with a private SSH key for accessing the GitHub repository (pull/push access should be allowed and the SSH key should not be protected with a passphrase):

```shell
neuro secret add gh-rsa @~/.ssh/id_rsa
```

Create a service account for authenticating the training pipeline:

```shell
neuro service-account create --name mlops-demo-oss-dogs
```

Take the full token from the command's output and store it in a secret:

```shell
neuro secret add platform-config FULL_TOKEN_FROM_OUTPUT
```

Grant permissions for the new service account

```shell
export USER=<YOUR_USERNAME>
export PROJECT=mlops-demo-oss-dogs
export PREFIX="/${USER}/${PROJECT}/"
export ACCOUNT=${USER}/service-accounts/${PROJECT}
export ROLE=${USER}/projects/${PROJECT//-/_}

neuro acl grant storage:${PREFIX} ${ROLE} write
neuro acl grant job:/${ACCOUNT} ${ACCOUNT} manage
neuro acl grant image:${PREFIX} ${ROLE} read 
neuro acl grant secret:gh-rsa ${ROLE} read
neuro acl grant role://${ROLE} ${ACCOUNT} read

# temp workaround for neuro-flow bug
neuro acl grant role://${USER}/projects ${ACCOUNT}  manage
```

Set up the variables needed to run the loads in your cluster that were provided by the Neu.ro team:

```shell
export MLFLOW_STORAGE=<storage:path>
export MLFLOW_URI=<URI>
```

Create a Pachyderm pipeline that will (re)train the model on every dataset update:

```shell
neuro-flow run create_pipeline --param mlflow_storage $MLFLOW_STORAGE --param mlflow_uri $MLFLOW_URI
```

Download the full dataset to storage:

```shell
neuro-flow run prepare_remote_dataset
```

## The flow

Each update of the dataset creates a [Pachyderm](https://www.pachyderm.com/) commit. If this commit also affects image labels, it triggers the Pachyderm pipeline, which in turn triggers model training on the platform.

- Pick 15 images from the dataset and put them under Pachyderm:

  ```shell
  neuro-flow run extend_data --param extend_dataset_by 15
  ```

- Run [Label Studio](https://labelstud.io/) in a browser in order to process the images for training. Label Studio closes automatically when all images are marked and commits a new dataset version, which triggers training. You will see the progress in logs.

  ```shell
  neuro-flow run label_studio
  ```

- You may follow the training process in the [MLFlow](https://www.mlflow.org/) server's Web UI using the provided link or in Pachyderm pipeline logs:
  
  ```shell
  pachctl config update context default --pachd-address <Pachyderm server address>
  pachctl logs -f -p train 
  ```

- Pick a run ID value from MLFlow's Web UI and deploy the trained model as a REST API on the platform:

  ```shell
  neuro-flow run deploy_inference_platform --param run_id XXXXXX  --param mlflow_storage $MLFLOW_STORAGE
  ```

- Run a stress test on the deployed model via Locust (open up web UI), specifying the model's endpoint URI. If the model is deployed as a platform job, you should use `https://demo-oss-dogs-test-inference--<username>.jobs.<cluster-name>.org.neu.ro/api/v1.0/predictions`, and `http://seldon.<cluster-name>.org.neu.ro/seldon/seldon/<model-name>-<model-stage>/api/v1.0/predictions` if the model is deployed in Seldon.

  ```shell
  neuro-flow run locust --param endpoint_url <Address>
  ```

- Run [SHAP](https://shap.readthedocs.io/en/latest/index.html) in Jupyter Notebook to explain the output of the trained model:

  ```shell
  neuro-flow run jupyter --param run_id XXXXXX --param mlflow_storage $MLFLOW_STORAGE
  ```

## Optional steps:

- Add 10 more images to the dataset, label them, and let Pachyderm retrain the model:

```shell
neuro-flow run extend_data --param extend_dataset_by 10
neuro-flow run label_studio
```

- Deploy the model to Seldon using our Kubernetes [MLFlow2Seldon operator](https://github.com/neuro-inc/mlops-k8s-mlflow2seldon) (assume the operator is already deployed). In this case, you will also need a Seldon Core installation up and running on the cluster.

## Additional

You might also run an MLFlow server by yourself, but in this case, you will need to replace the MLFlow server URI in the `env` configuration.

Create a persistent disk for Postgresql:

```shell
neuro disk create 1G --timeout-unused 30d --name mlops-demo-oss-dogs-postgres
```

Run a Postgresql server (needed by MLFlow):

```shell
neuro-flow run postgres
```

Run an MLFlow server for experiment and model tracking. In this setup, we imply personal use of MLFlow server (each user will connect to their own server).

```shell
neuro-flow run mlflow_server
```
