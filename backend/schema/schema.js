const express = require('express');
const { graphqlHTTP } = require('graphql-http');
const schema = require('./schema'); // Define your GraphQL schema
const app = express();

app.use('/graphql', graphqlHTTP({
  schema: schema,
  graphiql: true,
}));

app.listen(4000, () => {
  console.log('Server is running on port 4000..');
});
