CREATE TABLE doadores (
	id INTEGER NOT NULL, 
	cnpj VARCHAR(14) NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	tipo VARCHAR(20) NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	telefone VARCHAR(20) NOT NULL, 
	cidade VARCHAR(50) NOT NULL, 
	ativo BOOLEAN, 
	criado_em DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (cnpj)
);
CREATE INDEX ix_doadores_id ON doadores (id);
CREATE TABLE instituicoes (
	id INTEGER NOT NULL, 
	cnpj VARCHAR(14) NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	responsavel VARCHAR(100) NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	telefone VARCHAR(20) NOT NULL, 
	cidade VARCHAR(50) NOT NULL, 
	possui_refrigeracao BOOLEAN, 
	ativo BOOLEAN, 
	criado_em DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (cnpj)
);
CREATE INDEX ix_instituicoes_id ON instituicoes (id);
CREATE TABLE relatorios_ia (
	id INTEGER NOT NULL, 
	modelo VARCHAR(100) NOT NULL, 
	texto VARCHAR(8000) NOT NULL, 
	criado_em DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE doacoes (
	id INTEGER NOT NULL, 
	doador_id INTEGER NOT NULL, 
	descricao VARCHAR(200) NOT NULL, 
	categoria VARCHAR(20) NOT NULL, 
	tipo_armazenamento VARCHAR(20) NOT NULL, 
	unidade VARCHAR(10) NOT NULL, 
	quantidade_total FLOAT NOT NULL, 
	quantidade_reservada FLOAT, 
	data_validade DATE NOT NULL, 
	local_retirada VARCHAR(200) NOT NULL, 
	status VARCHAR(25), 
	criado_em DATETIME, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_total_positivo CHECK (quantidade_total > 0), 
	CONSTRAINT ck_saldo CHECK (quantidade_reservada >= 0 AND quantidade_reservada <= quantidade_total), 
	FOREIGN KEY(doador_id) REFERENCES doadores (id)
);
CREATE INDEX ix_doacao_busca ON doacoes (status, data_validade, categoria);
CREATE INDEX ix_doacao_doador ON doacoes (doador_id);
CREATE INDEX ix_doacoes_id ON doacoes (id);
CREATE TABLE reservas (
	id INTEGER NOT NULL, 
	doacao_id INTEGER NOT NULL, 
	instituicao_id INTEGER NOT NULL, 
	quantidade FLOAT NOT NULL, 
	status VARCHAR(15), 
	observacoes VARCHAR(500), 
	criado_em DATETIME, 
	coletado_em DATETIME, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_reserva_positiva CHECK (quantidade > 0), 
	FOREIGN KEY(doacao_id) REFERENCES doacoes (id), 
	FOREIGN KEY(instituicao_id) REFERENCES instituicoes (id)
);
CREATE INDEX ix_reserva_doacao ON reservas (doacao_id);
CREATE INDEX ix_reserva_instituicao_status ON reservas (instituicao_id, status);
CREATE INDEX ix_reservas_id ON reservas (id);