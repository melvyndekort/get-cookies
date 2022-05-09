.PHONY := decrypt encrypt

ifndef AWS_SESSION_TOKEN
  $(error Not logged in, please run 'awsume')
endif

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
