# restify-db
Expose DB as REST APIs

## APIs
### GET /tables 
List all the tables present in the database

### GET /tables/{table_name}
   Get all the rows from a table. This API is paginated.
#### Query Parameters
- maxRows => maximum number of rows to return per page
- pageNo => page no of the paginated response
  
Other than the above parameters the API supports dynamic query parameters in the following format
- The Parameter name should be in this format `<column_name>__<operator>`.
  Currently Supported Operators:
  - "eq" for "=="
  - "gt" for ">"
  - "lt" for "<"
  - "ge" for ">="
  - "le" for "<="

Eg. If a table named `members` contains a column `age` the following api gets first 100 members whose age is greater than 18    
```/tables/members?maxRows=100&pageNo=1&age__gt=18 ```

### POST /tables/{table_name}
Insert a row into the table
- The row should be sent in the request body.

If the table `members` has columns id, name, age, phone_no, the request body should be as shown below:
```json
{
  "id": 123123,
  "age": 25,
  "name": "member1",
  "phone_no": "9453291811"
}
```
### PUT /tables/{table_name}
Update the rows of the table
- The values to be updated should be sent in the request body. It updates only the columns sent leaving other columns unmodified. Behaves like a PATCH request even though it is PUT
- The filter query is sent in the URL as parameters similar to `GET /tables/{table_name}`
- The columns to be updated should be sent in the request body

If the table `members` has columns id, name, age, phone_no, type and members whose age is greater than 25 should be updated with type 2 then
```
PUT /tables/members?age__gt=25

Body:
{
  "type": 2
}
```

### Future plans
1. Add Authentication
2. Add RBAC to the service 
3. Configurable Access to data (particular set of data)