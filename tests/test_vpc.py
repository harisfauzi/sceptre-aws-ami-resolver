# -*- coding: utf-8 -*-

import pytest
from mock import MagicMock, patch, sentinel

from botocore.exceptions import ClientError

from sceptre.connection_manager import ConnectionManager
from sceptre.stack import Stack

from resolver.aws_ami import AwsAmi, AwsAmiBase
from resolver.aws_ami_exceptions import ImageNotFoundError


region = 'us-east-1'


class TestImageResolver(object):
    def test_resolve_str_arg_no_param_name(self):
        stack = MagicMock(spec=Stack)
        stack.profile = "test_profile"
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_image_resolver = AwsAmi(
            None, stack
        )
        with pytest.raises(ValueError):
            stack_image_resolver.resolve()

    def test_resolve_obj_arg_no_param_name(self):
        stack = MagicMock(spec=Stack)
        stack.profile = "test_profile"
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_image_resolver = AwsAmi(
            {}, stack
        )
        with pytest.raises(ValueError):
            stack_image_resolver.resolve()

    @patch(
        "resolver.aws_ami.AwsAmi._get_image_id"
    )
    def test_resolve_str_arg(self, mock_get_image_id):
        stack = MagicMock(spec=Stack)
        stack.profile = "test_profile"
        stack.region = region
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_image_resolver = AwsAmi(
            "amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs", stack
        )
        mock_get_image_id.return_value = "ami-04d0fca9fc2734804"
        stack_image_resolver.resolve()
        mock_get_image_id.assert_called_once_with(
            [{'Name': 'name', 'Values': ['amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs']}], region, "test_profile", None
        )

    @patch(
        "resolver.aws_ami.AwsAmi._get_image_id"
    )
    def test_resolve_obj_arg_no_profile(self, mock_get_image_id):
        stack = MagicMock(spec=Stack)
        stack.profile = "test_profile"
        stack.region = region
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_image_resolver = AwsAmi(
            {"name": "amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs"}, stack
        )
        mock_get_image_id.return_value = "ami-04d0fca9fc2734804"
        stack_image_resolver.resolve()
        mock_get_image_id.assert_called_once_with(
            [{'Name': 'name', 'Values': ['amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs']}], region, "test_profile", None
        )

    @patch(
        "resolver.aws_ami.AwsAmi._get_image_id"
    )
    def test_resolve_name_owner_arg_no_profile(self, mock_get_image_id):
        stack = MagicMock(spec=Stack)
        stack.profile = "test_profile"
        stack.region = region
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_image_resolver = AwsAmi(
            {
                "name": "amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs",
                "owners": "amazon"
            }, stack
        )
        mock_get_image_id.return_value = "ami-04d0fca9fc2734804"
        stack_image_resolver.resolve()
        mock_get_image_id.assert_called_once_with(
            [{'Name': 'name', 'Values': ['amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs']}], region, "test_profile", ['amazon']
        )

    @patch(
        "resolver.aws_ami.AwsAmi._get_image_id"
    )
    def test_resolve_name_tags_self_arg_no_profile(self, mock_get_image_id):
        stack = MagicMock(spec=Stack)
        stack.profile = "test_profile"
        stack.region = region
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_image_resolver = AwsAmi(
            {
                "name": "amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs",
                "tag:Name": "test-ami",
                "tag:branch": ["main","development"],
                "owners": "amazon"
            }, stack
        )
        mock_get_image_id.return_value = "ami-04d0fca9fc2734804"
        stack_image_resolver.resolve()
        mock_get_image_id.assert_called_once_with(
            [
                {
                    'Name': 'name',
                    'Values': ['amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs']
                },
                {
                    'Name': 'tag:Name',
                    'Values': ['test-ami']
                },
                {
                    'Name': 'tag:branch',
                    'Values': ['main', 'development']
                }
            ],
            region,
            "test_profile",
            ['amazon']
        )

    @patch(
        "resolver.aws_ami.AwsAmi._get_image_id"
    )
    def test_resolve_obj_arg_profile_override(self, mock_get_image_id):
        stack = MagicMock(spec=Stack)
        stack.profile = "test_profile"
        stack.region = region
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)
        stack_image_resolver = AwsAmi(
            {
                "name": "amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs",
                "profile": "new_profile"
            },
            stack
        )
        mock_get_image_id.return_value = "ami-04d0fca9fc2734804"
        stack_image_resolver.resolve()
        mock_get_image_id.assert_called_once_with(
            [{'Name': 'name', 'Values': ['amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs']}], region, "new_profile", None
        )

    @patch(
        "resolver.aws_ami.AwsAmi._get_image_id"
    )
    def test_resolve_obj_arg_region_override(self, mock_get_image_id):
        stack = MagicMock(spec=Stack)
        stack.profile = "test_profile"
        stack.region = region
        stack.dependencies = []
        stack._connection_manager = MagicMock(spec=ConnectionManager)

        custom_region = 'ap-southeast-1'
        assert custom_region != region

        stack_image_resolver = AwsAmi(
            {
                "name": "amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs",
                "region": custom_region,
                "profile": "new_profile"
            },
            stack
        )
        mock_get_image_id.return_value = "ami-04d0fca9fc2734804"
        stack_image_resolver.resolve()
        mock_get_image_id.assert_called_once_with(
            [{'Name': 'name', 'Values': ['amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs']}], custom_region, "new_profile", None
        )


