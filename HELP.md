# Neuro Project Template Reference

## Development Environment

This template runs on [Neuro Platform](https://neu.ro). 

To dive into the problem solving, you need to sign up at [Neuro Platform](https://neu.ro) website, set up your local machine according to [instructions](https://neu.ro/docs) and log into the Neuro CLI:

```shell
neuro login
```

## Directory structure

| Local directory | Description | Storage URI | Environment mounting point |
|:--------------- |:----------- |:----------- |:-------------------------- | 
| `data/` | Data | `storage:startup-package-test/data/` | `/startup-package-test/data/` | 
| `src/` | Python modules | `storage:startup-package-test/src/` | `/startup-package-test/src/` |
| `config/` | Configuration files | `storage:startup-package-test/config/` | `/startup-package-test/config/` |
| `notebooks/` | Jupyter notebooks | `storage:startup-package-test/notebooks/` | `/startup-package-test/notebooks/` |

## Development

Follow the instructions below to set up the environment on Neuro and start a Jupyter development session.

### Setup development environment 

```shell
make setup
```

* Several files from the local project are uploaded to the platform storage (namely, `requirements.txt`,  `apt.txt`, `setup.cfg`).
* A new job is started in our [base environment](https://hub.docker.com/r/neuromation/base). 
* Pip requirements from `requirements.txt` and apt applications from `apt.txt` are installed in this environment.
* The updated environment is saved under a new project-dependent name and is used further on.

### Run Jupyter with GPU 

```shell
neuro-flow run jupyter
```

* The content of the `src` and `notebooks` directories is uploaded to the platform storage.
* A job with Jupyter is started, and its web interface is opened in the local web browser window.

### Kill Jupyter

```shell 
neuro-flow kill jupyter
```

* The job with Jupyter Notebooks is terminated. The notebooks are saved on the platform storage. You may run `make download-notebooks` to download them to the local `notebooks/` directory.
