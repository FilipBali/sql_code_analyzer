SELECT la.nieco2, aa.nieco5
FROM table12, tab13
WHERE table.id = "Oracle";


CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    price DECIMAL(10,2)
);


SELECT sub.product_id, nieco, la.nieco2
FROM ( SELECT product_id, lf.producdt_id
       FROM products bla
     ) sub, table10, table12 sub2;

SELECT la.nieco2, aa.nieco5
FROM table12, tab13;


SELECT product_id, niecoco
FROM products;

SELECT product_id
FROM orders;