class MockAwsAmiBase(AwsAmiBase):
    """
    MockBaseResolver inherits from the abstract base class
    AwsAmiBase, and implements the abstract methods. It is used
    to allow testing on AwsAmiBase, which is not otherwise
    instantiable.
    """

    def __init__(self, *args, **kwargs):
        super(MockAwsAmiBase, self).__init__(*args, **kwargs)

    def resolve(self):
        pass


class TestAwsAmiBase(object):

    def setup_method(self, test_method):
        self.stack = MagicMock(spec=Stack)
        self.stack.name = "test_name"
        self.stack._connection_manager = MagicMock(
            spec=ConnectionManager
        )
        self.base_ami = MockAwsAmiBase(
            None, self.stack
        )

    @patch(
        "resolver.aws_ami.AwsAmiBase._request_image"
    )
    def test_get_image_id_with_valid_name(self, mock_request_image):
        mock_request_image.return_value = {
          "Images": [
            {
              "Architecture": "x86_64",
              "CreationDate": "2023-03-22T11:02:49.000Z",
              "ImageId": "ami-04d0fca9fc2734804",
              "ImageLocation": "amazon/amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs",
              "ImageType": "machine",
              "Public": True,
              "OwnerId": "137112412989",
              "PlatformDetails": "Linux/UNIX",
              "UsageOperation": "RunInstances",
              "State": "available",
              "BlockDeviceMappings": [
                {
                  "DeviceName": "/dev/xvda",
                  "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0a1b681cb42513928",
                    "VolumeSize": 8,
                    "VolumeType": "standard",
                    "Encrypted": False
                  }
                }
              ],
              "Description": "Amazon Linux 2 AMI 2.0.20230320.0 x86_64 HVM ebs",
              "EnaSupport": True,
              "Hypervisor": "xen",
              "ImageOwnerAlias": "amazon",
              "Name": "amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs",
              "RootDeviceName": "/dev/xvda",
              "RootDeviceType": "ebs",
              "SriovNetSupport": "simple",
              "VirtualizationType": "hvm",
              "DeprecationTime": "2025-03-22T11:02:49.000Z"
            }
          ]
        }

        response = self.base_ami._get_image_id("amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs", region)
        assert response == "ami-04d0fca9fc2734804"

    @patch(
        "resolver.aws_ami.AwsAmiBase._request_image"
    )
    def test_get_image_id_with_valid_pattern(self, mock_request_image):
        mock_request_image.return_value = {
          "Images": [
            {
              "Architecture": "x86_64",
              "CreationDate": "2023-03-22T11:02:49.000Z",
              "ImageId": "ami-04d0fca9fc2734804",
              "ImageLocation": "amazon/amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs",
              "ImageType": "machine",
              "Public": True,
              "OwnerId": "137112412989",
              "PlatformDetails": "Linux/UNIX",
              "UsageOperation": "RunInstances",
              "State": "available",
              "BlockDeviceMappings": [
                {
                  "DeviceName": "/dev/xvda",
                  "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0a1b681cb42513928",
                    "VolumeSize": 8,
                    "VolumeType": "standard",
                    "Encrypted": False
                  }
                }
              ],
              "Description": "Amazon Linux 2 AMI 2.0.20230320.0 x86_64 HVM ebs",
              "EnaSupport": True,
              "Hypervisor": "xen",
              "ImageOwnerAlias": "amazon",
              "Name": "amzn2-ami-hvm-2.0.20230320.0-x86_64-ebs",
              "RootDeviceName": "/dev/xvda",
              "RootDeviceType": "ebs",
              "SriovNetSupport": "simple",
              "VirtualizationType": "hvm",
              "DeprecationTime": "2025-03-22T11:02:49.000Z"
            },
            {
              "Architecture": "x86_64",
              "CreationDate": "2023-02-09T12:04:56.000Z",
              "ImageId": "ami-0850aa6a716348ce1",
              "ImageLocation": "amazon/amzn2-ami-hvm-2.0.20230207.0-x86_64-ebs",
              "ImageType": "machine",
              "Public": True,
              "OwnerId": "137112412989",
              "PlatformDetails": "Linux/UNIX",
              "UsageOperation": "RunInstances",
              "State": "available",
              "BlockDeviceMappings": [
                {
                  "DeviceName": "/dev/xvda",
                  "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0f47b9a59dccdea39",
                    "VolumeSize": 8,
                    "VolumeType": "standard",
                    "Encrypted": False
                  }
                }
              ],
              "Description": "Amazon Linux 2 AMI 2.0.20230207.0 x86_64 HVM ebs",
              "EnaSupport": True,
              "Hypervisor": "xen",
              "ImageOwnerAlias": "amazon",
              "Name": "amzn2-ami-hvm-2.0.20230207.0-x86_64-ebs",
              "RootDeviceName": "/dev/xvda",
              "RootDeviceType": "ebs",
              "SriovNetSupport": "simple",
              "VirtualizationType": "hvm",
              "DeprecationTime": "2025-02-09T12:04:56.000Z"
            },
            {
              "Architecture": "x86_64",
              "CreationDate": "2023-03-08T13:07:27.000Z",
              "ImageId": "ami-077de27e0c6f82f33",
              "ImageLocation": "amazon/amzn2-ami-hvm-2.0.20230307.0-x86_64-ebs",
              "ImageType": "machine",
              "Public": True,
              "OwnerId": "137112412989",
              "PlatformDetails": "Linux/UNIX",
              "UsageOperation": "RunInstances",
              "State": "available",
              "BlockDeviceMappings": [
                {
                  "DeviceName": "/dev/xvda",
                  "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0dc12a551fb6c6c5f",
                    "VolumeSize": 8,
                    "VolumeType": "standard",
                    "Encrypted": False
                  }
                }
              ],
              "Description": "Amazon Linux 2 AMI 2.0.20230307.0 x86_64 HVM ebs",
              "EnaSupport": True,
              "Hypervisor": "xen",
              "ImageOwnerAlias": "amazon",
              "Name": "amzn2-ami-hvm-2.0.20230307.0-x86_64-ebs",
              "RootDeviceName": "/dev/xvda",
              "RootDeviceType": "ebs",
              "SriovNetSupport": "simple",
              "VirtualizationType": "hvm",
              "DeprecationTime": "2025-03-08T13:07:27.000Z"
            },
            {
              "Architecture": "x86_64",
              "CreationDate": "2023-04-04T22:06:37.000Z",
              "ImageId": "ami-066fdb387a3b86d3d",
              "ImageLocation": "amazon/amzn2-ami-hvm-2.0.20230404.0-x86_64-ebs",
              "ImageType": "machine",
              "Public": True,
              "OwnerId": "137112412989",
              "PlatformDetails": "Linux/UNIX",
              "UsageOperation": "RunInstances",
              "State": "available",
              "BlockDeviceMappings": [
                {
                  "DeviceName": "/dev/xvda",
                  "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-05ca94d0067775a7c",
                    "VolumeSize": 8,
                    "VolumeType": "standard",
                    "Encrypted": False
                  }
                }
              ],
              "Description": "Amazon Linux 2 AMI 2.0.20230404.0 x86_64 HVM ebs",
              "EnaSupport": True,
              "Hypervisor": "xen",
              "ImageOwnerAlias": "amazon",
              "Name": "amzn2-ami-hvm-2.0.20230404.0-x86_64-ebs",
              "RootDeviceName": "/dev/xvda",
              "RootDeviceType": "ebs",
              "SriovNetSupport": "simple",
              "VirtualizationType": "hvm",
              "DeprecationTime": "2025-04-04T22:06:37.000Z"
            },
            {
              "Architecture": "x86_64",
              "CreationDate": "2023-04-11T07:47:10.000Z",
              "ImageId": "ami-06516aa38ccc9ae63",
              "ImageLocation": "amazon/amzn2-ami-hvm-2.0.20230404.1-x86_64-ebs",
              "ImageType": "machine",
              "Public": True,
              "OwnerId": "137112412989",
              "PlatformDetails": "Linux/UNIX",
              "UsageOperation": "RunInstances",
              "State": "available",
              "BlockDeviceMappings": [
                {
                  "DeviceName": "/dev/xvda",
                  "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-070b29d0c671a0a62",
                    "VolumeSize": 8,
                    "VolumeType": "standard",
                    "Encrypted": False
                  }
                }
              ],
              "Description": "Amazon Linux 2 AMI 2.0.20230404.1 x86_64 HVM ebs",
              "EnaSupport": True,
              "Hypervisor": "xen",
              "ImageOwnerAlias": "amazon",
              "Name": "amzn2-ami-hvm-2.0.20230404.1-x86_64-ebs",
              "RootDeviceName": "/dev/xvda",
              "RootDeviceType": "ebs",
              "SriovNetSupport": "simple",
              "VirtualizationType": "hvm",
              "DeprecationTime": "2025-04-11T07:47:10.000Z"
            },
            {
              "Architecture": "x86_64",
              "CreationDate": "2023-04-20T19:28:30.000Z",
              "ImageId": "ami-0adaa115ff2cc4adf",
              "ImageLocation": "amazon/amzn2-ami-hvm-2.0.20230418.0-x86_64-ebs",
              "ImageType": "machine",
              "Public": True,
              "OwnerId": "137112412989",
              "PlatformDetails": "Linux/UNIX",
              "UsageOperation": "RunInstances",
              "State": "available",
              "BlockDeviceMappings": [
                {
                  "DeviceName": "/dev/xvda",
                  "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-082b1ee5803f9b4d9",
                    "VolumeSize": 8,
                    "VolumeType": "standard",
                    "Encrypted": False
                  }
                }
              ],
              "Description": "Amazon Linux 2 AMI 2.0.20230418.0 x86_64 HVM ebs",
              "EnaSupport": True,
              "Hypervisor": "xen",
              "ImageOwnerAlias": "amazon",
              "Name": "amzn2-ami-hvm-2.0.20230418.0-x86_64-ebs",
              "RootDeviceName": "/dev/xvda",
              "RootDeviceType": "ebs",
              "SriovNetSupport": "simple",
              "VirtualizationType": "hvm",
              "DeprecationTime": "2025-04-20T19:28:30.000Z"
            },
          ]
        }

        response = self.base_ami._get_image_id("amzn2-ami-hvm-2.?.2023????.0-x86_64-ebs", region)
        assert response == "ami-0adaa115ff2cc4adf"

    @patch(
        "resolver.aws_ami.AwsAmiBase._request_image"
    )
    def test_get_image_id_with_invalid_response(self, mock_request_image):
        mock_request_image.return_value = {
            "Images": [
                {
                    "CidrBlock": "10.255.0.0/20",
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "TestVPC"
                        }
                    ]
                }
            ]
        }

        with pytest.raises(KeyError):
            self.base_ami._get_image_id(None, region)

    def test_request_image_with_unkown_boto_error(self):
        self.stack.connection_manager.call.side_effect = ClientError(
            {
                "Error": {
                    "Code": "500",
                    "Message": "Boom!"
                }
            },
            sentinel.operation
        )

        with pytest.raises(ClientError):
            self.base_ami._request_image(None, region)

    def test_request_image_with_image_not_found(self):
        self.stack.connection_manager.call.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ImageNotFound",
                    "Message": "Boom!"
                }
            },
            sentinel.operation
        )

        with pytest.raises(ImageNotFoundError):
            self.base_ami._request_image(None, region)