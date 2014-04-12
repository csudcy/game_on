BEGIN TRANSACTION;
    --Add team_file_x_uuid
    ALTER TABLE ONLY match ADD COLUMN team_file_1_uuid character varying(36);
    ALTER TABLE ONLY match ADD COLUMN team_file_2_uuid character varying(36);

    --Add team_file_x_uuid FKs
    ALTER TABLE ONLY match ADD CONSTRAINT match_team_file_1_uuid_fkey FOREIGN KEY (team_file_1_uuid) REFERENCES "teamfile"(uuid) ON UPDATE CASCADE ON DELETE CASCADE;
    ALTER TABLE ONLY match ADD CONSTRAINT match_team_file_2_uuid_fkey FOREIGN KEY (team_file_2_uuid) REFERENCES "teamfile"(uuid) ON UPDATE CASCADE ON DELETE CASCADE;

    --Populate team_file_1_uuid
    UPDATE match
       SET team_file_1_uuid = t.tf_uuid
      FROM (
        SELECT t.uuid AS t_uuid
              ,tf.uuid AS tf_uuid
              ,tf.version
              ,RANK() OVER (PARTITION BY t.uuid ORDER BY tf.version DESC) AS rnk
          FROM team t
         INNER JOIN teamfile tf ON t.uuid = tf.team_uuid
         ) AS t
     WHERE rnk = 1
       AND match.team_1_uuid = t.t_uuid;

    --Populate team_file_2_uuid
    UPDATE match
       SET team_file_2_uuid = t.tf_uuid
      FROM (
        SELECT t.uuid AS t_uuid
              ,tf.uuid AS tf_uuid
              ,tf.version
              ,RANK() OVER (PARTITION BY t.uuid ORDER BY tf.version DESC) AS rnk
          FROM team t
         INNER JOIN teamfile tf ON t.uuid = tf.team_uuid
         ) AS t
     WHERE rnk = 1
       AND match.team_2_uuid = t.t_uuid;

    --Make team_file_x_uuid NOT NULL
    ALTER TABLE ONLY match ALTER COLUMN team_file_1_uuid SET NOT NULL;
    ALTER TABLE ONLY match ALTER COLUMN team_file_2_uuid SET NOT NULL;

    --Remove team_x_uuid FKs
    ALTER TABLE ONLY match DROP CONSTRAINT match_team_1_uuid_fkey;
    ALTER TABLE ONLY match DROP CONSTRAINT match_team_2_uuid_fkey;

    --Remove team_x_uuid columns
    ALTER TABLE ONLY match DROP COLUMN team_1_uuid;
    ALTER TABLE ONLY match DROP COLUMN team_2_uuid;
COMMIT;
