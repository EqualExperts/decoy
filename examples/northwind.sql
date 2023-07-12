CREATE OR REPLACE TABLE Employees AS (
    SELECT
        range as EmployeeID,
        faker_last_name() as LastName,
        faker_first_name() as FirstName,
        xeger('[a-zA-Z0-9]{10,}') as Title,
        xeger('[a-zA-Z0-9]{10,}') as TitleOfCourtesy,
        mimesis_datetime_date() as BirthDate,
        mimesis_datetime_date() as HireDate,
        faker_street_address() as Address,
        faker_city() as City,
        faker_county() as Region,
        faker_postcode() as PostalCode,
        faker_country() as Country,
        faker_phone_number() as HomePhone,
        faker_country_calling_code() as Extension,
        xeger('[a-zA-Z0-9]{10,}') as Photo,
        xeger('[a-zA-Z0-9]{10,}') as Notes,
        random_randint(0,10) as ReportsTo,
        xeger('[a-zA-Z0-9]{10,}') as PhotoPath,
    FROM RANGE(100)
);


CREATE OR REPLACE TABLE Categories AS (
    SELECT
        range as CategoryID,
        xeger('[a-zA-Z0-9]{10,}') as CategoryName,
        xeger('[a-zA-Z0-9]{40,}') as Description,
        xeger('[a-zA-Z0-9]{40,}') as Picture,   
    FROM RANGE(10)
);

CREATE OR REPLACE TABLE Customer AS (
    SELECT
        xeger('[A-Z]{5},}') as CustomerID,
        faker_company() as CompanyName,
        faker_name() as ContactName,
        xeger('[a-zA-Z0-9]{10,}') as ContactTitle,
        faker_street_address() as Address,
        faker_city() as City,
        faker_county() as Region,
        faker_postcode() as PostalCode,
        faker_country() as Country,
        faker_phone_number() as Phone,
        faker_phone_number() as Fax, 
    FROM RANGE(1000)
);

CREATE OR REPLACE TABLE Suppliers AS (
    SELECT
        range as SupplierID,
        faker_company() as CompanyName,
        faker_name() as ContactName,
        xeger('[a-zA-Z0-9]{10,}') as ContactTitle,
        faker_street_address() as Address,
        faker_city() as City,
        faker_county() as Region,
        faker_postcode() as PostalCode,
        faker_country() as Country,
        faker_phone_number() as Phone,
        faker_phone_number() as Fax, 
        faker_uri() as HomePage,
    FROM RANGE(50)
);

CREATE OR REPLACE TABLE Orders AS (
    SELECT
        range as OrderID,
        oversample('Customer', 'CustomerID') as CustomerID,
        oversample('Employees', 'EmployeeID') as EmployeeID,
        mimesis_datetime_date() as OrderDate,
        mimesis_datetime_date() as RequiredDate,
        mimesis_datetime_date() as ShippedDate,
        random_randint(0,50) as ShipVia,
        random_randint(0,100000) as Freight,
        faker_company() as ShipName,
        faker_street_address() as ShipAddress,
        faker_city() as ShipCity,
        faker_county() as ShipRegion,
        faker_postcode() as ShipPostalCode,
        faker_country() as ShipCountry, 
    FROM RANGE(100000)
);

CREATE OR REPLACE TABLE Products AS (
    SELECT
        range as ProductID,
        xeger('[a-zA-Z0-9]{10,}') as ProductName,
        oversample('Suppliers', 'SupplierID') as SupplierID,
        oversample('Categories', 'CategoryID') as CategoryID,
        random_randint(0,1000) as QuantityPerUnit,
        random_randint(0,1000) as UnitPrice,
        random_randint(0,100) as UnitsInStock,
        random_randint(0,100) as UnitsOnOrder,
        random_randint(0,100) as ReorderLevel,
        random_randint(0, 1) as Discontinued,
    FROM RANGE(1000)
);


CREATE OR REPLACE TABLE "Order Details" AS (
    SELECT
        oversample('Orders', 'OrderID') as OrderID,
        oversample('Products', 'ProductID') as ProductID,
        random_randint(0,1000) as UnitPrice,
        random_randint(0,100) as Quantity,
        random_uniform(0, 1) as Discount
    FROM RANGE(100000)
);

