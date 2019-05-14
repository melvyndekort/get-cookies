# Convert JWT

A serverless authentication solution which converts Auth0 JWT tokens to AWS Cloudfront signed cookies

## Installation

Use the AWS Serverless Application Model [sam](https://aws.amazon.com/serverless/sam/) to build, test and deploy Convert JWT.

```bash
make gateway # run a local execution environment
```

## Makefile targets

```Makefile
build:
	sam build

invoke: build
	sam local invoke ConvertJWT --event event.json

gateway: build
	sam local start-api

package: build
	sam package
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
