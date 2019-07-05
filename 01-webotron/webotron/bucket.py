""" 
Classes for S3 Buckets.
"""
from botocore.exceptions import ClientError
import mimetypes
from pathlib import Path
import webbrowser
from webotron import util
from functools import reduce
import boto3
from hashlib import md5


class BucketManager:
    """Manage an S3 bucket."""

    CHUNK_SIZE = 8388608

    def __init__(self, session):
        """Create a BucketManager object."""
        self.s3 = session.resource('s3')
        self.session = session
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_chunksize=self.CHUNK_SIZE,
            multipart_threshold=self.CHUNK_SIZE
        )
        self.manifest = {}


    def get_region_name(self, bucket):
        """Get the bucket's region name."""
        client = self.s3.meta.client
        bucket_location = client.get_bucket_location(Bucket=bucket.name)

        return bucket_location["LocationConstraint"] or 'us-east-1'

    def delete_bucket(self, bucket_name):
        bucket = self.get_bucket(bucket_name)
        for key in bucket.objects.all():
            key.delete()
        bucket.delete()

    def get_bucket(self, bucket_name):
        """Get a bucket by name."""
        return self.s3.Bucket(bucket_name)


    def get_bucket_url(self, bucket):
        """Get the website URL for this bucket."""
        return "http://{}.{}".format(
            bucket.name,
            util.get_endpoint(self.get_region_name(bucket)).host
        )
    

    def load_manifest(self, bucket_name):
        """Load manifest for caching purposes."""
        paginator = self.s3.meta.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                self.manifest[obj['Key']] = obj['ETag']
    

    def all_buckets(self):
        """Get an iterator for all buckets"""
        return self.s3.buckets.all()
    
    def all_objects(self, bucket):
        """Get an iterator for all objects in the given bucket"""
        return self.s3.Bucket(bucket).objects.all()
    
    def init_bucket(self, bucket_name):
        """Create a new bucket, or return existing one by name."""
        s3_bucket = None
        try:
            s3_bucket = self.s3.create_bucket(
                Bucket= bucket_name,
                CreateBucketConfiguration={'LocationConstraint': self.session.region_name}
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.s3.Bucket(bucket_name)
            else:
                raise e
        return s3_bucket

    def set_policy(self, bucket):
        """Set bucket policy to be readabke by everyone."""
        policy = """
        {
        "Version":"2012-10-17",
        "Statement":[{
        "Sid":"PublicReadGetObject",
        "Effect":"Allow",
        "Principal": "*",
            "Action":["s3:GetObject"],
            "Resource":["arn:aws:s3:::%s/*"
            ]
            }
        ]
        }
        """ % bucket.name
        #Remove any white space at the beginning or at the end of the string
        policy = policy.strip()

        pol = bucket.Policy()
        pol.put(Policy=policy)
    

    def configure_website(self, bucket):
        ws = bucket.Website()
        ws.put(WebsiteConfiguration={
            'ErrorDocument': {
                'Key': 'error.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
            }
        })
    
    def configure_website_spa(self, bucket):
        ws = bucket.Website()
        ws.put(WebsiteConfiguration={
            'ErrorDocument': {
                'Key': 'index.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
            }
        })


    @staticmethod
    def hash_data(data):
        """Generate md5 hash for data."""
        hash = md5()
        hash.update(data)

        return hash

    def gen_etag(self, path):
        """Generate etag for file."""
        hashes = []

        with open(path, 'rb') as f:
            while True:
                #read the file by the chunk size
                data = f.read(self.CHUNK_SIZE)

                if not data:
                    break

                hashes.append(self.hash_data(data))
        #If the file is empty
        if not hashes:
            return
        # If the file only has one chunk of data (file size is less than the chunk size)
        elif len(hashes) == 1:
            return '"{}"'.format(hashes[0].hexdigest())
        else:
            #Append each chunk into a string and hash it
            hash = self.hash_data(reduce(lambda x, y: x + y, (h.digest() for h in hashes)))
            return '"{}-{}"'.format(hash.hexdigest(), len(hashes))


    def upload_file(self, bucket, path, key):
        """Upload path to s3_bucket at key."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'

        etag = self.gen_etag(path)
        if self.manifest.get(key, '') == etag:
            print("skipping...")
            return
        
        print('Uploading')
        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            },
            Config=self.transfer_config
        )


    def sync(self, pathname, bucket_name):
        s3_bucket = self.s3.Bucket(bucket_name)
        self.load_manifest(bucket_name)
        # .expanduser(): get the full absolute path of the given folder
        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir(): handle_directory(p)
                if p.is_file(): self.upload_file(s3_bucket, str(p), str(p.relative_to(root)).replace("\\","/"))
        handle_directory(root)
        # websiteUrl = "http://%s.s3-website-ap-southeast-2.amazonaws.com" % bucket_name
        # webbrowser.open(websiteUrl)
        

    

        
