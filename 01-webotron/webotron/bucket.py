""" 
Classes for S3 Buckets.
"""
from botocore.exceptions import ClientError
import mimetypes
from pathlib import Path
import webbrowser

class BucketManager:
    """Manage an S3 bucket."""
    def __init__(self, session):
        """Create a BucketManager object."""
        self.s3 = session.resource('s3')
    
    def all_buckets(self):
        """Get an iterator for all buckets"""
        return self.s3.buckets.all()
    
    def all_objects(self, bucket):
        """Get an iterator for all objects in the given bucket"""
        return self.s3.Bucket(bucket).objects.all()
    
    def init_bucket(self, bucket_name, session):
        """Create a new bucket, or return existing one by name."""
        s3_bucket = None
        try:
            s3_bucket = self.s3.create_bucket(
                Bucket= bucket_name,
                CreateBucketConfiguration={'LocationConstraint': session.region_name}
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

    def upload_file(self, bucket, path, key):
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            }
        )

    def sync(self, pathname, bucket_name):
        s3_bucket = self.s3.Bucket(bucket_name)
        # .expanduser(): get the full absolute path of the given folder
        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for p in target.iterdir():
                print("uploading...")
                if p.is_dir(): handle_directory(p)
                if p.is_file(): self.upload_file(s3_bucket, str(p), str(p.relative_to(root)).replace("\\","/"))
        handle_directory(root)
        websiteUrl = "http://%s.s3-website-ap-southeast-2.amazonaws.com" % bucket_name
        webbrowser.open(websiteUrl)
        

    

        
