CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name     TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'engineer',
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Seed admin user (password: admin123)
INSERT INTO users (username, email, password_hash, full_name, role)
VALUES (
    'admin',
    'admin@stdo.local',
    '$2b$12$LJ3m4ys3Lk0TSwHjWz8wOeFlQSPaGZ5PZFV8MDB97vM5IjMEIJWe',
    'Администратор',
    'admin'
) ON CONFLICT (username) DO NOTHING;
