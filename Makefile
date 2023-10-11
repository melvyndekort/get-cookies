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
	lambda.zip \
	.pytest_cache \
	*/__pycache__ \
	dist \
	package

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
	@poetry install && \
	poetry run pytest && \
	poetry build && \
	poetry run pip install --upgrade --platform manylinux2014_x86_64 --only-binary=:all: -t package dist/*.whl && \
	cd package && zip -r ../lambda.zip . -x '*.pyc'

test:
	@poetry run pytest

init:
	@cp lambda.zip terraform/lambda.zip && \
	terraform -chdir=terraform init

validate: init
	@terraform -chdir=terraform validate

deploy: validate
	@terraform -chdir=terraform apply -input=true -refresh=true
