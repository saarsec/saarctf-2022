const DB_NAME = "<dbname>";
const DB_TOKEN = "<dbtoken>";
const VALID_ID = /^[A-Za-z0-9]{32}$/

function randomId(length) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

const db = DatabaseConnection.connect(DB_NAME, DB_TOKEN);
db.then(connection => connection.exec('PRAGMA foreign_keys = ON;'));


LambdaRequests.get(/^\/api\/issues$/, async (request, match) => {
    return await (await db).exec("SELECT id, title, author, created FROM appendonly_issues WHERE public = TRUE ORDER BY created DESC");
});

LambdaRequests.get(/^\/api\/issues\/(.*)$/, async (request, match) => {
    let id = match[1];
    if (!id.match(VALID_ID)) throw new Error("Invalid id!");
    let issue = (await (await db).select("appendonly_issues", {id: id}))[0];
    let comments = await (await db).select("appendonly_comments", {issue_id: id}, {order: "created ASC"});
    return {issue, comments};
});

LambdaRequests.post(/^\/api\/issues$/, async (request, match) => {
    let issue = request.json();
    issue.id = randomId(32);
    let result = await (await db).insert("appendonly_issues", issue);
    return {id: issue.id};
});

LambdaRequests.post(/^\/api\/comments$/, async (request, match) => {
    let comment = request.json();
    let result = await (await db).insert("appendonly_comments", comment);
    return {ok: true};
});

