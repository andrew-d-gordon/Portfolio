/**
 * runRealEstateApplication skeleton, to be modified by students
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "libpq-fe.h"

/* Exit after closing connection to the server, and frees memory used by the PGconn object. */
static void do_exit(PGconn *conn)
{
    PQfinish(conn);
    exit(EXIT_SUCCESS);
}


/* The three C functions that you need to complete for Lab4 should appear below.
 * You need to write these functions, as described in Lab4 Section 4 (and Section 5, which
 * describes the Stored Function used by the third C function.
 * In main, you need to write the tests of those function, as described in Lab4, Section 6.
 */


 /* brokerLevel is an attribute in the Brokers table.  The getBrokerLevelCount function has a char
 * (not a sting) argument, theBrokerLevel, and it should return the number of Brokers whose
 *  brokerLevel value equals theBrokerLevel.
 *
 * A value of theBrokerLevel  that is not ‘A’, ‘B’, ‘C’ or ‘D’ is an error, and you should exit.
 */
int getBrokerLevelCount(PGconn *conn, char theBrokerLevel) {

    //error check theBrokerLevel, if input ascii val under/over specified char range then err.
    if((int)theBrokerLevel < 65 || (int)theBrokerLevel > 68) {
        fprintf(stderr, "Error in getBrokerLevelCount, theBrokerLevel value of: '%c' is invalid\n", 
            theBrokerLevel);
        do_exit(conn);
    }

    // Format appropriate SELECT query for valid brokerlevel
    char stmt[1000] = "SELECT COUNT(*) FROM Brokers WHERE brokerLevel='";
    strncat(stmt, &theBrokerLevel, 1);
    strcat(stmt, "';");

    PGresult *res = PQexec(conn, stmt); //pqexec passes conn to run stmt on
    // From result get val at first row, first col (i.e. count of type of brokerlevel in brokers)
    int k = atoi(PQgetvalue(res, 0, 0));
    PQclear(res); // clear result for subsequent results
    
    return(k);
}


/* Brokers work at companies.  The company that a broker works at is indicated by the companyName
 * attribute in the Brokers table  Sometimes the company that a broker works at changes, perhaps
 * the original company was bought by another company.
 *
 * The updateCompanyName function has two arguments, a string argument oldCompanyName and another
 * string argument, newCompanyName.  For every broker in the Brokers table (if any) whose
 * companyName equals oldCompanyName, updateCompanyName should update their companyName to be
 * newCompanyName.  (Of course, there might not be any tuples whose companyName matches
 * oldCompanyName.)  updateCompanyName should return the number of tuples that were updated
 * (which might be 0).
 */
int updateCompanyName(PGconn *conn, char *oldCompanyName, char *newCompanyName) {

    // Format appropriate Update Query w/old and new company name
    char stmt[1000];
    snprintf(stmt, sizeof stmt, "UPDATE Brokers set companyName = '%s' WHERE companyName = '%s'", newCompanyName, oldCompanyName);

    PGresult *res = PQexec(conn, stmt); //pqexec passes conn to run stmt on
    int k = atoi(PQcmdTuples(res)); // used to get count of how many updates done on Brokers
    PQclear(res); // clear result for subsequent results
    return(k);

}


/* increaseSomeOfferPrices: This method has two integer parameters, theOffererID, and
 * numOfferIncreases.  increaseSomeOfferPrice invokes a Stored Function,
 * increaseSomeOfferPricesFunction, that you will need to implement and store in the database
 * according to the description in Section 5.  The Stored Function increaseSomeOfferPricesFunction
 *  should have the same parameters, theOffererID and numOfferIncreases as
 * increaseSomeOfferPrices.
 *
 * A value of numOfferIncreases that’s not positive is an error, and you should exit.
 *
 * An offerer is a person who made an offer trying to buy a house that’s for sale.  The Offers
 * table has an offererID attribute, which gives the ID of the offerer, and an offerPrice
 * attribute, which gives the offer price that’s the offerer made because they want to buy the
 * house.  increaseSomeOfferPricesFunction will increase the offerPrice for some (but not
 * necessarily all) of the Offers made by theOffererID.  Section 5 explains which Offers should
 * have their offerPrice increased, and also tells you how much you should increase those
 * offerPrice values.  The increaseSomeOfferPrices function should return the same integer result
 * that the increaseSomeOfferPricesFunction Stored Function returns.
 *
 * The increaseSomeOfferPrices function must only invoke the Stored Function
 * increaseSomeOfferPricesFunction, which does all of the work for this part of the assignment;
 * increaseSomeOfferPrices should not do the work itself.
 */
