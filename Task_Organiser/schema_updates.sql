-- Database Schema Updates for HSC Study Planner
-- Section 2: Database Changes from UPGRADE.md

-- Create subjects table
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create assessment_results table
CREATE TABLE IF NOT EXISTS assessment_results (
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

-- Add subject_id column to tasks table
ALTER TABLE tasks ADD COLUMN subject_id INTEGER REFERENCES subjects(id);

-- Insert default HSC subjects for existing users
INSERT OR IGNORE INTO subjects (name, user_id) 
SELECT 
    CASE 
        WHEN u.id = 1 THEN 'English Advanced'
        WHEN u.id = 2 THEN 'English Standard'
        ELSE 'English Advanced'
    END,
    u.id
FROM users u;

-- Insert more default subjects for first user (as example)
INSERT OR IGNORE INTO subjects (name, user_id) VALUES
('Mathematics Advanced', 1),
('Mathematics Extension 1', 1),
('Mathematics Extension 2', 1),
('Physics', 1),
('Chemistry', 1),
('Biology', 1),
('Modern History', 1),
('Economics', 1),
('Business Studies', 1),
('Visual Arts', 1);
