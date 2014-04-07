--
-- PostgreSQL database dump
--

-- SET statement_timeout = 0;
-- SET client_encoding = 'UTF8';
-- SET standard_conforming_strings = on;
-- SET check_function_bodies = false;
-- SET client_min_messages = warning;

--
-- Name: match; Type: TABLE; Schema: public; Owner: postgres; Tablespace:
--

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


ALTER TABLE public.match OWNER TO postgres;

--
-- Name: team; Type: TABLE; Schema: public; Owner: postgres; Tablespace:
--

CREATE TABLE team (
    uuid character varying(36) NOT NULL,
    create_date timestamp without time zone NOT NULL,
    game character varying(100) NOT NULL,
    name character varying(100) NOT NULL,
    is_public boolean,
    path character varying(200) NOT NULL,
    creator_uuid character varying(36) NOT NULL
);


ALTER TABLE public.team OWNER TO postgres;

--
-- Name: tournament; Type: TABLE; Schema: public; Owner: postgres; Tablespace:
--

CREATE TABLE tournament (
    uuid character varying(36) NOT NULL,
    create_date timestamp without time zone NOT NULL,
    game character varying(100) NOT NULL,
    tournament_type character varying(100) NOT NULL,
    creator_uuid character varying(36) NOT NULL,
    best_of integer
);


ALTER TABLE public.tournament OWNER TO postgres;

--
-- Name: tournamentteam; Type: TABLE; Schema: public; Owner: postgres; Tablespace:
--

CREATE TABLE tournamentteam (
    uuid character varying(36) NOT NULL,
    create_date timestamp without time zone NOT NULL,
    tournament_uuid character varying(36) NOT NULL,
    team_uuid character varying(36) NOT NULL
);


ALTER TABLE public.tournamentteam OWNER TO postgres;

--
-- Name: user; Type: TABLE; Schema: public; Owner: postgres; Tablespace:
--

CREATE TABLE "user" (
    uuid character varying(36) NOT NULL,
    create_date timestamp without time zone NOT NULL,
    username character varying(100) NOT NULL,
    name character varying(100) NOT NULL,
    password_hash character varying(200) NOT NULL,
    is_admin boolean
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- Name: match_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY match
    ADD CONSTRAINT match_pkey PRIMARY KEY (uuid);


--
-- Name: team_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY team
    ADD CONSTRAINT team_pkey PRIMARY KEY (uuid);


--
-- Name: tournament_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY tournament
    ADD CONSTRAINT tournament_pkey PRIMARY KEY (uuid);


--
-- Name: tournamentteam_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY tournamentteam
    ADD CONSTRAINT tournamentteam_pkey PRIMARY KEY (uuid);


--
-- Name: user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (uuid);


--
-- Name: ix_match_uuid; Type: INDEX; Schema: public; Owner: postgres; Tablespace:
--

CREATE INDEX ix_match_uuid ON match USING btree (uuid);


--
-- Name: ix_team_uuid; Type: INDEX; Schema: public; Owner: postgres; Tablespace:
--

CREATE INDEX ix_team_uuid ON team USING btree (uuid);


--
-- Name: ix_tournament_uuid; Type: INDEX; Schema: public; Owner: postgres; Tablespace:
--

CREATE INDEX ix_tournament_uuid ON tournament USING btree (uuid);


--
-- Name: ix_tournamentteam_uuid; Type: INDEX; Schema: public; Owner: postgres; Tablespace:
--

CREATE INDEX ix_tournamentteam_uuid ON tournamentteam USING btree (uuid);


--
-- Name: ix_user_uuid; Type: INDEX; Schema: public; Owner: postgres; Tablespace:
--

CREATE INDEX ix_user_uuid ON "user" USING btree (uuid);


--
-- Name: match_creator_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY match
    ADD CONSTRAINT match_creator_uuid_fkey FOREIGN KEY (creator_uuid) REFERENCES "user"(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: match_team_1_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY match
    ADD CONSTRAINT match_team_1_uuid_fkey FOREIGN KEY (team_1_uuid) REFERENCES team(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: match_team_2_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY match
    ADD CONSTRAINT match_team_2_uuid_fkey FOREIGN KEY (team_2_uuid) REFERENCES team(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: match_tournament_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY match
    ADD CONSTRAINT match_tournament_uuid_fkey FOREIGN KEY (tournament_uuid) REFERENCES tournament(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: team_creator_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY team
    ADD CONSTRAINT team_creator_uuid_fkey FOREIGN KEY (creator_uuid) REFERENCES "user"(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: tournament_creator_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tournament
    ADD CONSTRAINT tournament_creator_uuid_fkey FOREIGN KEY (creator_uuid) REFERENCES "user"(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: tournamentteam_team_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tournamentteam
    ADD CONSTRAINT tournamentteam_team_uuid_fkey FOREIGN KEY (team_uuid) REFERENCES team(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: tournamentteam_tournament_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tournamentteam
    ADD CONSTRAINT tournamentteam_tournament_uuid_fkey FOREIGN KEY (tournament_uuid) REFERENCES tournament(uuid) ON UPDATE CASCADE ON DELETE CASCADE;
