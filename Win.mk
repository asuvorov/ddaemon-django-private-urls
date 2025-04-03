SHELL := /bin/bash
INIT := python -m venv .env
ENV := $(ENVDIR)/Scripts
ACTIVATE := . $(ENV)/activate
UPIP := $(ENV)/python.exe -m pip install --upgrade pip