int increaseSomeOfferPrices(PGconn *conn, int theOffererID, int numOfferIncreases) {

    // ensure numOfferIncreases is a positive number
    if (numOfferIncreases<1) { 
        fprintf(stderr, "Error in increaseSomeOfferPrices, numOfferIncreases value of: '%d' is invalid. numOfferIncreases must be a positive value.\n", 
            numOfferIncreases);
        do_exit(conn);
    }

    // Format appropriate SELECT from stored function with theOffererID and numOfferIncreases
    char stmt[1000] = "SELECT increaseSomeOfferPrices(";
    char stringFromNumber[100];
    sprintf(stringFromNumber, "%d, %d", theOffererID, numOfferIncreases);
    strcat(stmt, stringFromNumber);
    strcat(stmt, ")");

    PGresult *res = PQexec(conn, stmt);
    int k = atoi(PQgetvalue(res, 0, 0)); // get count of increases made from stmt call
    PQclear(res); // clear result for subsequent results 
    return(k);
}

int
main(int argc, char **argv)
{
    PGconn     *conn;
    int theResult;
    
    char *userID = argv[1];
    char *pwd = argv[2];
    
    char conninfo[1000] = "host=cse180-db.lt.ucsc.edu user=";
    strcat(conninfo, userID);
    strcat(conninfo, " password=");
    strcat(conninfo, pwd);
    
    /* Make a connection to the database */
    conn = PQconnectdb(conninfo);
    
    /* Check to see that the backend connection was successfully made */
    if (PQstatus(conn) != CONNECTION_OK)
    {
        fprintf(stderr, "Connection to database failed: %s",
                PQerrorMessage(conn));
        do_exit(conn);
    }
        
    /* Perform the call to getBrokerLevelCount described in Section 6 of Lab4,
     * and print its output.
     */
    char ch = 'B';
    theResult = getBrokerLevelCount(conn, ch);
    printf("\nOutput of getBrokerLevelCount\nwhen the parameter theBrokerLevel is '%c'\n%d\n\n", ch, theResult);
        
    /* Perform the call to updateCompanyName described in Section 6 of Lab4
     * and print its output. Weathervane Group Realty
     */
    char oldCompanyName1[1000] = "Weathervane Group Realty";
    char newCompanyName1[1000] = "Catbird Estates";
    theResult = updateCompanyName(conn, oldCompanyName1, newCompanyName1);
    printf("\nOutput of updateMovieName when the oldCompanyName is \n'%s' and the newCompanyName is '%s'\n%d\n\n", oldCompanyName1, newCompanyName1, theResult);

    char oldCompanyName2[1000] = "Intero";
    char newCompanyName2[1000] = "Sotheby";
    theResult = updateCompanyName(conn, oldCompanyName2, newCompanyName2);
    printf("\nOutput of updateMovieName when the oldCompanyName is \n'%s' and the newCompanyName is '%s'\n%d\n\n", oldCompanyName2, newCompanyName2, theResult);
        
    /* Perform the two calls to increaseSomeOfferPrices described in Section 6 of Lab4
     * and print their outputs.
     */

    int theOffererID = 13;
    int numOfferIncreases = 4;
    theResult = increaseSomeOfferPrices(conn, theOffererID, numOfferIncreases);
    printf("\nOutput of increaseSomeOfferPrices\nwhen parameter theOffererID is %d and numOfferIncreases = %d\n%d\n\n", theOffererID, numOfferIncreases, theResult);

    theOffererID = 13;
    numOfferIncreases = 2;
    theResult = increaseSomeOfferPrices(conn, theOffererID, numOfferIncreases);
    printf("\nOutput of increaseSomeOfferPrices\nwhen parameter theOffererID is %d and numOfferIncreases = %d\n%d\n\n", theOffererID, numOfferIncreases, theResult);
    
    // End conn and exit successful with return 0
    do_exit(conn);
    return 0;

}


