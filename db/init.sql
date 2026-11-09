-- Idempotent: safe to run on every `docker compose up`.
-- sqlcmd variables CATALOG_PWD and ORDERS_PWD are passed with -v.
IF DB_ID('catalog') IS NULL CREATE DATABASE catalog;
IF DB_ID('orders') IS NULL CREATE DATABASE orders;
GO

IF SUSER_ID('catalog_user') IS NULL CREATE LOGIN catalog_user WITH PASSWORD = '$(CATALOG_PWD)', CHECK_POLICY = OFF;
IF SUSER_ID('orders_user') IS NULL CREATE LOGIN orders_user WITH PASSWORD = '$(ORDERS_PWD)', CHECK_POLICY = OFF;
GO

-- Each login can only touch its own database.
USE catalog;
GO
IF USER_ID('catalog_user') IS NULL CREATE USER catalog_user FOR LOGIN catalog_user;
ALTER ROLE db_ddladmin ADD MEMBER catalog_user;
ALTER ROLE db_datareader ADD MEMBER catalog_user;
ALTER ROLE db_datawriter ADD MEMBER catalog_user;
GO

USE orders;
GO
IF USER_ID('orders_user') IS NULL CREATE USER orders_user FOR LOGIN orders_user;
ALTER ROLE db_ddladmin ADD MEMBER orders_user;
ALTER ROLE db_datareader ADD MEMBER orders_user;
ALTER ROLE db_datawriter ADD MEMBER orders_user;
GO
