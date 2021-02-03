DROP SCHEMA Lab4 CASCADE; 
CREATE SCHEMA Lab4; 

-- Create Tables for Lab4.


-- Houses(houseID, address, ownerID, mostRecentSaleDate)  
CREATE TABLE Houses 
  ( 
     houseID INTEGER, 
     address VARCHAR(50) NOT NULL, 
     ownerID INTEGER, 
     mostRecentSaleDate DATE, 
     PRIMARY KEY(houseID), 
     UNIQUE(address) 
  ); 
 

-- Persons(personID, personName, houseID)  
CREATE TABLE Persons 
  ( 
     personID INTEGER, 
     personName VARCHAR(30), 
     houseID INTEGER, 
     PRIMARY KEY(personID), 
     FOREIGN KEY(houseID) REFERENCES Houses, 
     UNIQUE(personName, houseID) 
  ); 

-- Brokers(brokerID, brokerLevel, companyName, soldCount)  
CREATE TABLE Brokers 
  ( 
     brokerID INTEGER, 
     brokerLevel CHAR(1), 
     companyName VARCHAR(30), 
     soldCount INTEGER, 
     PRIMARY KEY(brokerid) 
  ); 


-- ForSaleHouses(houseID, forSaleDate, brokerID, forSalePrice, isStillForSale)  
CREATE TABLE ForSaleHouses 
  ( 
     houseID INTEGER, 
     forSaleDate DATE, 
     brokerID INTEGER, 
     forSalePrice NUMERIC(10, 2), 
     isStillForSale BOOLEAN, 
     PRIMARY KEY(houseID, forSaleDate), 
     FOREIGN KEY(houseID) REFERENCES Houses 
  ); 


-- Offers(houseID, offererID, offerDate, offerPrice, isACurrentOffer)  
CREATE TABLE Offers 
  ( 
     houseID  INTEGER, 
     forSaleDate DATE,
     offererID INTEGER, 
     offerDate DATE, 
     offerPrice NUMERIC(10, 2) NOT NULL, 
     isACurrentOffer BOOLEAN, 
     PRIMARY KEY(houseID, forSaleDate, offererID, offerDate), 
     FOREIGN KEY(houseID, forSaleDate) REFERENCES ForSaleHouses
  ); 


-- SoldHouses(houseID, forSaleDate, soldDate, buyerID, soldPrice)  
CREATE TABLE SoldHouses 
  ( 
     houseID INTEGER, 
     forSaleDate DATE, 
     soldDate DATE, 
     buyerID INTEGER, 
     soldPrice NUMERIC(10, 2) NOT NULL, 
     PRIMARY KEY(houseID, forSaleDate), 
     FOREIGN KEY(houseID, forSaleDate) REFERENCES ForSaleHouses, 
     UNIQUE(buyerID, soldDate) 
  ); 