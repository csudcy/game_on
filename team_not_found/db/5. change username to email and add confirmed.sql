BEGIN TRANSACTION;
    --Change username to email
    ALTER TABLE ONLY "user" RENAME COLUMN username TO email;

    --Add is_confirmed column
    ALTER TABLE ONLY "user" ADD COLUMN is_confirmed boolean;

    --Update is_confirmed
    UPDATE "user"
       SET is_confirmed = true;

    --Change is_confirmed to NOT NULL
    ALTER TABLE ONLY "user" ALTER COLUMN is_confirmed SET NOT NULL;
COMMIT;
