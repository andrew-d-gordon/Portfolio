# Real Estate Stored Function Application

This project serves as a C program which can utilize the libpq library in order to run PostgreSQL operations.

Example tables can be generated via the create.sql and data_loading.sql. The primary functionality exists in runRealEstateApplication.c, more of libpq's cabapilities can be explored [here](https://www.postgresql.org/docs/9.5/libpq.html).

An example stored function which is utilized by the C code lives in increaseSomeOfferPrices.pgsql.

Utilize MakeAndExecute in order to compile and utilize runRealEstateApplication.c.

It is necessary to set your PostgreSQL credentials within MakeAndExecute as sql_username and psql_password are placeholders.

`gcc -L/usr/include -lpq -o runRealEstateApplication runRealEstateApplication.c
./runRealEstateApplication psql_username psql_password`
