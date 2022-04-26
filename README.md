# startup-package-test

* If you want to use S3 for data storage (no data versioning) and manual training process, rename `.neuro/live-s3.yml` to `.neuro/live.yml` and follow the docs from [AWS-S3.md](./AWS-S3.md)
* If you want to use Pachyderm for data versioning and automatic training pipeline triggering, rename `.neuro/live-s3.yml` to `.neuro/live.yml` and  follow the docs from [Pachyderm.md](./Pachyderm.md) (NOTE: this requires approval from the neu.ro MLOps team)