import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
_tmp=TemporaryDirectory()
os.environ['DATABASE_URL']='sqlite:///'+_tmp.name+'/test.db'
os.environ['API_TOKEN']='token-teste-nao-producao'
from main import app
from database import Base, engine
@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as c:
        c.headers['Authorization']='Bearer '+os.environ['API_TOKEN']
        yield c
