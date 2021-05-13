# startup-package-test

The project description is here.

## Quick Start

Sign up at [neu.ro](https://app.neu.ro) and setup your local machine according to [instructions](https://docs.neu.ro/).

Assumption: Pachyderm cluster is deployed and ready to create and run the pipelines. It also contains a `dogs-demo` repository.

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

Create persistent disk for Postgresql

```shell
neuro disk create 1G --timeout-unused 30d --name mlops-demo-oss-dogs-postgres
```

Create a secret with a private SSH key for GitHub repository access (pull/push access should be allowed)

```shell
neuro secret add gh-rsa @~/.ssh/id_rsa
```

Run Postgresql server (needed by MLFlow)

```shell
neuro-flow run postgres
```

Run MLFlow server for experiment and model tracking

```shell
neuro-flow run mlflow_server
```

Create Pachyderm pipeline that will (re)train model on every dataset update

```shell
neuro-flow run create_pipeline
```

Download full dataset to storage

```shell
neuro-flow run prepare_remote_dataset
```

## The flow


Pick 50 images from the dataset and put them under Pachyderm, together with their labels

```shell
neuro-flow run extend_data --param extend_dataset_by 50
```

Pick 5 images from the dataset and put them under Pachyderm, without their labels

```shell
neuro-flow run extend_data --param extend_dataset_by 5 --param extend_params ""
```

Run LabelStudio in browser in order to label images for training

```shell
neuro-flow run label_studio
```

Perform labeling. Label Studio closes automatically when all images are marked up. Neu.ro platform updates the dataset in Pachyderm and this update triggers the Pachyderm pipeline, which in turns triggers model training. You may follow the training process via:

```shell
pachctl logs -f -p train 
```

Check the results in MLFlow when training in complete.

(Optional step) Add 10 more images to the dataset, label them and let Pahyderm retrain the model.

```shell
neuro-flow run extend_data --param extend_dataset_by 10
neuro-flow run label_studio
pachctl logs -f -p train 
```

Pick a run id value from ML Flow web UI and deploy trained model via Seldon

```shell
neuro-flow run deploy_inference_platform --param run_id XXXXXX
```

Run deployed model's stress test via locust (open up web UI)

```shell
neuro-flow run locust
```
