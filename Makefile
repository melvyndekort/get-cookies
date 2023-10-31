.PHONY := clean decrypt encrypt install test build init validate deploy
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

install:
	@poetry install

test: install
	@poetry run pytest

build: test
	@poetry build
	@poetry run pip install --upgrade --platform manylinux2014_aarch64 --only-binary=":all:" -t package dist/*.whl
	@cd package && zip -r ../lambda.zip . -x '*.pyc'

init:
	@terraform -chdir=terraform init

validate: init
	@terraform -chdir=terraform validate

apply: validate
	@terraform -chdir=terraform apply -input=true -refresh=true
