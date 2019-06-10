from setuptools import setup

setup(
    name='webotron',
    version='0.1',
    author='Erayus',
    author_email='raymondhieutran@gmail.com',
    description='Webotron is a tool to deploy static websites to AWS.',
    license='GPLv3+',
    packages=['webotron'],
    url='https://github.com/Erayus/automating-aws-with-python',
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        webotron=webotron.webotron:cli
    '''
)