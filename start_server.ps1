$env:PYTHONPATH = "F:\code\project DNA\backend"
Set-Location "F:\code\project DNA"
py -m uvicorn dna.api.app:app --host 0.0.0.0 --port 8000
