import sys, os, boto3, pprint, shutil, subprocess, time, argparse

"""
This Python script is used to update a Cloudfront distribution
"""

class CloudFrontDeployer:

  def __init__(self, args):
    self.env = args.env
    self.bucket_name = args.bucket_name
    self.origin_id = args.origin_id
    self.commit_id = args.commit_id
    self.distribution_id = args.distribution_id
    self.build_dir = args.build_dir

    self.aws = boto3.Session(
      aws_access_key_id=args.aws_access_key_id,
      aws_secret_access_key=args.aws_secret_access_key
    )

  # upload build files to app s3 origin 
  def update_origin(self):
    s3_client = self.aws.client('s3')
    config =  '{}/config-{}.js'.format(self.build_dir, self.env)
    destination = '{}/config.js'.format(self.commit_id)

    # Upload right config file
    print("Uploading {} config file".format(self.env))
    s3_client.upload_file(config, self.bucket_name, destination)

    # Upload build files
    try:
      command = "aws s3 cp --recursive --exclude 'config.js' --exclude 'config-*.js' {} s3://{}/{}".format(self.build_dir, self.bucket_name, self.commit_id)
      print("Uploading {} build files to s3".format(self.env))
      subprocess.run(["/bin/bash", "-c", command])
    except subprocess.CalledProcessError as e:
      sys.exit(e.stderr.decode('utf-8'))

  # update distibution config's origin path with commit id
  def update_distribution(self):
    cf_client = self.aws.client("cloudfront")
    config = cf_client.get_distribution_config(Id=self.distribution_id)
    eTag = config["ETag"]

    origins = config["DistributionConfig"]["Origins"]["Items"]

    app_origin = [origin for origin in origins if origin["Id"] == self.origin_id ]
    app_origin[0]["OriginPath"] = "/{}".format(self.commit_id)

    for i in range(len(origins)):
      if origins[i]["Id"] == self.origin_id:
        del origins[i]
    origins.append(app_origin[0])

    config["DistributionConfig"]["Origins"]["Items"] = origins

    print("Updating {} CloudFront distribution".format(self.env))
    cf_client.update_distribution(
      Id=self.distribution_id,
      DistributionConfig=config["DistributionConfig"],
      IfMatch=eTag
    )

    print("Cleaning CloudFront Edge caches")
    response = cf_client.create_invalidation(
      DistributionId=self.distribution_id,
      InvalidationBatch={
        "Paths": {
          "Quantity": 1,
          "Items": ["/*"]
        },
        "CallerReference": str(time.time()).replace(".", "")
      },
    )

    if response["ResponseMetadata"]["HTTPStatusCode"] != 201:
      pprint.pprint(response)
      sys.exit()

    print("{} CloudFront distribution updated".format(self.env))

def main():
  parser = argparse.ArgumentParser(description="Update Cloudfront distribution")
  parser.add_argument("env", type=str, help="Environment of the targeted distribution")
  parser.add_argument("commit_id", type=str, help="ID of the commit that triggered the build")
  parser.add_argument('distribution_id', type=str, help="ID of the Cloudfront distribution")
  parser.add_argument('bucket_name', type=str, help="Name of the s3 bucket origin of the app")
  parser.add_argument('origin_id', type=str, help="Name of the s3 origin")
  parser.add_argument('build_dir', type=str, help="Path to the build files")
  args = parser.parse_args()

  try:
    args.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    args.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
  except KeyError:
    print('Mising AWS_ACCESS_KEY_ID and/or AWS_SECRET_ACCESS_KEY. Please be sure those system variables are set')
    sys.exit()
  deployer = CloudFrontDeployer(args)
  deployer.update_origin()
  deployer.update_distribution()

if __name__ == "__main__":
	main()