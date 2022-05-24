CREATE TABLE users(
  id Integer Primary Key Generated Always as Identity,
  username VARCHAR(50) NOT NULL,
  first VARCHAR(50) NOT NULL,
  last VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(100) NOT NULL
)
