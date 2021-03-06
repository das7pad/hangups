##############################################################################
# General targets
##############################################################################

python = python3
venv = venv
pip = $(venv)/bin/pip

.PHONY: venv
venv:
	@if [ ! -d $(venv) ]; then \
		echo "Creating venv" && $(python) -m venv $(venv); fi

.PHONY: venv-deps
venv-deps: venv
	@echo "Upgrading requirements"
	$(pip) install --requirement requirements-dev.txt

.PHONY: test-all
test-all: style lint check test

.PHONY: style
style:
	@if [ ! -d $(venv)/lib/*/site-packages/pycodestyle*/ ]; then \
		make -s venv-deps; fi
	@echo "Stylecheck: started"
	$(venv)/bin/pycodestyle hangups
	@echo "Stylecheck: no errors found"

.PHONY: lint
lint:
	@if [ ! -d $(venv)/lib/*/site-packages/pylint/ ]; then \
		make -s venv-deps; fi
	@echo "Lint: started"
	$(venv)/bin/pylint -s no --reports=n hangups
	@echo "Lint: no errors found"

.PHONY: check
check: venv
	@if [ ! -d $(venv)/lib/*/site-packages/docutils/ ]; then \
		make -s venv-deps; fi
	@echo "Package check: started"
	$(venv)/bin/python setup.py check --metadata --restructuredtext --strict
	@echo "Package check: no errors found"

.PHONY: test
test:
	@if [ ! -d $(venv)/lib/*/site-packages/_pytest/ ]; then \
		make -s venv-deps; fi
	@echo "Tests: started"
	$(venv)/bin/pytest hangups
	@echo "Test: all completed"

# internal: check for `pip-compile` and ensure an existing cache directory
.PHONY: .gen-deps
.gen-deps: venv
		@if [ ! -d $(venv)/lib/*/site-packages/piptools ]; then \
			echo "Installing pip-tools" && $(pip) install pip-tools \
			echo "Done"; \
		fi

.PHONY: gen-deps
gen-deps: .gen-deps
	@echo "Generating requirements-dev.txt"
	@CUSTOM_COMPILE_COMMAND="make gen-deps" \
		$(venv)/bin/pip-compile \
			--upgrade \
			--no-index \
			--no-emit-trusted-host \
			--output-file requirements-dev.txt \
			requirements-dev.in
	@sed -i 's#-e file://$(PWD)#-e .#' requirements-dev.txt
	@echo "Done"

.PHONY: Jenkinsfile
Jenkinsfile:
	@$(python) tools/gen_Jenkinsfile.py

.PHONY: clean
clean:
	@echo "Remove venv and compiled python files"
	rm -rf $(venv) .cache `find . -name __pycache__`

##############################################################################
# Protocol buffer targets
##############################################################################

proto = hangups/hangouts.proto
proto_py = hangups/hangouts_pb2.py
proto_doc = docs/proto.rst
test_proto = hangups/test/test_pblite.proto
test_proto_py = hangups/test/test_pblite_pb2.py

.PHONY: protos
protos: $(proto_py) $(test_proto_py) $(proto_doc)

.PHONY: clean-protos
clean-protos:
	rm -f $(proto_py) $(proto_doc) $(test_proto_py)

$(proto_py): $(proto)
	protoc --python_out . $(proto)

$(test_proto_py): $(test_proto)
	protoc --python_out . $(test_proto)

$(proto_doc): $(proto)
	$(venv)/bin/python docs/generate_proto_docs.py $(proto) > $(proto_doc)
