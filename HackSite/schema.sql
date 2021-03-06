DROP TABLE IF EXISTS question;
DROP TABLE IF EXISTS answer;

CREATE TABLE question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    body NOT NULL
);

CREATE TABLE answer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    body NOT NULL
    --FOREIGN KEY (question_id) REFERENCES question (id)
);