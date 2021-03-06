# Neu.ro MLOps platform demo project for dogs classification

## Quick Start

Sign up at [app.neu.ro](https://app.neu.ro) and setup your local machine according
to [these instructions](https://docs.neu.ro/getting-started#installing-the-cli).

To get access to the sandbox environment that contains all the components installed and configured,
please [contact our team](team@neu.ro).

## Preparation

```shell
neuro login
```

Edit `.neuro/project.yml` and set owner to your username and role to `<YOUR_USERNAME>/projects/mlops-demo-oss-dogs`.

Build all images used in the flow:

```shell
neuro-flow build ALL
```

Create secret for Label Studio token:

```shell
neuro secret add ls-token token123456
```

Create a new bucket for storing data and AWS credentials

```shell
neuro blob mkbucket --name mlops-demo-oss-dogs
neuro blob mkcredentials mlops-demo-oss-dogs --name mlops-demo-oss-dogs-credentials
```

Download the full dataset to storage:

```shell
neuro-flow run prepare_remote_dataset
```

## The flow

- Pick 15 images from the dataset and put them to S3 bucket:

  ```shell
  neuro-flow run extend_data --param extend_dataset_by 15
  ```

- Run [Label Studio](https://labelstud.io/) in a browser in order to process the images for training. Label Studio
  closes automatically when all images are marked and stores markup result in the same S3 bucket.

  ```shell
  neuro-flow run label_studio
  ```

- Run training with labeled data.

  ```shell
  neuro-flow run train
  ```

- You may follow the training process in the [MLFlow](https://www.mlflow.org/) server's Web UI using the provided link
  or open it again.

  ```shell
  neuro-flow run mlflow_server
  ```

- Pick a run ID value from MLFlow's Web UI and deploy the trained model as a REST API on the platform:

  ```shell
  neuro-flow run deploy_inference_platform --param run_id XXXXXX
  ```

- Run a stress test on the deployed model via Locust (open up web UI), specifying the model's endpoint URI. If the model
  is deployed as a platform job, you should
  use `https://demo-oss-dogs-test-inference--<username>.jobs.<cluster-name>.org.neu.ro/api/v1.0/predictions`,
  and `http://seldon.<cluster-name>.org.neu.ro/seldon/seldon/<model-name>-<model-stage>/api/v1.0/predictions` if the
  model is deployed in Seldon.

  ```shell
  neuro-flow run locust --param endpoint_url <Address>
  ```

- Run [SHAP](https://shap.readthedocs.io/en/latest/index.html) in Jupyter Notebook to explain the output of the trained
  model:

  ```shell
  neuro-flow run jupyter --param run_id XXXXXX
  ```

## Optional steps:

- Add 10 more images to the dataset, label them, and retrain the model:

```shell
neuro-flow run extend_data --param extend_dataset_by 10
neuro-flow run label_studio
neuro-flow run train
```

- Deploy the model to Seldon using our
  Kubernetes [MLFlow2Seldon operator](https://github.com/neuro-inc/mlops-k8s-mlflow2seldon) (contact us
  at `mlops[at]neu.ro` if you need a deployed operator).

## Additional

You might also run an MLFlow server by yourself, but in this case, you will need to replace the MLFlow server URI in
the `env` configuration.

Create a persistent disk for Postgresql:

```shell
neuro disk create 1G --timeout-unused 30d --name mlops-demo-oss-dogs-postgres
```

Run a Postgresql server (needed by MLFlow):

```shell
neuro-flow run postgres
```

Run an MLFlow server for experiment and model tracking. In this setup, we imply personal use of MLFlow server (each user
will connect to their own server).

```shell
neuro-flow run mlflow_server
```
