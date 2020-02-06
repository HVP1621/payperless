import ibm_boto3
from ibm_botocore.client import Config
from  ibm_botocore.exceptions import ClientError

#~~~~~~~~~~~~~~~~~~~~~~~ Conection to COS Buckets ~~~~~~~~~~~~~~~~~~~~~~~#
# Constants for IBM COS values
COS_ENDPOINT = "https://s3.au-syd.objectstorage.softlayer.net" # Current list avaiable ath ttps://control.cloud-object-storage.cloud.ibm.com/v2/endpoints
COS_API_KEY_ID = "3h2SAwb7olaQnpHVC1NJeHwFT-xTodI9gtCJQ9HIkaIp"
COS_AUTH_ENDPOINT = "https://iam.bluemix.net/oidc/token"
COS_RESOURCE_CRN = "3e71e118-30e1-4e9e-b795-165f3959b051"
COS_BUCKET_LOCATION = "au-syd"

cos_resource = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

cos_client = ibm_boto3.client("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

#~~~~~~~~~~~~~~~~~~~~~~~ COS BUCKET FUNCTIONS  START ~~~~~~~~~~~~~~~~~~~~~~~#


def create_bucket(bucket_name):
    print("Creating new bucket: {0}".format(bucket_name))
    try:
        cos_resource.Bucket(bucket_name).create(
            ACL= 'private',
            CreateBucketConfiguration={
                "LocationConstraint":'au-syd-standard'
            },
            IBMServiceInstanceId=COS_RESOURCE_CRN
        )
        print("Bucket: {0} created!".format(bucket_name))
        return 1

    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
        return 0
    except Exception as e:
        print("Unable to create bucket: {0}".format(e))
        return 0


def get_bucket_contents(bucket_name):
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        files = cos_resource.Bucket(bucket_name).objects.all()
        file_names = []
        file_update = []
        for file in files:
            file_names.append(file.key)
            file_update.append(file.last_modified)

        return file_names, file_update

    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))

def upload2bucket(Filename, Bucket, Key):
    cos_client.upload_file(Filename=Filename,Bucket=Bucket,Key=Key)


def delete_item(bucket_name, item_name):
    print("Deleting item: {0}".format(item_name))
    try:
        cos_resource.Object(bucket_name, item_name).delete()
        print("Item: {0} deleted!".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to delete item: {0}".format(e))
