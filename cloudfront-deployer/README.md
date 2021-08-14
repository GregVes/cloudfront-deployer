# Cloudfront Deployer

A Python program with the `boto3` dependency to perform:

* upload build files to s3 origin (object key = build commmit id)
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
pip3 install -e .
cf-deployer \
    dev
    2681ece875fb3ee469ebeceb6377ebb715e682ec \
    ABCD1234 \
    my-app-bucket \
    my-app-origin-id \
    ./build 
```

## How to run in Docker

```sh
docker build -t cf-deployer .
docker run -t -it \
    --env-file .env \
    -v <local-path-to-your-build-folder>:/home/cf-deployer/build \
    cf-deployer cf-deployer \
    dev \
    2681ece875fb3ee469ebeceb6377ebb715e682ec \
    EAH4B0D2H5DVF \
    curameet-web-dev-bucket \
    curameet-web-dev-frontend-app \
    ./build
```

## How to run in CD pipeline

TODO