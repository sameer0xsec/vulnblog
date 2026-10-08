CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(100) NOT NULL,       -- VULN: unsalted SHA1, see routes/auth.py
  role VARCHAR(20) DEFAULT 'user',
  reset_token VARCHAR(50),              -- VULN: predictable token, see auth.py
  bio TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  title VARCHAR(200),
  body TEXT,                            -- VULN: markdown/HTML rendered unsanitized on frontend
  published TINYINT DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE comments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT,
  user_id INT,
  body TEXT,                            -- VULN: stored XSS sink on frontend
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE drafts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  pickled_data BLOB,                    -- VULN: Python pickle blob, see routes/tools.py
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SHA1("admin123"), SHA1("password123"), SHA1("letmein") — unsalted, instantly crackable
INSERT INTO users (username, email, password, role, reset_token, bio) VALUES
('admin', 'admin@vulnblog.local', SHA1('admin123'), 'admin', NULL, 'Site administrator'),
('alice', 'alice@vulnblog.local', SHA1('password123'), 'user', NULL, 'I write about tech'),
('bob', 'bob@vulnblog.local', SHA1('letmein'), 'user', NULL, 'Bob blogs here');

INSERT INTO posts (user_id, title, body, published) VALUES
(1, 'Welcome to VulnBlog', 'This is the **first** post. Markdown and HTML both render here.', 1),
(2, 'My thoughts on security', 'Security is important! Or is it... <i>for this app, no.</i>', 1);

INSERT INTO comments (post_id, user_id, body) VALUES
(1, 2, 'Great first post!'),
(1, 3, 'Looking forward to more.');
