BUILD_PATH = stacks/degrades-reporting/terraform/lambda/build
DEGRADES_LAMBDA_PATH = lambda/degrades-reporting

degrades-env:
	cd $(DEGRADES_LAMBDA_PATH) && rm -rf lambdas/venv || true
	cd $(DEGRADES_LAMBDA_PATH) && python3.12 -m venv ./venv
	cd $(DEGRADES_LAMBDA_PATH) && ./venv/bin/pip3 install --upgrade pip
	cd $(DEGRADES_LAMBDA_PATH) && ./venv/bin/pip3 install -r requirements.txt --no-cache-dir
	cd $(DEGRADES_LAMBDA_PATH) && ./venv/bin/pip3 install -r requirements_local.txt --no-cache-dir

#degrades-github-env:
#	cd $(DEGRADES_LAMBDA_PATH) && rm -rf lambdas/venv || true
#	cd $(DEGRADES_LAMBDA_PATH) && python3.12 -m venv ./venv
#	cd $(DEGRADES_LAMBDA_PATH) && ./venv/bin/pip3 install --upgrade pip
#	cd $(DEGRADES_LAMBDA_PATH) && ./venv/bin/pip3 install -r requirements.txt --no-cache-dir


test-degrades:
	cd $(DEGRADES_LAMBDA_PATH) && rm -rf tmp/reports || true
	cd $(DEGRADES_LAMBDA_PATH) && mkdir -p tmp/reports
	cd $(DEGRADES_LAMBDA_PATH)  && venv/bin/python3 -m pytest tests/

test-degrades-coverage:
	cd $(DEGRADES_LAMBDA_PATH) && rm -rf tmp || true
	cd $(DEGRADES_LAMBDA_PATH) && mkdir -p tmp
	cd $(DEGRADES_LAMBDA_PATH) && ./venv/bin/coverage run -m pytest tests/
	cd $(DEGRADES_LAMBDA_PATH) && ./venv/bin/coverage report -m


zip-degrades-local: zip-lambda-layer
	cd $(DEGRADES_LAMBDA_PATH) && rm -rf ../../$(BUILD_PATH)/degrades-message-receiver || true
	cd $(DEGRADES_LAMBDA_PATH) && rm -rf ../../$(BUILD_PATH)/degrades-daily-summary || true


	cd $(DEGRADES_LAMBDA_PATH) && mkdir -p ../../$(BUILD_PATH)/degrades-message-receiver
	cd $(DEGRADES_LAMBDA_PATH) && mkdir -p ../../$(BUILD_PATH)/degrades-daily-summary


	cd $(DEGRADES_LAMBDA_PATH) && ./venv/bin/pip3 install --platform manylinux2014_x86_64\
 	--only-binary=:all: --implementation cp --python-version 3.12 -r requirements.txt -t ../../$(BUILD_PATH)/degrades-daily-summary

	cd $(DEGRADES_LAMBDA_PATH) && ./venv/bin/pip3 install --platform manylinux2014_x86_64\
 	--only-binary=:all: --implementation cp --python-version 3.12 -r requirements.txt -t ../../$(BUILD_PATH)/degrades-message-receiver


	cp ./$(DEGRADES_LAMBDA_PATH)/degrades_daily_summary/main.py $(BUILD_PATH)/degrades-daily-summary
	cp ./$(DEGRADES_LAMBDA_PATH)/degrades_message_receiver/main.py $(BUILD_PATH)/degrades-message-receiver

	cp -r $(DEGRADES_LAMBDA_PATH)/utils $(BUILD_PATH)/degrades-daily-summary/utils
	cp -r $(DEGRADES_LAMBDA_PATH)/utils $(BUILD_PATH)/degrades-message-receiver/utils

	cp -r $(DEGRADES_LAMBDA_PATH)/models $(BUILD_PATH)/degrades-daily-summary/models
	cp -r $(DEGRADES_LAMBDA_PATH)/models $(BUILD_PATH)/degrades-message-receiver/models

	cd $(BUILD_PATH)/degrades-message-receiver && zip -r -X ../degrades-message-receiver.zip .
	cd $(BUILD_PATH)/degrades-daily-summary && zip -r -X ../degrades-daily-summary.zip .


deploy-local:  zip-degrades-local
	ACTIVATE_PRO=0 localstack start -d
	$(DEGRADES_LAMBDA_PATH)/venv/bin/awslocal s3 mb s3://terraform-state
	cd stacks/degrades-dashboards/terraform && ../../../$(DEGRADES_LAMBDA_PATH)/venv/bin/tflocal init
	cd stacks/degrades-dashboards/terraform && ../../../$(DEGRADES_LAMBDA_PATH)/venv/bin/tflocal plan
	cd stacks/degrades-dashboards/terraform && ../../../$(DEGRADES_LAMBDA_PATH)/venv/bin/tflocal apply --auto-approve

zip-lambda-layer:
	cd $(DEGRADES_LAMBDA_PATH) && rm -rf ../../$(BUILD_PATH) || true
	cd $(DEGRADES_LAMBDA_PATH) && mkdir -p ../../$(BUILD_PATH)/layers
	cd $(DEGRADES_LAMBDA_PATH) && ./venv/bin/pip3 install \
		--platform manylinux2014_x86_64 --only-binary=:all: --implementation cp --python-version 3.12 -r requirements.txt -t ../../$(BUILD_PATH)/layers/python/lib/python3.12/site-packages
	cd $(BUILD_PATH)/layers && zip -r -X ../degrades-lambda-layer.zip .

zip-degrades-lambdas: zip-lambda-layer
	cd $(DEGRADES_LAMBDA_PATH) && rm -rf ../../$(BUILD_PATH)/degrades-message-receiver || true
	cd $(DEGRADES_LAMBDA_PATH) && rm -rf ../../$(BUILD_PATH)/degrades-daily-summary || true

	cd $(DEGRADES_LAMBDA_PATH) && mkdir -p ../../$(BUILD_PATH)/degrades-message-receiver
	cd $(DEGRADES_LAMBDA_PATH) && mkdir -p ../../$(BUILD_PATH)/degrades-daily-summary

	cp ./$(DEGRADES_LAMBDA_PATH)/degrades_message_receiver/main.py $(BUILD_PATH)/degrades-message-receiver
	cp ./$(DEGRADES_LAMBDA_PATH)/degrades_daily_summary/main.py $(BUILD_PATH)/degrades-daily-summary

	cp -r $(DEGRADES_LAMBDA_PATH)/utils $(BUILD_PATH)/degrades-message-receiver/utils
	cp -r $(DEGRADES_LAMBDA_PATH)/utils $(BUILD_PATH)/degrades-daily-summary/utils


	cp -r $(DEGRADES_LAMBDA_PATH)/models $(BUILD_PATH)/degrades-message-receiver/models
	cp -r $(DEGRADES_LAMBDA_PATH)/models $(BUILD_PATH)/degrades-daily-summary/models


	cd $(BUILD_PATH)/degrades-message-receiver && zip -r -X ../degrades-message-receiver.zip .
	cd $(BUILD_PATH)/degrades-daily-summary && zip -r -X ../degrades-daily-summary.zip .



