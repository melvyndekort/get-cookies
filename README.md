# GET-COOKIES

get-cookies is a serverless authentication solution which converts a JWT token to AWS Cloudfront signed cookies

## Installation

It is possible to build and deploy stuff locally, but it's also fully automated through Github Actions.
If you still have a desire to do stuff locally use the following Makefile targets:

```Makefile
clean:   clean all temporary files
build:   build the lambda zip
decrypt: decrypt the KMS encrypted secrets
encrypt: encrypt the secrets with KMS
deploy:  run the build target and then run terraform apply
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
