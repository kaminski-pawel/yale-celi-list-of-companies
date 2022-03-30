# Build Docker image

`docker image build --tag yale-celi-api-companies-post:0.1 .`

# Update Airtable extended table

#### Step \_. Update Airtable extended table

1. Copy Airtable data

   - Open Developer Console (if using Google Chrome) in the "Network" tab
   - Go to `https://airtable.com/shri4fzaMzXrQ3ZHp/tbloSNFhgc3BjkuC8`
   - Find `readSharedViewData` response (response to `https://airtable.com/v0.3/view/viw{someId}/readSharedViewData`).
   - In "Preview" tab copy value of the `data` variable
   - Save the copied value to `extended-table.json`

<!-- #### Step \_. Create a Box application for API calls

1. Log in Box developer account

   - Create a [Box account](https://www.box.com/pricing/individual) (free individual account should be sufficient)
   - Log into the [Box Developer Console](https://developers.box.com)

2. Create New App

   - Go to "My Apps" and click on "Create New App"
   - Select "Custom App"
   - Select "Server Authentication with JWT, name the application and press "Create App"

3. Enable 2FA

   - Go to "Account Settings"
   - Set up 2-Step Verification

4. Generate a Public/Private Keypair

   - Go to app configuration ("My Apps"/[new-app]/"Configuration")
   - Click on "Generate a Public/Private Keypair" and save the JSON config file

5. Set application scope

   - In app configuration turn on all(?) "Content Actions", "Administrative Actions", "Developer Actions" and "Advanced Features"

6. Give the app admin authorization

   - Go to the admin console (from the dropdown in the top right corner), then to "Apps" (left sidebar), finally to the "Custom Apps Manager"
   - Click on the "App Settings" and turn on "Disable unpublished apps by default"
   - Click on the "Add App", enter "Client ID" of the new app and click "Authorize"
   - The new app should be added to the list of server authentication apps. Click on "..." button next to the new app and select "Enable App"
   - Later, while testing the Lambda function an 403 error ("Access denied - insufficient permission") may appear. One way of solving it might be broadening the scope of "Application scope" (see step above) and "Reauthorizing App" in "Custom Apps Manager" (in the same place as the "Enable App" option). -->

# Testing locally

`docker container run --publish 9000:8080 yale-celi-api-companies-post:0.1`
`curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}' && echo`

# TODO

- Serve `extended-table.json` from S3 or similar service (something that would make updating Airtable data easy).
