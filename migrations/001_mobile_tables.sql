-- Feed
CREATE TABLE IF NOT EXISTS posts (
    id          BIGSERIAL PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id),
    title       TEXT NOT NULL,
    body        TEXT NOT NULL,
    tags        JSONB NOT NULL DEFAULT '[]',
    city        TEXT,
    likes_count INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS post_likes (
    post_id     BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id     TEXT NOT NULL REFERENCES users(id),
    PRIMARY KEY (post_id, user_id)
);

CREATE TABLE IF NOT EXISTS post_comments (
    id          BIGSERIAL PRIMARY KEY,
    post_id     BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id     TEXT NOT NULL REFERENCES users(id),
    body        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Discover
CREATE TABLE IF NOT EXISTS circles (
    id           BIGSERIAL PRIMARY KEY,
    name         TEXT NOT NULL,
    description  TEXT,
    member_count INTEGER NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS circle_members (
    circle_id   BIGINT NOT NULL REFERENCES circles(id) ON DELETE CASCADE,
    user_id     TEXT NOT NULL REFERENCES users(id),
    joined_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (circle_id, user_id)
);

-- Plans
CREATE TABLE IF NOT EXISTS move_plans (
    id          BIGSERIAL PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id),
    title       TEXT NOT NULL,
    from_city   TEXT,
    to_city     TEXT,
    stage       TEXT NOT NULL DEFAULT 'planning'
                CHECK (stage IN ('planning', 'booked', 'completed')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS move_checklist_items (
    id          BIGSERIAL PRIMARY KEY,
    plan_id     BIGINT NOT NULL REFERENCES move_plans(id) ON DELETE CASCADE,
    text        TEXT NOT NULL,
    is_done     BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order  INTEGER NOT NULL DEFAULT 0
);

-- Profile
CREATE TABLE IF NOT EXISTS user_badges (
    user_id     TEXT NOT NULL REFERENCES users(id),
    badge       TEXT NOT NULL
                CHECK (badge IN ('host', 'verified_reviewer', 'community_builder')),
    earned_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, badge)
);
