CREATE OR REPLACE FUNCTION increaseSomeOfferPrices(IN theOffererID INTEGER, IN numOfferIncreases INTEGER)
RETURNS INTEGER AS $$

DECLARE 
newOfferPrice NUMERIC(10,2);
increaseCount INTEGER;
increasePerOffer INTEGER;

offersC CURSOR FOR SELECT o.houseID, o.forSaleDate, o.offererID, o.offerPrice
from Offers o
where o.houseID NOT IN (SELECT s.houseID
                        FROM SoldHouses s
                        WHERE s.forSaleDate::date = o.forSaleDate::date and 
                        s.houseID = o.houseID) 
      AND o.offererID = theOffererID
order by o.offerPrice ASC;  

fhouseID INTEGER;
fForSaleDate DATE;
fOffererID INTEGER;
fOfferPrice NUMERIC(10,2);
fshouseID INTEGER;
fsForSaleDate DATE;

BEGIN

increaseCount = 0;
increasePerOffer = 8000;

OPEN offersC;

LOOP

FETCH offersC INTO fhouseID,fForSaleDate,fOffererID,fOfferPrice,fshouseID,fsForSaleDate;

EXIT WHEN NOT FOUND OR increaseCount=numOfferIncreases;

newOfferPrice = fOfferPrice+increasePerOffer;

UPDATE Offers
SET offerPrice = newOfferPrice
WHERE offererID = theOffererID
AND houseID = fhouseID
AND forSaleDate::date = fForSaleDate::date
AND offerPrice = fOfferPrice;

increaseCount = increaseCount+1;

END LOOP;

CLOSE offersC;
RETURN increaseCount;

END

$$ LANGUAGE plpgsql;
