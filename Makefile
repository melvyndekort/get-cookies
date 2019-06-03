build:
	sam build

invoke: build
	sam local invoke ConvertJWTFunction --event event.json

gateway: build
	sam local start-api

package: build
	rm -f .aws-sam/packaged.yaml
	sam package --s3-bucket mdekort-auth --output-template-file .aws-sam/packaged.yaml

deploy: package
	sam deploy --template-file .aws-sam/packaged.yaml --stack-name auth --capabilities CAPABILITY_NAMED_IAM
