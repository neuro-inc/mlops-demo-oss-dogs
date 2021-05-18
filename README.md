# startup-package-test

The project description is here.

## Quick Start

Sign up at [app.neu.ro](https://app.neu.ro) and setup your local machine according to [instructions](https://docs.neu.ro/).

Assumption: Pachyderm cluster is deployed and ready to create and run the pipelines.

## Preparation

```shell
pip install -U neuro-cli neuro-flow
neuro login
```

Build images used in the flow

```shell
for image in train seldon label_studio
do 
  neuro-flow build "$image"
done
```

Create a secret with a private SSH key for GitHub repository access (pull/push access should be allowed, SSH key should not be protected with a passphase)

```shell
neuro secret add gh-rsa @~/.ssh/id_rsa
```

Set up the variables provided by Neu.ro team needed to run the loads in your cluster.

```shell
export MLFLOW_STORAGE=<storage:path>
export MLFLOW_URI=<URI>
```

Create Pachyderm pipeline that will (re)train model on every dataset update

```shell
neuro-flow run create_pipeline --param mlflow_storage $MLFLOW_STORAGE --param mlflow_uri $MLFLOW_URI
```

Download full dataset to storage

```shell
neuro-flow run prepare_remote_dataset
```

## The flow

Each update of the dataset creates a [Pachyderm](https://www.pachyderm.com/) commit. If this commit also affects image labels, it triggers the Pachyderm pipeline, which in turns triggers model training on a platform.

- Pick 15 images from the dataset and put them under Pachyderm

  ```shell
  neuro-flow run extend_data --param extend_dataset_by 15
  ```

- Run [Label Studio](https://labelstud.io/) in browser in order to process them for training. Label Studio closes automatically when all images are marked up and commits a new dataset version, which triggers training.

  ```shell
  neuro-flow run label_studio
  ```

- You may follow the training process in [MLFlow](https://www.mlflow.org/) server WebUI using the provided link and in Pachyderm pipeline logs:
  ```shell
  pachctl config update context default --pachd-address <Pachyderm server address>
  pachctl logs -f -p train 
  ```

- Pick a run id value from MLFlow web UI and deploy trained model as a REST API on the platform

  ```shell
  neuro-flow run deploy_inference_platform --param run_id XXXXXX  --param mlflow_storage $MLFLOW_STORAGE
  ```

- Run deployed model's stress test via Locust (open up web UI), specifying model endpoint URI (check Locust job description in live.yaml for hints).

  ```shell
  neuro-flow run locust --param endpoint_url <Address>
  ```

- Run [SHAP](https://shap.readthedocs.io/en/latest/index.html) in Jupyter Notebook to explain the output of trained model.

  ```shell
  neuro-flow run jupyter --param run_id XXXXXX --param mlflow_storage $MLFLOW_STORAGE
  ```

## Optional steps:
- Add 10 more images to the dataset, label them and let Pahyderm retrain the model.

```shell
neuro-flow run extend_data --param extend_dataset_by 10
neuro-flow run label_studio
```

- Deploy model to Seldon using our Kubernetes [MLFlow2Seldon operator](https://github.com/neuro-inc/mlops-k8s-mlflow2seldon) (assume operator is already deployed).

## Additional
You might also run MLFlow server by yourself, but in this case, you will need to replace MLFlow server URI in env configuration.

Create persistent disk for Postgresql

```shell
neuro disk create 1G --timeout-unused 30d --name mlops-demo-oss-dogs-postgres
```

Run Postgresql server (needed by MLFlow)

```shell
neuro-flow run postgres
```

Run MLFlow server for experiment and model tracking. Note, in this setup we imply personal use of MLFlow server (each user will connect to its own server)

```shell
neuro-flow run mlflow_server
```
