#!/usr/bin/env sh

pwd

ls -lah

python -m debugpy --listen 0.0.0.0:5678 -m src.main
