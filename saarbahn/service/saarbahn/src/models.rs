use super::schema::users;

#[derive(Queryable, Debug)]
pub struct ObtainedUser {
    pub id: i32,
    pub username: String,
    pub first: String,
    pub last: String,
    pub email: String,
    pub password: String,
}

#[derive(Insertable, Debug, FromForm, Clone)]
#[table_name="users"]
pub struct NewUser {
    pub username: String,
    pub first: String,
    pub last: String,
    pub email: String,
    pub password: String,
}