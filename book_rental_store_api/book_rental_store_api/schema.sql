DROP TABLE IF EXISTS "auth_user";
DROP TABLE IF EXISTS "books_book";

CREATE TABLE IF NOT EXISTS "auth_user" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    "password" varchar(128) NOT NULL, 
    "last_login" datetime NULL, 
    "is_superuser" bool NOT NULL, 
    "username" varchar(150) NOT NULL UNIQUE, 
    "last_name" varchar(150) NOT NULL, 
    "email" varchar(254) NOT NULL, 
    "is_staff" bool NOT NULL, 
    "is_active" bool NOT NULL, 
    "date_joined" datetime NOT NULL, 
    "first_name" varchar(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS "books_book" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    "title" varchar(75) NOT NULL, 
    "author" varchar(75) NOT NULL, 
    "rental_due_date" datetime NOT NULL, 
    "days_rented" integer unsigned NULL CHECK ("days_rented" >= 0), 
    "renting_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
    "book_type_id" bigint NOT NULL REFERENCES "books_booktype" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX "books_book_renting_user_id_89fc9a35" ON "books_book" ("renting_user_id");
CREATE INDEX "books_book_book_type_id_ce8b1bf9" ON "books_book" ("book_type_id");

CREATE TABLE IF NOT EXISTS "books_booktype" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "book_type" varchar(50) NOT NULL, 
    "rental_rate" decimal NOT NULL, 
    "min_days" integer unsigned NOT NULL CHECK ("min_days" >= 0), 
    "min_days_rate" decimal NOT NULL
);

INSERT INTO "books_booktype" ("book_type",  "rental_rate", "min_days", "min_days_rate") VALUES ("Regular", 1.50, 2, 1.00);
INSERT INTO "books_booktype" ("book_type",  "rental_rate", "min_days", "min_days_rate") VALUES ("Novel", 1.50, 3, 1.50);
INSERT INTO "books_booktype" ("book_type",  "rental_rate", "min_days", "min_days_rate") VALUES ("Fiction", 3.00, 0, 1.00);