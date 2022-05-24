use std::fs;

use rocket_dyn_templates::{context, Template};
use rocket::{form::Form, response::Redirect};

use crate::{user::Message, comment::{write_rating, get_ratings}, utils::get_hash};


#[get("/")]
fn index() -> Template{
    let stops = ["brebach".to_string(), "dudweiler".to_string(), "ludwigskirche".to_string(), "hauptbahnhof".to_string(), "heusweiler".to_string(), "johanneskirche".to_string(), "kleinblittersdorf".to_string(), "lebach".to_string(), "riegelsberg".to_string(), "roemerkastell".to_string(), "universitaet".to_string(), "sylt".to_string()];
    Template::render("stops", context! {
        stops: stops
    })
}

#[get("/<name>")]
fn stop(name: &str) -> Template{
    println!("I want to stop at {}!", name);
    let comments = get_ratings(name.to_string());
    Template::render("stop", context!{name: name, comments: comments})
}

#[post("/<name>", data = "<comment>")]
fn stop_comment(name: &str, comment: Form<Message<'_>>) -> Redirect{
    println!("Posting comment {:#?}!", comment);
    let _result = write_rating(name.to_string(), comment.comment.to_string());
    Redirect::to(uri!("/stops",stop(name)))

}

pub fn routes() -> Vec<rocket::Route> {
    routes![
        index,
        stop,
        stop_comment,
    ]
}
