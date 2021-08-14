# Cloudfront Deployer

A Python program with the `boto3` dependency to perform:

* upload new build files to s3 origin (object key = build commmit id)
* update distribution config's origin path with build commit id
* invalidate CloudFront Edge caches

## Required arguments to pass to the script

* `env` > for app's config file suffix such as `config-{env}.js`
* `commit_id` > commit of the current build, used for creating a bucket object where build files will be uploaded
* `distribution_id` > see `aws list-distributions` command
* `bucket_name` > s3 origin for the app
* `origin_id` >  id of the s3 origin
* `build_dir`

## How to run locally

```sh
python3 -m venv .
source bin/activate
pip3 install -r requirements.txt
python src/deploy.py <env> <commit_id> <distribution_id> <bucket_name> <origin_id> <build_dir> 
```

## How to run in Docker

Use an `.env` file for your `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

```sh
docker build -t cf-deployer .

docker run -t -it \
    --env-file .env \
    -v <local-path-to-your-build-folder>:/home/cf-deployer/build \
    cf-deployer cf-deployer \
    dev \
    2681mce875fbkee469ebeceb9377ebb715e682ec \
    WMH4I0D2H5DVF \
    app-web-dev-bucket \
    app-web-dev-frontend-app \
    ./build
```

## How to run in CD pipeline

### Push the Docker image to your Hub repo

```sh
sh build-and-push.sh <your-docker-hub-repo> <app-tag>
```

### Use it in your CD pipeline

This is an example with Codeship

```yml
# service
cf-deployer:
  image: <your-repo>/cf-deployer:0.1.0
  encrypted_env_file: .codeship/env.encrypted # stores AWS creds for the container
  volumes_from:
    - web-build-service
  environment:
    - PYTHONUNBUFFERED=1
  cached: true
  default_cache_branch: 'master'

# step
  steps:
    - name: Update DEV deployment
      command: /bin/bash -c 'python deploy.py dev $CI_COMMIT_ID $CLOUDFRONT_DEV_DIST_ID $CLOUDFRONT_DEV_BUCKET_NAME $CLOUDFRONT_DEV_ORIGIN_ID /usr/app/build'
```