.PHONY := clean decrypt encrypt build deploy
.DEFAULT_GOAL := build

ifndef AWS_SESSION_TOKEN
  $(error Not logged in, please run 'awsume')
endif

clean:
	@rm -rf \
	terraform/.terraform \
	terraform/.terraform.lock.hcl \
	terraform/lambda.zip \
	terraform/secrets.yaml

decrypt:
	@aws kms decrypt \
		--ciphertext-blob $$(cat terraform/secrets.yaml.encrypted) \
		--output text \
		--query Plaintext \
		--encryption-context target=convert-jwt | base64 -d > terraform/secrets.yaml

encrypt:
	@aws kms encrypt \
		--key-id alias/generic \
		--plaintext fileb://terraform/secrets.yaml \
		--encryption-context target=convert-jwt \
		--output text \
		--query CiphertextBlob > terraform/secrets.yaml.encrypted

build:
	@IMAGE_ID=$$(docker buildx build -q src); \
	CONTAINER_ID=$$(docker container create $$IMAGE_ID); \
	docker container cp $$CONTAINER_ID:/tmp/lambda.zip terraform/lambda.zip; \
	docker container rm $$CONTAINER_ID; \
	docker image rm $$IMAGE_ID

deploy: build
	@cd terraform; terraform init; terraform apply
