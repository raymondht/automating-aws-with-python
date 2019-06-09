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
from domain import DomainManager
import util

session = None
bucket_manager = None
domain_manager = None


@click.group()
@click.option('--profile', default=None,
              help="Use a given AWS profile.")
def cli(profile):
    """Webotron deploys websites to AWS."""
    global session, bucket_manager, domain_manager      

    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile
    else:
        session_cfg['profile_name'] = "pythonAutomation"

    session = boto3.Session(**session_cfg)
    bucket_manager = BucketManager(session)
    domain_manager = DomainManager(session)

@cli.command('list-buckets')
def list_bucket():
    """List all s3 buckets"""
    for bucket in bucket_manager.all_buckets():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in an s3 buckets"""
    for obj in bucket_manager.all_objects(bucket):
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket_name')
def setup_bucket(bucket_name):
    """Create and configure S3 bucket"""
    bucket = bucket_manager.init_bucket(bucket_name)
    #Set bucket policy to be readable by everyone
    bucket_manager.set_policy(bucket)
    #Configure website
    bucket_manager.configure_website(bucket)
    return


@cli.command('delete-bucket')
@click.argument('bucket_name')
def delete_bucket(bucket_name):
    """Delete S3 bucket"""
    bucket_manager.delete_bucket(bucket_name)
    return


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket_name')
def sync(pathname, bucket_name):
    """Sync contents of PATHNAME to BUCKET"""
    bucket_manager.sync(pathname, bucket_name)
    webbrowser.open(bucket_manager.get_bucket_url(bucket_manager.s3.Bucket(bucket_name)))


@cli.command('setup-domain')
@click.argument('domain')
def setup_domain(domain):
    """Configure DOMAIN to point to BUCKET."""
    bucket = bucket_manager.get_bucket(domain)

    zone = domain_manager.find_hosted_zone(domain) \
        or domain_manager.create_hosted_zone(domain)

    endpoint = util.get_endpoint(bucket_manager.get_region_name(bucket))
    domain_manager.create_s3_domain_record(zone, domain, endpoint)
    print("Domain configure: http://{}".format(domain))

if __name__ == '__main__':
    cli()