create view "Customer and Suppliers by City" AS
SELECT City, CompanyName, ContactName, 'Customers' AS Relationship
FROM Customers
UNION SELECT City, CompanyName, ContactName, 'Suppliers'
FROM Suppliers;

create view "Alphabetical list of products" AS
SELECT Products.*, Categories.CategoryName
FROM Categories INNER JOIN Products ON Categories.CategoryID = Products.CategoryID
WHERE (((Products.Discontinued)=0));

create view "Current Product List" AS
SELECT Product_List.ProductID, Product_List.ProductName
FROM Products AS Product_List
WHERE (((Product_List.Discontinued)=0));

create view "Orders Qry" AS
SELECT Orders.OrderID, Orders.CustomerID, Orders.EmployeeID, Orders.OrderDate, Orders.RequiredDate,
	Orders.ShippedDate, Orders.ShipVia, Orders.Freight, Orders.ShipName, Orders.ShipAddress, Orders.ShipCity,
	Orders.ShipRegion, Orders.ShipPostalCode, Orders.ShipCountry,
	Customers.CompanyName, Customers.Address, Customers.City, Customers.Region, Customers.PostalCode, Customers.Country
FROM Customers INNER JOIN Orders ON Customers.CustomerID = Orders.CustomerID;

create view "Products Above Average Price" AS
SELECT Products.ProductName, Products.UnitPrice
FROM Products
WHERE Products.UnitPrice>(SELECT AVG(UnitPrice) From Products);

create view "Products by Category" AS
SELECT Categories.CategoryName, Products.ProductName, Products.QuantityPerUnit, Products.UnitsInStock, Products.Discontinued
FROM Categories INNER JOIN Products ON Categories.CategoryID = Products.CategoryID
WHERE Products.Discontinued <> 1;

create view "Quarterly Orders" AS
SELECT DISTINCT Customers.CustomerID, Customers.CompanyName, Customers.City, Customers.Country
FROM Customers RIGHT JOIN Orders ON Customers.CustomerID = Orders.CustomerID
WHERE Orders.OrderDate BETWEEN '19970101' And '19971231';

create view Invoices AS
SELECT Orders.ShipName, Orders.ShipAddress, Orders.ShipCity, Orders.ShipRegion, Orders.ShipPostalCode,
	Orders.ShipCountry, Orders.CustomerID, Customers.CompanyName AS CustomerName, Customers.Address, Customers.City,
	Customers.Region, Customers.PostalCode, Customers.Country,
	(FirstName + ' ' + LastName) AS Salesperson,
	Orders.OrderID, Orders.OrderDate, Orders.RequiredDate, Orders.ShippedDate, Shippers.CompanyName As ShipperName,
	"Order Details".ProductID, Products.ProductName, "Order Details".UnitPrice, "Order Details".Quantity,
	"Order Details".Discount,
	(CONVERT(money,("Order Details".UnitPrice*Quantity*(1-Discount)/100))*100) AS ExtendedPrice, Orders.Freight
FROM 	Shippers INNER JOIN
		(Products INNER JOIN
			(
				(Employees INNER JOIN
					(Customers INNER JOIN Orders ON Customers.CustomerID = Orders.CustomerID)
				ON Employees.EmployeeID = Orders.EmployeeID)
			INNER JOIN "Order Details" ON Orders.OrderID = "Order Details".OrderID)
		ON Products.ProductID = "Order Details".ProductID)
	ON Shippers.ShipperID = Orders.ShipVia

create view "Order Details Extended" AS
SELECT "Order Details".OrderID, "Order Details".ProductID, Products.ProductName,
	"Order Details".UnitPrice, "Order Details".Quantity, "Order Details".Discount,
	(CONVERT(money,("Order Details".UnitPrice*Quantity*(1-Discount)/100))*100) AS ExtendedPrice
FROM Products INNER JOIN "Order Details" ON Products.ProductID = "Order Details".ProductID;

create view "Order Subtotals" AS
SELECT "Order Details".OrderID, Sum(CONVERT(money,("Order Details".UnitPrice*Quantity*(1-Discount)/100))*100) AS Subtotal
FROM "Order Details"
GROUP BY "Order Details".OrderID;

