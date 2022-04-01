# Lambda function to write to DynamoDB table

The function fetches data from official YALE CELI list and from extended unofficial datasource. The data is joined and written to DynamoDB table. The Lambda function code and dependencies is stored and distributed as a Docker container image.

## Update Airtable extended table

### Step 1. Update Airtable extended table

1. Copy Airtable data

   - Open Developer Console (if using Google Chrome) in the "Network" tab
   - Go to `https://airtable.com/shri4fzaMzXrQ3ZHp/tbloSNFhgc3BjkuC8`
   - Find `readSharedViewData` response (response to `https://airtable.com/v0.3/view/viw${someId}/readSharedViewData`).
   - In "Preview" tab copy value of the `data` variable
   - Save the copied value to `extended-table.json`

## Deployment of Lambda function

### Step 2. Create IAM permissions

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
        "dynamodb:BatchGet*",
        "dynamodb:DescribeTable",
        "dynamodb:Get*",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWrite*",
        "dynamodb:Delete*",
        "dynamodb:Update*",
        "dynamodb:PutItem",
        "ecr:SetRepositoryPolicy",
        "ecr:GetRepositoryPolicy"
      ],
      "Resource": ["${arn-of-image-in-ECR}", "${arn-of-dynamodb-table}"]
    }
  ]
}
```

### Step 3. Build and deploy image

1. Authenticate the Docker CLI to your Amazon ECR registry

```bash
aws ecr get-login-password --region ${aws-region-name} | docker login --username AWS --password-stdin ${aws-account-id}.dkr.ecr.${aws-region-name}.amazonaws.com
```

2. Build your Docker image

```bash
docker build -t ${name-of-the-image} .
```

3. Create a repository in Amazon ECR using the create-repository command

```bash
aws ecr create-repository --region ${aws-region-name} --repository-name ${name-of-the-image} --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
```

4. Tag your image to match your repository name using the docker tag command

```bash
docker tag ${name-of-the-image}:${tag} ${aws-account-id}.dkr.ecr.${aws-region-name}.amazonaws.com/${name-of-the-image}:${tag}
```

5. Deploy the image to Amazon ECR using the docker push command

```bash
docker push ${aws-account-id}.dkr.ecr.${aws-region-name}.amazonaws.com/${name-of-the-image}:${tag}
```

### Step 4. Create a Lambda function

1. Open the "Functions" page of the Lambda console
2. Choose "Create function"
3. Choose the "Container image" option
4. Under Basic information, do the following:

- For "Container image URI", enter the URI of the Amazon ECR image that you created previously

5. Choose "Create function"
6. Change timeout to e.g. 10-15 seconds by editing "Configuration"/"General configuration"

For more information see the [documentation](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-images.html).

### Step 5. Add an event trigger

For example, the event trigger can be set up by the following steps:

1. Create a new rule in the "EventBridge" service panel
2. For "Rule type" select "Schedule"
3. Set the schedule pattern, for example rate expression `12` `Hours` for a `schedule that runs at a regular rate`
4. Select the Lambda function as a target
5. Create the new rule

### Updating

In order to update build, push to ECR and run update-function-code command:

```bash
aws lambda update-function-code --function-name ${lambda-function-arn} --image-uri ${image-uri} --region=${aws-region}
```

## TODO

- Serve `extended-table.json` from S3 or similar service (something that would make updating Airtable data easy).
