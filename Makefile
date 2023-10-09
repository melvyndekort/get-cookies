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
	terraform/secrets.yaml \
	src/.pytest_cache \
	src/*/__pycache__ \
	src/dist \
	src/package

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
	@cd src; \
	poetry install && \
	poetry run pytest && \
	poetry build && \
	poetry run pip install --upgrade --platform manylinux2014_x86_64 --only-binary=:all: -t package dist/*.whl && \
	cd package && \
  zip -r ../lambda.zip . -x '*.pyc' && \
	mv ../lambda.zip ../../terraform/lambda.zip

test:
	@cd src; poetry run pytest

deploy: build
	@cd terraform; terraform init; terraform apply
