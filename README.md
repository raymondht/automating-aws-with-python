# automating-aws-with-python

## 01-Webotron
Webotron is a script that will sync a local directory to an s3 bucket, 
and optionally configure Route 53 and Cloudfront as well.

### Features:

Webotron is currently having these features:
- List bucket
- List objects of a given bucket
- Create and set up bucket
- Sync directory tree to bucket
- Set AWS profile with --profile=<profileName>
- Delete bucket
- Configure route 53 domain
- Set up and configure CDN with the certificate created by AWS Certificate Manager