--Create the tables
CREATE TABLE match (
    uuid character varying(36) NOT NULL,
    create_date timestamp without time zone NOT NULL,
    game character varying(100) NOT NULL,
    state character varying(10) NOT NULL,
    team_1_uuid character varying(36) NOT NULL,
    team_2_uuid character varying(36) NOT NULL,
    creator_uuid character varying(36) NOT NULL,
    tournament_uuid character varying(36)
);
CREATE TABLE team (
    uuid character varying(36) NOT NULL,
    create_date timestamp without time zone NOT NULL,
    game character varying(100) NOT NULL,
    name character varying(100) NOT NULL,
    is_public boolean,
    path character varying(200) NOT NULL,
    creator_uuid character varying(36) NOT NULL
);
CREATE TABLE tournament (
    uuid character varying(36) NOT NULL,
    create_date timestamp without time zone NOT NULL,
    game character varying(100) NOT NULL,
    tournament_type character varying(100) NOT NULL,
    creator_uuid character varying(36) NOT NULL,
    best_of integer
);
CREATE TABLE tournamentteam (
    uuid character varying(36) NOT NULL,
    create_date timestamp without time zone NOT NULL,
    tournament_uuid character varying(36) NOT NULL,
    team_uuid character varying(36) NOT NULL
);
CREATE TABLE "user" (
    uuid character varying(36) NOT NULL,
    create_date timestamp without time zone NOT NULL,
    username character varying(100) NOT NULL,
    name character varying(100) NOT NULL,
    password_hash character varying(200) NOT NULL,
    is_admin boolean
);

--Create primary keys
ALTER TABLE ONLY match ADD CONSTRAINT match_pkey PRIMARY KEY (uuid);
ALTER TABLE ONLY team ADD CONSTRAINT team_pkey PRIMARY KEY (uuid);
ALTER TABLE ONLY tournament ADD CONSTRAINT tournament_pkey PRIMARY KEY (uuid);
ALTER TABLE ONLY tournamentteam ADD CONSTRAINT tournamentteam_pkey PRIMARY KEY (uuid);
ALTER TABLE ONLY "user" ADD CONSTRAINT user_pkey PRIMARY KEY (uuid);

--Create indexes on primary keys
CREATE INDEX ix_match_uuid ON match USING btree (uuid);
CREATE INDEX ix_team_uuid ON team USING btree (uuid);
CREATE INDEX ix_tournament_uuid ON tournament USING btree (uuid);
CREATE INDEX ix_tournamentteam_uuid ON tournamentteam USING btree (uuid);
CREATE INDEX ix_user_uuid ON "user" USING btree (uuid);

--Create foreign key constraints
ALTER TABLE ONLY match ADD CONSTRAINT match_creator_uuid_fkey FOREIGN KEY (creator_uuid) REFERENCES "user"(uuid) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY match ADD CONSTRAINT match_team_1_uuid_fkey FOREIGN KEY (team_1_uuid) REFERENCES team(uuid) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY match ADD CONSTRAINT match_team_2_uuid_fkey FOREIGN KEY (team_2_uuid) REFERENCES team(uuid) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY match ADD CONSTRAINT match_tournament_uuid_fkey FOREIGN KEY (tournament_uuid) REFERENCES tournament(uuid) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY team ADD CONSTRAINT team_creator_uuid_fkey FOREIGN KEY (creator_uuid) REFERENCES "user"(uuid) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY tournament ADD CONSTRAINT tournament_creator_uuid_fkey FOREIGN KEY (creator_uuid) REFERENCES "user"(uuid) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY tournamentteam ADD CONSTRAINT tournamentteam_team_uuid_fkey FOREIGN KEY (team_uuid) REFERENCES team(uuid) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY tournamentteam ADD CONSTRAINT tournamentteam_tournament_uuid_fkey FOREIGN KEY (tournament_uuid) REFERENCES tournament(uuid) ON UPDATE CASCADE ON DELETE CASCADE;
