def test_sql_001():
    return "SELECT \n col1 --Koment2 \n" \
           "FROM --Koment3\n table1 --Koment4"


def test_sql_002():
    return "SELECT COUNT(CustomerID), Country \n" \
          "FROM Tabulka;"


def test_sql_003():
    """
SELECT COUNT(CustomerID), Country
FROM (SELECT Col2 FROM Customers)
GROUP BY Country
HAVING COUNT(CustomerID) > 5
ORDER BY COUNT(CustomerID) DESC;
    """
    return "SELECT COUNT(CustomerID), Country \n" \
          "FROM (SELECT Col2 FROM Customers) \n" \
          "GROUP BY Country\n" \
          "HAVING COUNT(CustomerID) > 5\n" \
          "ORDER BY COUNT(CustomerID) DESC;\n"

def test_sql_004():
    return "CREATE TABLE Persons (\n" \
          "PersonID int,\n" \
          "LastName varchar(255),\n" \
          "FirstName varchar(255),\n" \
          "Address varchar(255),\n" \
          "City varchar(255)\n" \
          ");"


def test_sql_005():
    """
SELECT COUNT(CustomerID);
    """
    return "SELECT COUNT(CustomerID);"