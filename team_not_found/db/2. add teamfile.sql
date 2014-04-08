BEGIN TRANSACTION;
    --Create the teamfile table
    CREATE TABLE teamfile (
        uuid character varying(36) NOT NULL,
        create_date timestamp without time zone NOT NULL,
        team_uuid character varying(36) NOT NULL,
        path character varying(200) NOT NULL,
        version integer NOT NULL
    );
    --Create primary key
    ALTER TABLE ONLY teamfile ADD CONSTRAINT teamfile_pkey PRIMARY KEY (uuid);
    --Create index on primary key
    CREATE INDEX ix_teamfile_uuid ON teamfile USING btree (uuid);
    --Create FKs
    ALTER TABLE ONLY teamfile ADD CONSTRAINT teamfile_team_uuid_fkey FOREIGN KEY (team_uuid) REFERENCES "team"(uuid) ON UPDATE CASCADE ON DELETE CASCADE;
    --Create unique constraints
    ALTER TABLE teamfile ADD CONSTRAINT teamfile_path_uq UNIQUE (path);
    ALTER TABLE teamfile ADD CONSTRAINT teamfile_team_uuid_version_uq UNIQUE (team_uuid, version);

    --Insert existing teams into teamfile
    INSERT INTO teamfile
    SELECT uuid
          ,create_date
          ,uuid
          ,path
          ,1
    FROM team;

    --Remove columns from team
    ALTER TABLE team DROP COLUMN path;
COMMIT;
