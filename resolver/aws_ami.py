# -*- coding: utf-8 -*-

import abc
import six
import logging

from botocore.exceptions import ClientError
from sceptre.resolvers import Resolver
from resolver.aws_ami_exceptions import ImageNotFoundError

TEMPLATE_EXTENSION = ".yaml"

@six.add_metaclass(abc.ABCMeta)
class AwsAmiBase(Resolver):
    """
    A abstract base class which provides methods for getting Image ID.
    """

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        super(AwsAmiBase, self).__init__(*args, **kwargs)

    def _get_image_id(self, filters, region, profile=None, owners=None):
        """
        Attempts to get the Image ID with tag:Name by ``param``
        :param filters: The filters of the Image in which to return.
        :type param: dict
        :returns: Image ID.
        :rtype: str
        :raises: KeyError
        """
        response = self._request_image(filters, region, profile, owners)

        try:
            self.logger.debug("Got response: {0}".format(response))
            unsorted_images = response['Images']
            sorted_images = sorted(unsorted_images, key=lambda x: x['CreationDate'],reverse=True)
            return sorted_images[0]['ImageId']
        except KeyError:
            self.logger.error("%s - Invalid response looking for: %s",
                              self.stack.name, filters)
            raise

    def _request_image(self, filters, region, profile=None, owners=None):
        """
        Communicates with AWS EC2 to fetch VPC Information.
        :returns: The JSON block of the VPC info
        :rtype: dict
        :raises: resolver.exceptions.ImageNotFoundError
        """
        connection_manager = self.stack.connection_manager

        try:
            self.logger.debug("Calling ec2.describe_images")
            kwargs = {"Filters": filters}
            if owners:
                kwargs["Owners": owners]
            response = connection_manager.call(
                service="ec2",
                command="describe_images",
                kwargs=kwargs,
                region=region,
                profile=profile
            )
            self.logger.debug("Finished calling ec2.describe_images")
        except ClientError as e:
            if "ImageNotFound" in e.response["Error"]["Code"]:
                self.logger.error("%s - ImageNotFound: %s",
                                  self.stack.name, kwargs)
                raise ImageNotFoundError(e.response["Error"]["Message"])
            else:
                raise e
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
            raise
            
        else:
            return response


class AwsAmi(AwsAmiBase):
    """
    Resolver for retrieving the value of Image ID.
    :param argument: The AMI name to get.
    :type argument: str
    """

    def __init__(self, *args, **kwargs):
        super(AwsAmi, self).__init__(*args, **kwargs)

    def resolve(self):
        """
        Retrieves the value of AMI info
        :returns: The decoded value of the AMI info
        :rtype: str
        """
        args = self.argument
        if not args:
            raise ValueError("Missing argument")

        instance_id = None
        self.logger.debug(
            "Resolving EC2 Image with argument: {0}".format(args)
        )
        name = self.argument
        region = self.stack.region
        profile = self.stack.profile
        filters = [
            {
                'Name': 'name',
                'Values': [name]
            }
        ]
        owners = None
        if isinstance(args, dict):
            if 'name' in args:
                name = args['name']
                filters = [
                    {
                        'Name': 'name',
                        'Values': [name]
                    }
                ]
            else:
                raise ValueError("Missing image name filters")
            if 'owners' in args:
                owners_value = args['owners']
                if isinstance(owners_value, list):
                    owners = owners_value
                else:
                    owners = [owners_value]

            profile = args.get('profile', profile)
            region = args.get('region', region)
            # Parse additional filters
            for key in args.keys():
                if key in ['name', 'region', 'profile', 'owners']:
                    continue
                value = args.get(key)
                if isinstance(value, list):
                    filter_value = value
                else:
                    filter_value = [value]
                filters.append({'Name': key, 'Values': filter_value})

        self.logger.debug("Resolving image with name pattern: {0}".format(name))
        instance_id = self._get_image_id(filters, region, profile, owners)
        return instance_id