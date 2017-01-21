CREATE TABLE gh_user (
    id      integer primary key,
    name    varchar(50)
);

CREATE TABLE repository (
    id          integer primary key,
    owner       varchar(50),
    name        varchar(50)
);

CREATE TABLE sentiment (
    id            serial primary key,
    text          text,
    polarity      numeric,
    subjectivity  numeric
);

CREATE TABLE sentiment_breakdown (
    id            serial primary key,
    s_id          integer references sentiment (id) on delete cascade,
    sentence      text,
    polarity      numeric,
    subjectivity  numeric
);

CREATE TABLE issue (
    id            integer primary key,
    number        integer,
    repo_id       integer references repository (id) on delete cascade,
    gh_user_id    integer references gh_user (id),
    title_s_id    integer references sentiment (id),
    body_s_id     integer references sentiment (id)
);

CREATE TABLE comment (
    id            integer primary key,
    issue_id      integer references issue (id) on delete cascade,
    gh_user_id    integer references gh_user (id),
    body_s_id     integer references sentiment (id)
);
