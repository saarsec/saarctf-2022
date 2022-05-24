use std::{fs, env, io::Write, io::Read, path::Path};

use self::diesel::prelude::*;
use rocket::form::Form;
use rocket::http::{Cookie, CookieJar};
use rocket::request::{self, FlashMessage, FromRequest, Request};
use rocket::response::{Flash, Redirect};
use rocket_sync_db_pools::diesel;

use crate::comment::{write_personal_comment, get_personal_comments};
use crate::models::{self, NewUser, ObtainedUser};
use crate::MyPgDatabase;
use crate::utils::{get_hash};

use rocket_dyn_templates::{context, Template};
use qr_code::QrCode;
use serde_json::json;

use sha2::Sha256;
use hmac::{Hmac, Mac};
use hex_literal::hex;
use base64::{encode, decode};
use rand::{distributions::Alphanumeric, Rng, thread_rng};

type HmacSha256 = Hmac<Sha256>;

#[derive(FromForm, Debug, Clone)]
struct Login {
    email: String,
    password: String,
}

#[derive(FromForm, Debug, Clone)]
struct GroupTicket {
    friends: Vec<String>
}

#[derive(FromForm, Debug, Clone)]
struct QrTicket {
    ticket: String,
}

fn load_single_user(
    conn: &diesel::PgConnection,
    mail: String,
) -> Result<models::ObtainedUser, diesel::result::Error> {
    use crate::schema::users::dsl::users;
    users
        .filter(crate::schema::users::email.eq(&mail))
        .first::<crate::models::ObtainedUser>(conn)
}


fn load_single_user_password(
    conn: &diesel::PgConnection,
    mail: String,
    password: String,
) -> Result<models::ObtainedUser, diesel::result::Error> {
    use crate::schema::users::dsl::users;
    users
        .filter(crate::schema::users::email.eq(&mail))
        .filter(crate::schema::users::password.eq(&password))
        .first::<crate::models::ObtainedUser>(conn)
}

// #[derive(FromForm, Debug, Clone)]
// pub struct Register {
//     username: String,
//     first: String,
//     last: String,
//     email: String,
//     password: String,
// }

#[derive(FromForm, Debug)]
pub struct Message<'r> {
    pub comment: &'r str,
}

struct User {
    pub username: String,
    pub first: String,
    pub last: String,
    pub email: String,
}

#[rocket::async_trait]
impl<'r> FromRequest<'r> for User {
    type Error = std::convert::Infallible;

    async fn from_request(request: &'r Request<'_>) -> request::Outcome<User, Self::Error> {
        let username = request
            .cookies()
            .get_private("username").map(|cookie| cookie.value().to_string());
        let first = request
            .cookies()
            .get_private("first").map(|cookie| cookie.value().to_string());
        let last = request
            .cookies()
            .get_private("last").map(|cookie| cookie.value().to_string());
        let email = request
            .cookies()
            .get_private("email").map(|cookie| cookie.value().to_string());
        if username.is_some() && first.is_some() && last.is_some() && email.is_some() {
            rocket::outcome::Outcome::Success(User {
                username: username.unwrap(),
                first: first.unwrap(),
                last: last.unwrap(),
                email: email.unwrap(),
            })
        } else {
            rocket::outcome::Outcome::Forward(())
        }
    }
}

#[macro_export]
macro_rules! session_uri {
    ($($t:tt)*) => (rocket::uri!("/", $crate::user:: $($t)*))
}
pub use session_uri as uri;

#[get("/")]
fn index(_user: User) -> Redirect {
    Redirect::to(uri!(profile))
}

#[get("/", rank = 2)]
fn no_auth_index() -> Template {
    Template::render("index", context! {})
}

#[get("/login")]
fn login(flash: Option<FlashMessage<'_>>) -> Template {
    Template::render("login", &flash)
}

#[get("/register")]
fn register() -> Template {
    Template::render("register", context! {})
}

#[post("/register", data = "<register>")]
async fn post_register(
    conn: MyPgDatabase,
    jar: &CookieJar<'_>,
    register: Form<NewUser>,
) -> Redirect {
    let res: Result<models::ObtainedUser, diesel::result::Error> = conn
        .run(|c| {
            use crate::schema::users::dsl::users;
            let register = register.into_inner();
            diesel::insert_into(users)
                .values(register)
                .get_result::<ObtainedUser>(c)
        })
        .await;
    match res {
        Ok(inner) => {
            jar.add_private(Cookie::new("username", inner.username));
            jar.add_private(Cookie::new("first", inner.first));
            jar.add_private(Cookie::new("last", inner.last));
            jar.add_private(Cookie::new("email", inner.email));
            Redirect::to(uri!(profile))
        }
        Err(_) => {
            println!("Error inserting new user in database!");
            Redirect::to(uri!(show_error))
        }
    }
}

