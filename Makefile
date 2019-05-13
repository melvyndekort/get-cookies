build:
	sam build

invoke: build
	sam local invoke ConvertJWT --event event.json

gateway: build
	sam local start-api

package: build
	sam package
