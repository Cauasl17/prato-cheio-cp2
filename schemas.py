"""Schemas do Pydantic: definem o formato dos dados que entram e saem da API."""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator


class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)
    @model_validator(mode="before")
    @classmethod
    def rejeitar_nulos(cls, dados):
        if isinstance(dados, dict):
            for campo, valor in dados.items():
                if valor is None and campo != "observacoes":
                    raise ValueError(f"{campo} não aceita null. Omita o campo para mantê-lo.")
        return dados

# --------------------------------------------------
# Listas de valores aceitos
# --------------------------------------------------

class TipoDoador(str, Enum):
    RESTAURANTE = "RESTAURANTE"
    MERCADO = "MERCADO"
    PADARIA = "PADARIA"
    HORTIFRUTI = "HORTIFRUTI"
    OUTRO = "OUTRO"


class Categoria(str, Enum):
    HORTIFRUTI = "HORTIFRUTI"
    PANIFICACAO = "PANIFICACAO"
    LATICINIOS = "LATICINIOS"
    NAO_PERECIVEL = "NAO_PERECIVEL"
    PRONTO_CONSUMO = "PRONTO_CONSUMO"
    OUTROS = "OUTROS"


class TipoArmazenamento(str, Enum):
    AMBIENTE = "AMBIENTE"
    REFRIGERADO = "REFRIGERADO"
    CONGELADO = "CONGELADO"


class Unidade(str, Enum):
    KG = "KG"
    LITRO = "LITRO"
    UNIDADE = "UNIDADE"
    PORCAO = "PORCAO"


# --------------------------------------------------
# Doador
# --------------------------------------------------

class DoadorCriar(Entrada):
    cnpj: str = Field(min_length=1, max_length=20)
    nome: str = Field(min_length=1, max_length=100)
    tipo: TipoDoador
    email: EmailStr
    telefone: str = Field(min_length=1, max_length=20)
    cidade: str = Field(min_length=1, max_length=50)


class DoadorAtualizar(Entrada):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    tipo: TipoDoador | None = None
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, min_length=1, max_length=20)
    cidade: str | None = Field(default=None, min_length=1, max_length=50)
    ativo: bool | None = None


class DoadorResposta(BaseModel):
    id: int
    cnpj: str = Field(min_length=1, max_length=20)
    nome: str = Field(min_length=1, max_length=100)
    tipo: str
    email: EmailStr
    telefone: str = Field(min_length=1, max_length=20)
    cidade: str = Field(min_length=1, max_length=50)
    ativo: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ListaDoadores(BaseModel):
    total: int
    pagina: int
    itens: list[DoadorResposta]


# --------------------------------------------------
# Instituicao
# --------------------------------------------------

class InstituicaoCriar(Entrada):
    cnpj: str = Field(min_length=1, max_length=20)
    nome: str = Field(min_length=1, max_length=100)
    responsavel: str = Field(min_length=1, max_length=100)
    email: EmailStr
    telefone: str = Field(min_length=1, max_length=20)
    cidade: str = Field(min_length=1, max_length=50)
    possui_refrigeracao: bool = False


class InstituicaoAtualizar(Entrada):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    responsavel: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, min_length=1, max_length=20)
    cidade: str | None = Field(default=None, min_length=1, max_length=50)
    possui_refrigeracao: bool | None = None
    ativo: bool | None = None


class InstituicaoResposta(BaseModel):
    id: int
    cnpj: str = Field(min_length=1, max_length=20)
    nome: str = Field(min_length=1, max_length=100)
    responsavel: str = Field(min_length=1, max_length=100)
    email: EmailStr
    telefone: str = Field(min_length=1, max_length=20)
    cidade: str = Field(min_length=1, max_length=50)
    possui_refrigeracao: bool
    ativo: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ListaInstituicoes(BaseModel):
    total: int
    pagina: int
    itens: list[InstituicaoResposta]


# --------------------------------------------------
# Doacao
# --------------------------------------------------

class DoacaoCriar(Entrada):
    doador_id: int = Field(gt=0)
    descricao: str = Field(min_length=1, max_length=200)
    categoria: Categoria
    tipo_armazenamento: TipoArmazenamento
    unidade: Unidade
    quantidade_total: float = Field(gt=0, allow_inf_nan=False)
    data_validade: date
    local_retirada: str = Field(min_length=1, max_length=200)


class DoacaoAtualizar(Entrada):
    descricao: str | None = Field(default=None, min_length=1, max_length=200)
    categoria: Categoria | None = None
    quantidade_total: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    data_validade: date | None = None
    local_retirada: str | None = Field(default=None, min_length=1, max_length=200)


class DoacaoResposta(BaseModel):
    id: int
    doador_id: int = Field(gt=0)
    descricao: str = Field(min_length=1, max_length=200)
    categoria: str
    tipo_armazenamento: str
    unidade: str
    quantidade_total: float = Field(gt=0, allow_inf_nan=False)
    quantidade_reservada: float
    data_validade: date
    local_retirada: str = Field(min_length=1, max_length=200)
    status: str
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ListaDoacoes(BaseModel):
    total: int
    pagina: int
    itens: list[DoacaoResposta]


# --------------------------------------------------
# Reserva
# --------------------------------------------------

class ReservaCriar(Entrada):
    doacao_id: int = Field(gt=0)
    instituicao_id: int = Field(gt=0)
    quantidade: float = Field(gt=0, allow_inf_nan=False)
    observacoes: str | None = Field(default=None, max_length=500)


class ReservaResposta(BaseModel):
    id: int
    doacao_id: int = Field(gt=0)
    instituicao_id: int = Field(gt=0)
    quantidade: float = Field(gt=0, allow_inf_nan=False)
    status: str
    observacoes: str | None
    criado_em: datetime
    coletado_em: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ListaReservas(BaseModel):
    total: int
    pagina: int
    itens: list[ReservaResposta]