#[get("/profile")]
fn profile(user: User) -> Template {
    let mail = user.email;
    let email_hash= get_hash(mail);
    let content = get_personal_comments(email_hash);
    Template::render("profile", context! {name: user.username, people: ["a","b","c"], comments: content})
}

#[post("/profile", data = "<comment>")]
fn post_message(user: User, comment: Form<Message<'_>>) -> Redirect {
    let mail = user.email;
    let result = get_hash(mail);
    println!("Got message: {:#?} from email hash {}", comment, result);
    // we write this to users/<email_hash>
    write_personal_comment(result, comment.comment.to_string()).expect("Could not write personal comment!");
    Redirect::to(uri!(profile))
}

#[get("/profile", rank = 2)]
fn profile_unauth() -> Redirect {
    Redirect::to(uri!(register))
}


pub fn get_key() -> String {
    let mut path = env::current_dir().expect("Could not read current directory!");
    path.push("key.txt");
    let metadata = fs::metadata(&path);

    match metadata {
        Ok(metadata) => {
            if metadata.is_file() {
                let mut fd = fs::OpenOptions::new()
                    .read(true)
                    .open(path)
                    .expect("Could not open file!");
                let mut contents = String::new();
                fd.read_to_string(&mut contents).expect("Could not read key file!");
                return contents;
            }
            else {
                panic!("Key file is not a file!");
            }
        }
        Err(e) => {
            let s: String = rand::thread_rng()
            .sample_iter(&rand::distributions::Alphanumeric)
            .take(16)
            .map(char::from)
            .collect();
            let mut fd = fs::OpenOptions::new()
                .write(true)
                .append(false)
                .create(true)
                .open(path).expect("Could not open file!");
            fd.write_all(s.as_bytes());
            return s;
        }
    }
}

fn sign_json(json: serde_json::Value) -> String {
    let data_string = json.to_string();
    match HmacSha256::new_from_slice(get_key().as_bytes()) {
        Ok(mut hmac) => {
            hmac.update(data_string.as_bytes());
            let result = hmac.finalize();
            let result_string = result.into_bytes();
            let signature = format!("{:x}", result_string);
            signature
        }
        Err(e) => {
            println!("Error signing json: {}", e);
            "".to_string()
        }
    }
}


#[get("/generate_ticket")]
fn generate_ticket(user: User) -> Template {
    let mail = user.email;

    let data = json!([
        mail
    ]);

    let signature = sign_json(data);

    let ticket = json!({
        "data": [mail],
        "signature": signature
    });

    let ticket_string = ticket.to_string();


    let qr_code = qr_code::QrCode::new(ticket_string);
    match qr_code {
        Ok(qr) => {
            let qrcode = qr.to_string(false, 3);
            Template::render("generate_ticket", context! {name: user.username, qr: qrcode})
        }
        Err(_) => {
            println!("Could not generate QR code!");
            Template::render("generate_ticket", context! {name: user.username, qr: ""})
        }
    }
}

#[post("/generate_group_ticket", data="<friends>")]
fn generate_group_ticket(user: User, friends: Form<GroupTicket>) -> Template {
    let mail = user.email;

    let mut friends_vec = friends.friends.to_vec();
    friends_vec.push(mail);

    let mut list = Vec::new();

    friends_vec.iter().for_each(|friend| {
        let friend_string = friend.to_string();
        if !list.contains(&friend_string) {
            list.insert(0, friend_string);
        }
    });

    let data = json!(list);

    let signature = sign_json(data);

    let ticket = json!({
        "data": list,
        "signature": signature
    });

    let ticket_string = ticket.to_string();


    let qr_code = qr_code::QrCode::new(ticket_string);
    match qr_code {
        Ok(qr) => {
            let qrcode = qr.to_string(false, 3);
            Template::render("generate_ticket", context! {name: user.username, qr: qrcode})
        }
        Err(_) => {
            println!("Could not generate QR code!");
            Template::render("generate_ticket", context! {name: user.username, qr: ""})
        }
    }
}

