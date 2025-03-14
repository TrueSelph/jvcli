#!/bin/bash
# Script to serve jivas app

# Export env vars
set -o allexport; source .env; set +o allexport
# serve jivas app
jac jvserve main.jac