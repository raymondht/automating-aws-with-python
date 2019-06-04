#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Webotron automates the process of deploying static web
- Configure AWS S3 buckets 
    - Create them 
    - Set them up for static website hosting
    - Deploy local files to them
- Configure DNS with AWS route Route 53
- Configure a Content Delivery Network and SSL with AWS CloudFront
"""
from bucket import BucketManager
import webbrowser

import boto3
import click

session = boto3.Session(profile_name='pythonAutomation')
BucketManager = BucketManager(session)
# 


@click.group()
def cli():
    """Webotron deploys websites to AWS"""
    pass

@cli.command('list-buckets')
def list_bucket():
    """List all s3 buckets"""
    for bucket in BucketManager.all_buckets():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in an s3 buckets"""
    for obj in BucketManager.all_objects(bucket):
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket_name')
def setup_bucket(bucket_name):
    """Create and configure S3 bucket"""
    bucket = BucketManager.init_bucket(bucket_name, session)
    #Set bucket policy to be readable by everyone
    BucketManager.set_policy(bucket)
    #Configure website
    BucketManager.configure_website(bucket)
    return

@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket_name')
def sync(pathname, bucket_name):
    """Sync contents of PATHNAME to BUCKET"""
    BucketManager.sync(pathname, bucket_name)
    webbrowser.open(BucketManager.get_bucket_url(BucketManager.s3.Bucket(bucket_name)))

if __name__ == '__main__':
    cli()