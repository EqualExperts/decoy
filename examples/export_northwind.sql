COPY (SELECT * FROM Employees ) TO 'Employees.csv' WITH (HEADER 1, DELIMITER ',');
COPY (SELECT * FROM Categories ) TO 'Categories.csv' WITH (HEADER 1, DELIMITER ',');
COPY (SELECT * FROM Customers ) TO 'Customers.csv' WITH (HEADER 1, DELIMITER ',');
COPY (SELECT * FROM Shippers ) TO 'Shippers.csv' WITH (HEADER 1, DELIMITER ',');
COPY (SELECT * FROM Suppliers ) TO 'Suppliers.csv' WITH (HEADER 1, DELIMITER ',');
COPY (SELECT * FROM Orders ) TO 'Orders.csv' WITH (HEADER 1, DELIMITER ',');
COPY (SELECT * FROM Products ) TO 'Products.csv' WITH (HEADER 1, DELIMITER ',');
COPY (SELECT * FROM "Order Details" ) TO 'Order Details.csv' WITH (HEADER 1, DELIMITER ',');