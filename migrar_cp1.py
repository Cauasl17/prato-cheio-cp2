"""Copia SQLite CP1 para novo arquivo CP2 sem alterar a origem."""
import sys
from pathlib import Path
import sqlite3
from sqlalchemy import create_engine
import models
from database import Base
if len(sys.argv)!=3:
    raise SystemExit("Uso: python migrar_cp1.py origem.db destino.db")
origem,destino=map(Path,sys.argv[1:])
if not origem.is_file() or destino.exists():
    raise SystemExit("Origem deve existir e destino deve ser novo.")
novo=create_engine("sqlite:///"+str(destino.resolve()))
Base.metadata.create_all(novo)
try:
    with sqlite3.connect(destino) as db:
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("ATTACH DATABASE ? AS antigo",(str(origem.resolve()),))
        for tab in ["doadores","instituicoes","doacoes","reservas"]:
            campos=[r[1] for r in db.execute(f"PRAGMA main.table_info({tab})")]
            colunas=','.join(campos)
            db.execute(f"INSERT INTO main.{tab} ({colunas}) SELECT {colunas} FROM antigo.{tab}")
        erros=db.execute("SELECT d.id FROM doacoes d WHERE abs(d.quantidade_reservada - coalesce((SELECT sum(r.quantidade) FROM reservas r WHERE r.doacao_id=d.id AND r.status IN ('PENDENTE','COLETADA')),0))>0.000001").fetchall()
        if erros:raise ValueError(f"Saldos incoerentes nos lotes {erros}")
    print("Migração concluída. Origem preservada:",origem)
except Exception:
    novo.dispose()
    destino.unlink(missing_ok=True)
    raise
