#!/bin/bash

PROJECT_ROOT=$(pwd)
export GOOGLE_APPLICATION_CREDENTIAL="${PROJECT_ROOT}/credentials/iitp-class-team-4-4fb491fb905a.json"

cd "${PROJECT_ROOT}"

python main.py
