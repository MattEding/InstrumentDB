# Gibson Instrument Database
Collection of all the guitar models hosted on Gibson's website.

## Extract:
- Selenium webscraper
    - logging functionality
- Store raw HTML
- Extract fields to JSON

## Transform:
- Clean extracted JSON files
    - fix data types
    - rename keys
- Reformulate data for PostgreSQL database

## Load _(TODO)_:
- Provide RESTful API

## Unit Testing:
- Webscraper
- JSON cleaner

## Terraform _(TODO)_:
- Automate entire ETL process
- Create EC2 instance to scrape
- Store scraped data in buckets
- RDS for PostgreSQL database
- Lambda Gateway, & S3 for serverless RESTful API
    - (https://aws.amazon.com/getting-started/projects/build-serverless-web-app-lambda-apigateway-s3-dynamodb-cognito/)