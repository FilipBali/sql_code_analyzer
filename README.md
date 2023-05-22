## About

This program provides the ability to analyze SQL code in the context of past statements. It uses the SQLGlot library for parsing. 

The context between SQL statements is recorded using a data structure that reflects the database schema. Only important information about changes of the database schema are stored by processing the statements that perform those actions.

The parsed SQL code is processed into an abstract syntax tree using the SQLGlot library. This tree is then traversed using the DFS algorithm. During the traversal, checking rules are applied. Rules checking the SQL statement have access to the context-checking API as well as to a structure that contains data about an already created database structure. The program supports the addition of new rules. The output of the program is a list of reports that have been created based on these rules.

The state of the data structure that represents the database schema can be saved or restored. The program also supports connection to a running database system from which it obtains the DDL and initializes its own data structure state.

A more detailed description will be added later. The current goal is to expand the set of supported SQL statements that change database schema state and connection support for most databases.
