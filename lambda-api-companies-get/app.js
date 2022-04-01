const AWS = require("aws-sdk");
const dynamo = new AWS.DynamoDB.DocumentClient();
const tableName = "YaleSonnenfeldList";

exports.handler = async (event, context) => {
  let body;
  let statusCode = 200;
  const headers = {
    "Content-Type": "application/json",
  };

  try {
    switch (event.routeKey) {
      case "GET /companies/{slug}":
        body = await dynamo
          .get({
            TableName: tableName,
            Key: {
              slug: event.pathParameters.slug,
            },
          })
          .promise();
        break;
      case "GET /companies":
        body = await dynamo.scan({ TableName: tableName }).promise();
        break;
      default:
        throw new Error(`Unsupported route: "${event.routeKey}"`);
    }
  } catch (err) {
    statusCode = 400;
    body = err.message;
  } finally {
    body = JSON.stringify(body);
  }

  return {
    statusCode,
    body,
    headers,
  };
};
