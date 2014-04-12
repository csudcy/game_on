BEGIN TRANSACTION;
    --Rename tournamentteam to tournamentteamfile
    ALTER TABLE tournamentteam RENAME TO tournamentteamfile;

    --Add team_file_uuid
    ALTER TABLE ONLY tournamentteamfile ADD COLUMN team_file_uuid character varying(36);

    --Add team_file_uuid FKs
    ALTER TABLE ONLY tournamentteamfile ADD CONSTRAINT tournamentteamfile_team_file_uuid_fkey FOREIGN KEY (team_file_uuid) REFERENCES "teamfile"(uuid) ON UPDATE CASCADE ON DELETE CASCADE;

    --Populate team_file_uuid
    UPDATE tournamentteamfile
       SET team_file_uuid = t.tf_uuid
      FROM (
        SELECT t.uuid AS t_uuid
              ,tf.uuid AS tf_uuid
              ,tf.version
              ,RANK() OVER (PARTITION BY t.uuid ORDER BY tf.version DESC) AS rnk
          FROM team t
         INNER JOIN teamfile tf ON t.uuid = tf.team_uuid
         ) AS t
     WHERE rnk = 1
       AND tournamentteamfile.team_uuid = t.t_uuid;

    --Make team_file_uuid NOT NULL
    ALTER TABLE ONLY tournamentteamfile ALTER COLUMN team_file_uuid SET NOT NULL;

    --Remove team_uuid FKs
    ALTER TABLE ONLY tournamentteamfile DROP CONSTRAINT tournamentteam_team_uuid_fkey;

    --Remove team_uuid columns
    ALTER TABLE ONLY tournamentteamfile DROP COLUMN team_uuid;

    --Rename indexes
    ALTER INDEX ix_tournamentteam_uuid RENAME TO ix_tournamentteamfile_uuid;
    ALTER INDEX tournamentteam_pkey RENAME TO tournamentteamfile_pkey;

    --"Rename" constraints
    ALTER TABLE ONLY tournamentteamfile ADD CONSTRAINT tournamentteamfile_tournament_uuid_fkey FOREIGN KEY (tournament_uuid) REFERENCES "tournament"(uuid) ON UPDATE CASCADE ON DELETE CASCADE;
    ALTER TABLE ONLY tournamentteamfile DROP CONSTRAINT tournamentteam_tournament_uuid_fkey;
COMMIT;
