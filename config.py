# config.py

# Operacional + DW em Postgres
# - certifique-se de que o DB 'varejo' existe
# - ajuste porta se for diferente de 5432
PG_URI    = "postgresql+psycopg2://postgres:root@localhost:5432/varejo"

# MongoDB para dados não-estruturados
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB  = "VarejoNoSQL"