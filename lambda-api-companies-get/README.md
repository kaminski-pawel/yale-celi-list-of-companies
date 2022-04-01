# Lambda function to get companies data from DynamoDB table

The Lambda function fetches data from DynamoDB table.

## Set up

### Step 1. Create IAM permissions

1. Create IAM role

   - For "Trusted entity type", choose "AWS Service"
   - For "Use case", choose "Lambda"

2. Create IAM policy

I tested with the following IAM policy attached to the IAM role.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "dynamodb:BatchGetItem",
        "dynamodb:GetItem",
        "dynamodb:Scan",
        "dynamodb:Query"
      ],
      "Resource": "${dynamodb-table-arn}"
    }
  ]
}
```

### Step 2. Create a Lambda function

1. In "Lambda"/"Functions" select "Create function"
2. In "Create function":

   - Select "Author from scratch"
   - for "Runtime" choose latest "Node"
   - attach new role

3. Choose Create function
4. Replace `index.js` in the console's code editor, and replace its contents with the code from `app.js` in this repo

### Step 3. Create an HTTP API

1. In "API Gateway" click on "Create API", and then choose "Build" under "HTTP API"
2. For "Configure routes", choose "Next" to skip route creation. You'll create routes later
3. Review the stage that API Gateway creates for you, and then choose "Next"
4. Click "Create"

### Step 4. Create routes

We are going to create 2 routes:

- `GET /companies/{slug}`
- `GET /companies`

To create routes:

1. Select the newly created API in the "API Gateway" panel and go to "Routes"
2. Click "Create"
3. Choose "GET" and `/companies/{slug}` and hit "Create"
4. Click "Create" again to create next route
5. Choose "GET" and `/companies` and hit "Create"

For more information, see the [documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-dynamo-db.html).
