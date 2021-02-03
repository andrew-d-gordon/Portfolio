DROP SCHEMA RealEstate CASCADE;
CREATE SCHEMA RealEstate;
SET SEARCH_PATH to RealEstate;
ALTER ROLE psql_username SET SEARCH_PATH TO RealEstate;
\i create.sql;
\i data_loading.sql;
\i increaseSomeOfferPricesFunction.pgsql;