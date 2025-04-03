SHELL := /bin/bash
INIT := virtualenv .env
ENV := $(ENVDIR)/bin
ACTIVATE := . $(ENV)/activate
UPIP := $(ENV)/pip install -U  pip

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S), Linux)
	# Do something
endif
ifeq ($(UNAME_S), Darwin)
	# Do something
endif
