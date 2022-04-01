# Yale CELI list of companies

This project contains AWS Lambda functions to provide a standardized API to the [list of companies](https://som.yale.edu/story/2022/almost-500-companies-have-withdrawn-russia-some-remain) maintained by Jeffrey Sonnenfeld and his team of experts, research fellows, and students at the Yale Chief Executive Leadership Institute.

The Lambda functions include:

- `lambda-api-companies-post` - extracts and transforms data from the original Yale list, joins with supplementary data and writes to the DynamoDB table.
- `lambda-api-companies-get` - fetches data from the DynamoDB table.

See README.md in each lambda function for further guidance.

## General remarks about the database

- Before running lambda functions first create DynamoDB table. For Primary key, enter `slug`.
- The DynamoDB table has no ID other than `slug`. As a result:
  - A new DB entry overwrites an old one.
  - An edge case may arise with two entries having the same `slug`. In such case one will overwrite the other.
  - Old entries are not removed unless overwritten.

## Licence

This project is licensed under the terms of the MIT license.
