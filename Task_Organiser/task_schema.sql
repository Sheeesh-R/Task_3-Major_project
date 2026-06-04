DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    color TEXT NOT NULL
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    due_date TEXT,
    priority TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL DEFAULT 'not_started',
    category_id INTEGER,
    subject_id INTEGER,
    completed_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (category_id) REFERENCES categories (id),
    FOREIGN KEY (subject_id) REFERENCES subjects (id)
);

-- Create subjects table
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    units INTEGER NOT NULL DEFAULT 2,
    target_mark INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create assessment_results table
CREATE TABLE assessment_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    weight REAL NOT NULL,                -- Percentage weight e.g. 30.0
    raw_mark REAL NOT NULL,              -- Mark achieved
    max_mark REAL NOT NULL,              -- Mark out of
    date_recorded TEXT,
    FOREIGN KEY (subject_id) REFERENCES subjects (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks (user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_subject_id ON tasks (subject_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks (priority);
CREATE INDEX IF NOT EXISTS idx_subjects_user_id ON subjects (user_id);
CREATE INDEX IF NOT EXISTS idx_assessment_results_subject_user ON assessment_results (subject_id, user_id);

-- Create atar_predictions table
CREATE TABLE atar_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    atar_score REAL NOT NULL,            -- Calculated ATAR score
    aggregate_score REAL NOT NULL,       -- ATAR aggregate score
    prediction_date TEXT NOT NULL,       -- When prediction was made
    notes TEXT,                          -- Optional notes about the prediction
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insert default categories
INSERT INTO categories (name, color) VALUES ('Work', '#007bff');
INSERT INTO categories (name, color) VALUES ('Study', '#28a745');
INSERT INTO categories (name, color) VALUES ('Personal', '#dc3545');

-- Insert default HSC subjects (will be associated with users during app initialization)
INSERT OR IGNORE INTO subjects (name, user_id) VALUES
('English Advanced', 1),
('Mathematics Advanced', 1),
('Mathematics Extension 1', 1),
('Mathematics Extension 2', 1),
('Physics', 1),
('Chemistry', 1),
('Biology', 1),
('Modern History', 1),
('Economics', 1),
('Business Studies', 1);
