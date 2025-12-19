CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  phone TEXT NOT NULL UNIQUE,
  sign_viewed TEXT DEFAULT '[]',
  blocked INTEGER DEFAULT 0,
  pro INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS quizz (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  type TEXT,
  correct INTEGER DEFAULT 0,
  difficulty TEXT,
  question TEXT,
  user TEXT,
  FOREIGN KEY (user) REFERENCES user(phone)
);