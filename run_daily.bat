@echo off
set SERVERCHAN_KEY=SCT364214Tj8zj8ZrbAVCj3O8lgywlRKeb
cd /d C:\Users\Administrator\stock-mini-app
echo === Daily Report ===
python daily_report.py
echo === Monitors ===
python monitors\run_all.py
echo === All Done ===
