`docker image build --tag yale-celi-api-companies-post:0.1 .`

# Update Airtable extended table

#### Step \_. Update Airtable extended table

1. Copy Airtable data

   - Open Developer Console (if using Google Chrome) in the "Network" tab
   - Go to `https://airtable.com/shri4fzaMzXrQ3ZHp/tbloSNFhgc3BjkuC8`
   - Find `readSharedViewData` response (response to `https://airtable.com/v0.3/view/viw{someId}/readSharedViewData`).
   - In "Preview" tab copy value of the `data` variable
   - Save the copied value to `extended-table.json`

# Testing locally

`docker container run --publish 9000:8080 yale-celi-api-companies-post:0.1`
`curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}' && echo`

# TODO

- Serve `extended-table.json` from S3 or similar service (something that would make updating Airtable data easy).
