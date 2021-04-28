# startup-package-test

The project description is here.

## Quick Start

Sign up at [neu.ro](https://neu.ro) and setup your local machine according to [instructions](https://docs.neu.ro/).

Assumption: Pachyderm cluster is ready and contains a `dogs-demo` repository.

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
neuro disk create --name postgres 1G
```

Create a secret with a private key for GitHub access

```shell
neuro secret create gh-rsa @~/.ssh/id_rsa
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

## The flow

Download full dataset to storage

```shell
neuro-flow run prepare_remote_dataset
```

Pick 15 images from the dataset and put them under Pachyderm

```shell
neuro-flow run extend_data --param extend_dataset_by 15
```

Run LabelStudio in browser in order to label images for training

```shell
neuro-flow run label_studio
```

Perform labeling. Label Studio closes automatically when all images are marked up. Neu.ro platform updates the dataset in Pachyderm and this update triggers the Pachyderm pipeline, which in turns triggers model training. You may follow the training process via:

```shell
pachctl inspect pipeline train 
```

Check the results in MLFlow when training in complete

(Optional step) Add 10 more images to the dataset, label them and let Pahyderm to re-train the model.

```shell
neuro-flow run extend_data --param extend_dataset_by 10
neuro-flow run label_studio
pachctl inspect pipeline train 
```

Pick a run id value from ML Flow web UI and deploy trained model via Seldon

```shell
neuro-flow run deploy_inference_platform --param run_id XXXXXX
```

Run deployed model's stress test via locust (open up web UI)

```shell
neuro-flow run locust
```
