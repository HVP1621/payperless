
import datetime
import hashlib
import hmac
import requests
from requests.utils import quote

access_key = '564cbef2d57b427488eada21d06091b4'
secret_key = '5ad4e48f889590bc1c04115b8d1e1c8cc19f777bfcfedafd'

# request elements
http_method = 'GET'
region = 'au-syd' # us-south
bucket = 'extract-sig'
cos_endpoint = 's3.au-syd.objectstorage.softlayer.net'
host = cos_endpoint
endpoint = 'https://' + host
# object_key = 'random.jpg'
expiration = 86400  # time in seconds


# hashing methods
def hash(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


# region is a wildcard value that takes the place of the AWS region value
# as COS doen't use regions like AWS, this parameter can accept any string
def createSignatureKey(key, datestamp, region, service):
    keyDate = hash(('AWS4' + key).encode('utf-8'), datestamp)
    keyRegion = hash(keyDate, region)
    keyService = hash(keyRegion, service)
    keySigning = hash(keyService, 'aws4_request')
    return keySigning

def requestURL(bucket_name, filename):
   object_key = filename
   bucket = bucket_name
   # assemble the standardized request
   time = datetime.datetime.utcnow()
   timestamp = time.strftime('%Y%m%dT%H%M%SZ')
   datestamp = time.strftime('%Y%m%d')

   standardized_querystring = ('X-Amz-Algorithm=AWS4-HMAC-SHA256' +
                               '&X-Amz-Credential=' + access_key + '/' + datestamp + '/' + region + '/s3/aws4_request' +
                               '&X-Amz-Date=' + timestamp +
                               '&X-Amz-Expires=' + str(expiration) +
                               '&X-Amz-SignedHeaders=host')
   standardized_querystring_url_encoded = quote(standardized_querystring, safe='&=')

   standardized_resource = '/' + bucket + '/' + object_key
   standardized_resource_url_encoded = quote(standardized_resource, safe='&')

   payload_hash = 'UNSIGNED-PAYLOAD'
   standardized_headers = 'host:' + host
   signed_headers = 'host'

   standardized_request = (http_method + '\n' +
                           standardized_resource + '\n' +
                           standardized_querystring_url_encoded + '\n' +
                           standardized_headers + '\n' +
                           '\n' +
                           signed_headers + '\n' +
                           payload_hash).encode('utf-8')

   # assemble string-to-sign
   hashing_algorithm = 'AWS4-HMAC-SHA256'
   credential_scope = datestamp + '/' + region + '/' + 's3' + '/' + 'aws4_request'
   sts = (hashing_algorithm + '\n' +
          timestamp + '\n' +
          credential_scope + '\n' +
          hashlib.sha256(standardized_request).hexdigest())

   # generate the signature
   signature_key = createSignatureKey(secret_key, datestamp, region, 's3')
   signature = hmac.new(signature_key,
                        (sts).encode('utf-8'),
                        hashlib.sha256).hexdigest()

   # create and send the request
   # the 'requests' package autmatically adds the required 'host' header
   request_url = (endpoint + '/' +
                  bucket + '/' +
                  object_key + '?' +
                  standardized_querystring_url_encoded +
                  '&X-Amz-Signature=' +
                  signature)

   # print(('request_url: %s' % request_url))
   return request_url

if __name__ == '__main__':
  requestURL('extract_sig', 'lol')
