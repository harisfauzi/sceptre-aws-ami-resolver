# Overview

The purpose of this resolver is to retrieve EC2 Image ID from the AWS.

## Install

```shell
pip install sceptre-aws-ami-resolver
```
or
```shell
pip install git+https://github.com/harisfauzi/sceptre-aws-ami-resolver.git
```

## Available Resolvers

### aws_ami

Fetches the EC2 Image ID from AWS with given name or other searchable filters.

__Note:__ Sceptre must be run with a user or role that has access to the describe EC2 images (ec2:DescribeImages).

Syntax:

```yaml
parameter|sceptre_user_data:
  <name>: !aws_ami image_name_pattern
```

```yaml
parameter|sceptre_user_data:
  <name>: !aws_ami
    name: image_name_pattern
    owners:
      - amazon
      - self
    tag:Name:
      - this-project
      - that-project
    region: us-east-1
    profile: OtherAccount
```

```yaml
parameter|sceptre_user_data:
  <name>: !aws_ami {"name": "image_name_pattern", "region": "us-east-1", "profile": "OtherAccount"}
```


#### Parameters
* name - Image name (or pattern), mandatory
* 
* owners - Image owners, optional
* region - VPC region, optional, stack region by default
* profile - VPC account profile , optional, stack profile by default
* other searchable filters, see [documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_images.html)

#### Example:

Retrieve the Image ID from an image with the name `amzn2-ami-hvm-2.0.20230221.0-x86_64-ebs`:
```yaml
parameters:
  ImageId: !aws_ami amzn2-ami-hvm-2.0.20230221.0-x86_64-ebs
```

Retrieve the Image ID from the latest image with the pattern `amzn2-ami-hvm-2.?.????????.0-x86_64-ebs`:
```yaml
parameters:
  ImageId: !aws_ami "amzn2-ami-hvm-2.?.????????.0-x86_64-ebs"
```

Retrieve the Image ID from another AWS account:
```yaml
parameters:
  ImageId: !aws_ami
    name: TestAmi
    profile: OtherAccount
```


Retrieve the Image ID of the latest image from another AWS account with `tag:Branch` set to `ready-for-deployment`:
```yaml
parameters:
  ImageId: !aws_ami
    name: TestAmi
    tag:Branch: ready-for-deployment
    profile: OtherAccount
```