#[post("/check_ticket", data = "<ticket>")]
async fn check_ticket(
    ticket: Form<QrTicket>,
) -> Result<Flash<Redirect>, Flash<Redirect>> {
    let ticket_string = ticket.ticket.to_string();
    let ticket_json: serde_json::Value = serde_json::from_str(&ticket_string).unwrap();
    let signature = ticket_json["signature"].as_str().unwrap();
    let signature_expected = sign_json(ticket_json["data"].clone());
    if signature != signature_expected {
        return Err(Flash::error(Redirect::to(uri!(show_error)), "Invalid QR code!"));
    }

    let data = ticket_json["data"].clone();
    match data {
        serde_json::Value::Array(array) => {   
            if array.len() == 1 {
                let response = format!("Valid ticket for {}", array[0].as_str().unwrap());
                return Err(Flash::error(Redirect::to(uri!(show_error)), response));
            }
            else if array.len() == 0 {
                Err(Flash::error(Redirect::to(uri!(show_error)), "Invalid QR code!"))
            }  
            else {
                let response = format!("Valid group ticket: {}", ticket_string);
                return Err(Flash::error(Redirect::to(uri!(show_error)), response));
            }
        }
        _ => Err(Flash::error(Redirect::to(uri!(show_error)), "Invalid QR code!")),
    }
}

#[post("/quick_login", data = "<ticket>")]
async fn quick_login(
    conn: MyPgDatabase,
    jar: &CookieJar<'_>,
    ticket: Form<QrTicket>,
) -> Result<Flash<Redirect>, Flash<Redirect>> {
    let ticket_string = ticket.ticket.to_string();
    let ticket_json: serde_json::Value = serde_json::from_str(&ticket_string).unwrap();
    let signature = ticket_json["signature"].as_str().unwrap();
    let signature_expected = sign_json(ticket_json["data"].clone());
    if signature != signature_expected {
        return Err(Flash::error(Redirect::to(uri!(show_error)), "Invalid QR code!"));
    }

    let data = ticket_json["data"].clone();
    match data {
        serde_json::Value::Array(array) => {   
            match &array[0]{
                serde_json::Value::String(mail) => {
                    let mail = String::from(mail);
                    let response = format!("Could not find user with email {}", mail);
                    let result = conn
                        .run(move |c| load_single_user(c, mail))
                        .await;
                    match result {
                        Ok(inner) => {
                            jar.add_private(Cookie::new("username", inner.username));
                            jar.add_private(Cookie::new("first", inner.first));
                            jar.add_private(Cookie::new("last", inner.last));
                            jar.add_private(Cookie::new("email", inner.email));
                            Ok(Flash::success(Redirect::to(uri!(profile)), "Successfully logged in!"))
                        }
                        Err(_) => {
                            Err(Flash::error(Redirect::to(uri!(show_error)), response))
                        }
                    }
                }
                _ => Err(Flash::error(Redirect::to(uri!(show_error)), "Invalid QR code! (2)")),
            }
        }
        _ => Err(Flash::error(Redirect::to(uri!(show_error)), "Invalid QR code!")),
    }
}

#[post("/login", data = "<login>")]
async fn post_login(
    conn: MyPgDatabase,
    jar: &CookieJar<'_>,
    login: Form<Login>,
) -> Result<Flash<Redirect>, Flash<Redirect>> {
    println!("Login form: {:#?}", login.clone());
    let result = conn
        .run(move |c| load_single_user_password(c, login.email.to_string(), login.password.to_string()))
        .await;
    match result {
        Ok(inner) => {
            jar.add_private(Cookie::new("username", inner.username));
            jar.add_private(Cookie::new("first", inner.first));
            jar.add_private(Cookie::new("last", inner.last));
            jar.add_private(Cookie::new("email", inner.email));
            Ok(Flash::success(
                Redirect::to(uri!(profile)),
                "Successfully logged in.",
            ))
        }
        Err(_) => Err(Flash::error(
            Redirect::to(uri!(register)),
            "Invalid username/password.",
        )),
    }
}

#[get("/error")]
fn show_error() -> Template {
    Template::render("error", context! {})
}

#[get("/logout")]
fn logout(jar: &CookieJar<'_>) -> Flash<Redirect> {
    jar.remove_private(Cookie::named("user_id"));
    Flash::success(Redirect::to(uri!(login)), "Successfully logged out.")
}

pub fn routes() -> Vec<rocket::Route> {
    routes![
        index,
        no_auth_index,
        login,
        post_login,
        logout,
        register,
        post_register,
        profile,
        profile_unauth,
        post_message,
        show_error,
        generate_ticket,
        generate_group_ticket,
        quick_login,
        check_ticket
    ]
}
