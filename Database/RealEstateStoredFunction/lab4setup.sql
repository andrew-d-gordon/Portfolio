DROP SCHEMA Lab4 CASCADE;
CREATE SCHEMA Lab4;
SET SEARCH_PATH to Lab4;
ALTER ROLE andgordo SET SEARCH_PATH TO Lab4;
\i create.sql;
\i lab4_data_loading.sql;
\i increaseSomeOfferPricesFunction.pgsql;