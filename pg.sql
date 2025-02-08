-- Criação do banco de dados
DO
$$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'ebenezer') THEN
        CREATE DATABASE ebenezer;
    END IF;
END
$$;

-- Conectar ao banco de dados 'ebenezer'
\c ebenezer;

-- Tabela companies
DROP TABLE IF EXISTS companies;
CREATE TABLE companies (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(255) DEFAULT NULL,
  cnpj VARCHAR(14) DEFAULT NULL,           -- CNPJ com 14 caracteres, sem pontos ou traços
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserção de exemplo na tabela companies
INSERT INTO companies (name, cnpj) VALUES ('Empresa Padrão', '12345678000195');

-- Tabela roles
DROP TABLE IF EXISTS roles;
CREATE TABLE roles (
  id BIGSERIAL PRIMARY KEY,
  company_id BIGINT NOT NULL,
  active BOOLEAN DEFAULT TRUE,
  description VARCHAR(255) DEFAULT NULL,
  role VARCHAR(255) DEFAULT NULL,
  FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Inserção de exemplo na tabela roles
INSERT INTO roles (company_id, active, description, role) VALUES (1, TRUE, 'Administrador', 'ADMIN');
INSERT INTO roles (company_id, active, description, role) VALUES (1, TRUE, 'Padrão', 'PADRAO');

-- Tabela users
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    role_id BIGINT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    photo BYTEA,
    user_creator_id BIGINT,          -- Usuário que criou o registro
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_creator_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Tabela funcionarios
DROP TABLE IF EXISTS employees;
CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT NOT NULL,               -- Empresa associada
    name VARCHAR(255) NOT NULL,               -- Nome do funcionário
    date_of_birth DATE,                       -- Data de nascimento
    hire_date DATE,                           -- Data de contratação
    termination_date DATE,                    -- Data de desligamento (se houver)
    ctps VARCHAR(100),                        -- CNPJ do funcionário (se aplicável)
    cnpj VARCHAR(14) UNIQUE,                  -- CNPJ do funcionário (se aplicável)
    cpf VARCHAR(11) UNIQUE,                   -- CPF do funcionário
    rg VARCHAR(30),                           -- RG do funcionário
    rg_issuer VARCHAR(30),                    -- Órgão emissor do RG
    position VARCHAR(100),                    -- Cargo do funcionário
    department VARCHAR(100),                  -- Departamento do funcionário
    salary NUMERIC(15, 2),                    -- Salário do funcionário
    active BOOLEAN DEFAULT TRUE,              -- Status do funcionário (ativo/inativo)
    marital_status VARCHAR(255),
    wife_name VARCHAR(255),
    wife_date_of_birth DATE,
    user_creator_id BIGINT NOT NULL,          -- Usuário que criou o registro
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Data de criação
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,                -- Soft delete

    -- Foreign Keys
    FOREIGN KEY (user_creator_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);


-- Tabela donor_contacts
DROP TABLE IF EXISTS employee_contacts;
CREATE TABLE employee_contacts (
    id BIGSERIAL PRIMARY KEY,
    employee_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(60) NOT NULL,
    email VARCHAR(60),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    UNIQUE (employee_id, phone, email)  -- Restrição de unicidade para evitar duplicidade de contatos para o mesmo func
);

-- Tabela donor_addresses
DROP TABLE IF EXISTS employee_addresses;
CREATE TABLE employee_addresses (
    id BIGSERIAL PRIMARY KEY,
    employee_id BIGINT NOT NULL,
    street VARCHAR(255) NOT NULL,
    neighborhood VARCHAR(255),
    complement VARCHAR(255),
    city VARCHAR(255) NOT NULL,
    state VARCHAR(2) NOT NULL,               -- Estado com 2 caracteres (UF)
    postal_code VARCHAR(20),                  -- CEP com 8 caracteres
    number VARCHAR(100) NOT NULL,
    country VARCHAR(60) DEFAULT 'Brazil',
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    UNIQUE (employee_id)  -- Adiciona a restrição de unicidade para donor_id
);

-- Inserção de exemplo na tabela users
INSERT INTO users (company_id, username, password, email, role_id, active) VALUES 
(1, 'admin', '$2a$10$St2AvRkC5G9g1R9HmNRTyuCkKyL8051CR2FGkBmpDOJaBznH7xnVK', 'admin@admin.com', 1, TRUE);


DROP TABLE IF EXISTS employee_users;
CREATE TABLE employees_users (
    employee_id BIGINT NOT NULL,            -- Relacionamento com a tabela employees
    user_id BIGINT NOT NULL,                -- Relacionamento com a tabela users
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (employee_id, user_id),     -- Chave primária composta para garantir unicidade
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabela donors
DROP TABLE IF EXISTS donors;
CREATE TABLE donors (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT NOT NULL,
    person_type VARCHAR(20) NOT NULL CHECK (person_type IN ('Pessoa Física', 'Pessoa Jurídica')),
    name VARCHAR(255) NOT NULL,
    cnpj VARCHAR(30),                       -- CNPJ com 14 caracteres
    ie VARCHAR(30),
    cpf VARCHAR(30) ,                        -- CPF com 11 caracteres
    rg VARCHAR(30),
    rg_issuer VARCHAR(30),
    active BOOLEAN DEFAULT TRUE,
    user_creator_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_creator_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    -- Restrição única para (cpf, person_type)
    CONSTRAINT unique_cpf_person_type UNIQUE (cpf, person_type),
    
    -- Restrição única para (cnpj, person_type)
    CONSTRAINT unique_cnpj_person_type UNIQUE (cnpj, person_type)
);

-- Tabela donor_contacts
DROP TABLE IF EXISTS donor_contacts;
CREATE TABLE donor_contacts (
    id BIGSERIAL PRIMARY KEY,
    donor_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(60) NOT NULL,
    email VARCHAR(60),
    FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE CASCADE,
    UNIQUE (donor_id, phone, email)  -- Restrição de unicidade para evitar duplicidade de contatos para o mesmo doador
);

-- Tabela donor_addresses
DROP TABLE IF EXISTS donor_addresses;
CREATE TABLE donor_addresses (
    id BIGSERIAL PRIMARY KEY,
    donor_id BIGINT NOT NULL,
    street VARCHAR(255) NOT NULL,
    neighborhood VARCHAR(255),
    complement VARCHAR(255),
    city VARCHAR(255) NOT NULL,
    state VARCHAR(2) NOT NULL,               -- Estado com 2 caracteres (UF)
    postal_code VARCHAR(20),                  -- CEP com 8 caracteres
    number VARCHAR(100) NOT NULL,
    country VARCHAR(60) DEFAULT 'Brazil',
    FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE CASCADE,
    UNIQUE (donor_id)  -- Adiciona a restrição de unicidade para donor_id
);

DROP TABLE IF EXISTS appointments;
CREATE TABLE appointments (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT NOT NULL,
    user_creator_id BIGINT NOT NULL,
    date TIMESTAMP,
    time VARCHAR(20),
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('Ligação')),
    notes VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_creator_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS appointment_calls;
CREATE TABLE appointment_calls (
    id BIGSERIAL PRIMARY KEY,
    appointment_id BIGINT NOT NULL,
    donor_id BIGINT NOT NULL,
    phone TEXT,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Agendado', 'Realizado', 'Cancelado')),
    duration VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id),
    FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS donations;
CREATE TABLE donations (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT NOT NULL,
    user_creator_id BIGINT NOT NULL,
    appointment_id BIGINT,
    donor_id BIGINT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL CHECK (amount > 0),
    received_at DATE NOT NULL,
    received_time VARCHAR(20) NOT NULL,
    paid BOOLEAN DEFAULT FALSE,
    notes VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL, -- Campo para soft delete
    FOREIGN KEY (user_creator_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE
);


-- Inserção de doadores na tabela donors
INSERT INTO donors (company_id, person_type, name, cpf, active, user_creator_id)
VALUES 
(1, 'Pessoa Física', 'João Silva', '12345678901', TRUE, 1),
(1, 'Pessoa Física', 'Maria Oliveira', '98765432100', TRUE, 1),
(1, 'Pessoa Jurídica', 'Empresa Generosa', NULL, TRUE, 1);

-- Inserção de contatos dos doadores na tabela donor_contacts
INSERT INTO donor_contacts (donor_id, name, phone, email)
VALUES
(1, 'João Silva', '(11) 99999-1234', 'joao.silva@example.com'),
(2, 'Maria Oliveira', '(21) 98888-4321', 'maria.oliveira@example.com'),
(3, 'Empresa Generosa', '(31) 91234-5678', 'contato@empresagenerosa.com');

-- Inserção de endereços dos doadores na tabela donor_addresses
INSERT INTO donor_addresses (donor_id, street, neighborhood, complement, city, state, postal_code, number)
VALUES
(1, 'Rua Alegria', 'Centro', NULL, 'São Paulo', 'SP', '01010-010', '123'),
(2, 'Avenida das Flores', 'Jardim', NULL, 'Rio de Janeiro', 'RJ', '20020-020', '456'),
(3, 'Praça Generosa', 'Comercial', 'Sala 101', 'Belo Horizonte', 'MG', '30030-030', '789');