create view "Product Sales for 1997" AS
SELECT Categories.CategoryName, Products.ProductName,
Sum(CONVERT(money,("Order Details".UnitPrice*Quantity*(1-Discount)/100))*100) AS ProductSales
FROM (Categories INNER JOIN Products ON Categories.CategoryID = Products.CategoryID)
	INNER JOIN (Orders
		INNER JOIN "Order Details" ON Orders.OrderID = "Order Details".OrderID)
	ON Products.ProductID = "Order Details".ProductID
WHERE (((Orders.ShippedDate) Between '19970101' And '19971231'))
GROUP BY Categories.CategoryName, Products.ProductName;

create view "Category Sales for 1997" AS
SELECT "Product Sales for 1997".CategoryName, Sum("Product Sales for 1997".ProductSales) AS CategorySales
FROM "Product Sales for 1997"
GROUP BY "Product Sales for 1997".CategoryName;

create view "Sales by Category" AS
SELECT Categories.CategoryID, Categories.CategoryName, Products.ProductName,
	Sum("Order Details Extended".ExtendedPrice) AS ProductSales
FROM 	Categories INNER JOIN
		(Products INNER JOIN
			(Orders INNER JOIN "Order Details Extended" ON Orders.OrderID = "Order Details Extended".OrderID)
		ON Products.ProductID = "Order Details Extended".ProductID)
	ON Categories.CategoryID = Products.CategoryID
WHERE Orders.OrderDate BETWEEN '19970101' And '19971231'
GROUP BY Categories.CategoryID, Categories.CategoryName, Products.ProductName;

create view "Sales Totals by Amount" AS
SELECT "Order Subtotals".Subtotal AS SaleAmount, Orders.OrderID, Customers.CompanyName, Orders.ShippedDate
FROM 	Customers INNER JOIN
		(Orders INNER JOIN "Order Subtotals" ON Orders.OrderID = "Order Subtotals".OrderID)
	ON Customers.CustomerID = Orders.CustomerID
WHERE ("Order Subtotals".Subtotal >2500) AND (Orders.ShippedDate BETWEEN '19970101' And '19971231');

create view "Summary of Sales by Quarter" AS
SELECT Orders.ShippedDate, Orders.OrderID, "Order Subtotals".Subtotal
FROM Orders INNER JOIN "Order Subtotals" ON Orders.OrderID = "Order Subtotals".OrderID
WHERE Orders.ShippedDate IS NOT NULL;

create view "Summary of Sales by Year" AS
SELECT Orders.ShippedDate, Orders.OrderID, "Order Subtotals".Subtotal
FROM Orders INNER JOIN "Order Subtotals" ON Orders.OrderID = "Order Subtotals".OrderID
WHERE Orders.ShippedDate IS NOT NULL;

create procedure "Ten Most Expensive Products" AS
SET ROWCOUNT 10
SELECT Products.ProductName AS TenMostExpensiveProducts, Products.UnitPrice
FROM Products
ORDER BY Products.UnitPrice DESC;

create procedure "Employee Sales by Country"
@Beginning_Date DateTime, @Ending_Date DateTime AS
SELECT Employees.Country, Employees.LastName, Employees.FirstName, Orders.ShippedDate, Orders.OrderID, "Order Subtotals".Subtotal AS SaleAmount
FROM Employees INNER JOIN
	(Orders INNER JOIN "Order Subtotals" ON Orders.OrderID = "Order Subtotals".OrderID)
	ON Employees.EmployeeID = Orders.EmployeeID
WHERE Orders.ShippedDate Between @Beginning_Date And @Ending_Date;
GO

create procedure "Sales by Year"
	@Beginning_Date DateTime, @Ending_Date DateTime AS
SELECT Orders.ShippedDate, Orders.OrderID, "Order Subtotals".Subtotal, DATENAME(yy,ShippedDate) AS Year
FROM Orders INNER JOIN "Order Subtotals" ON Orders.OrderID = "Order Subtotals".OrderID
WHERE Orders.ShippedDate Between @Beginning_Date And @Ending_Date;