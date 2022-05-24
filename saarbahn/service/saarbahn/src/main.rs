#[macro_use] extern crate rocket;
#[macro_use] extern crate diesel;
mod user;
mod stops;
mod comment;
mod utils;
pub mod schema;
pub mod models;
use rocket_dyn_templates::Template;
use rocket_sync_db_pools::database;


#[database("my_pg_db")]
struct MyPgDatabase(diesel::PgConnection);


#[launch]
fn rocket() -> _ {
    rocket::build()
        .attach(Template::fairing())
        .attach(MyPgDatabase::fairing())
        .mount("/", user::routes())
        .mount("/stops/", stops::routes())
}
