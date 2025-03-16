#!/bin/bash
pip install -r requirements.pysqlite3.txt
uvicorn app.main:app --host=0.0.0.0 --port=8000 