#!make
KUSTOMIZE_VERSION := $(shell test -e /usr/local/bin/kustomize && /usr/local/bin/kustomize version | cut -f2 -d/ | cut -f1 -d' ')
KUBEVAL_VERSION := $(shell test -e /usr/local/bin/kubeval && /usr/local/bin/kubeval --version | grep Version | cut -f2 -d' ')

shell:
	pipenv shell

# Manifest Validators
validate_manifest:
	rm -f .manifest
	kustomize build .deploy/ >> .manifest
	[ -s .manifest ] || (echo "Manifest is Empty" ; exit 2)
	kubeval .manifest --kubernetes-version 1.18.0 --ignore-missing-schemas
	echo "Manifest Validated"
	rm -rf .manifest

validate_manifest_if_changed:
	if test -n "$(shell git ls-files -m .deploy/)"; \
		then make validate_manifest; \
		else echo deploy/ files unchanged; \
	fi

install_validate_manifest:
ifneq ($(KUSTOMIZE_VERSION), v3.8.1)
	curl -o kustomize.tar.gz --location https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize/v3.8.1/kustomize_v3.8.1_linux_amd64.tar.gz
	tar -xzvf kustomize.tar.gz kustomize
	chmod u+x kustomize
	sudo mv kustomize /usr/local/bin/
	rm kustomize.tar.gz
endif
ifneq ($(KUBEVAL_VERSION), 0.15.0)
	wget -O kubeval-linux-amd64.tar.gz https://github.com/instrumenta/kubeval/releases/latest/download/kubeval-linux-amd64.tar.gz
	tar xf kubeval-linux-amd64.tar.gz kubeval
	chmod u+x kubeval
	sudo mv kubeval /usr/local/bin/
	rm kubeval-linux-amd64.tar.gz
endif