BEGIN TRANSACTION;
    --Add is_confirmed column
    ALTER TABLE ONLY match ADD COLUMN error TEXT;
COMMIT;
