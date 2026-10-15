
-- ==========================================
-- STOCKFLOW - AUTHENTICATION MIGRATION 001
-- ==========================================

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    username VARCHAR(50) NOT NULL UNIQUE,

    password_hash TEXT NOT NULL,

    role VARCHAR(20) NOT NULL
        DEFAULT 'viewer',

    is_active BOOLEAN NOT NULL
        DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_users_role
        CHECK (
            role IN ('admin', 'operator', 'viewer')
        ),

    CONSTRAINT chk_users_username
        CHECK (
            LENGTH(TRIM(username)) >= 3
        )
);
