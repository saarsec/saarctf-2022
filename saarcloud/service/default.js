const DB_TOKEN = "testtoken";
const validName = /^[A-Za-z0-9_]{3,64}$/
const db = DatabaseConnection.connect("default", DB_TOKEN);

LambdaRequests.get(/^\/hello\/(.*)$/, (request, match) => {
    return `Welcome here! Hello "${match[1]}"!`;
});

LambdaRequests.get(/^\/api\/hello\/(.*)$/, (request, match) => {
    return `Welcome here! Hello "${match[1]}"!`;
});

// POST /api/register/rds    body: {username: "..."}
LambdaRequests.post(/^\/api\/register\/rds$/, async (request, match) => {
    let {username} = request.json();
    if (!username.match(validName)) throw new Error("Invalid name!");
    let token = generateRandomToken();
    await (await db).insert("rds_databases", {dbname: username, token: token});
    return {dbname: username, token: token};
});

// POST /api/register/lambda    body: {username: "..."}
LambdaRequests.post(/^\/api\/register\/(lambda|cdn)$/, async (request, match) => {
    let {username} = request.json();
    if (!username.match(validName)) throw new Error("Invalid name!");
    let token = generateRandomToken();
    await (await db).insert("lambda_sites", {sitename: username, token: sha256(token)});
    return {sitename: username, token: token, log_token: passwordHash(username)};
});

// POST /api/feature   body: {username: "...", feature: "..."}
LambdaRequests.post(/^\/api\/feature$/, async (request, match) => {
    let {username, feature} = request.json();
    if (!username.match(validName)) throw new Error("Invalid name!");
    if (feature === 'rds') {
        let users = await (await db).select('rds_databases', {dbname: username});
        if (users.length === 0) throw new Error("RDS user not found!");
    } else {
        let users = await (await db).select('lambda_sites', {sitename: username});
        if (users.length === 0) throw new Error("Lambda/CDN user not found!");
    }
    await (await db).insert('featured_sites', {name: username, feature: feature});
    return {ok: true};
});

// GET /api/featured
LambdaRequests.get(/^\/api\/featured$/, async (request, match) => {
    let result = {};
    for (let feature of ['rds', 'lambda', 'cdn']) {
        let data = await (await db).select('featured_sites', {feature: feature, '_': "ts > datetime(CURRENT_TIMESTAMP, '-10 minutes')"}, {order: 'id DESC'});
        if (data.length === 0) {
            data = await (await db).select('featured_sites', {feature: feature}, {order: 'id DESC', limit: 5});
        }
        result[feature] = data;
    }
    return result;
});


// POST /api/rds/<dbname>?token=<token>
LambdaRequests.post(/^\/api\/rds\/([A-Za-z0-9_]+)$/, async (request, match) => {
    let sql = request.body;
    let db = await DatabaseConnection.connect(match[1], request.params.token);
    return await db.exec(sql);
});

// GET /api/rds/<dbname>/<table>/select?token=<token>
LambdaRequests.get(/^\/api\/rds\/([A-Za-z0-9_]+)\/([A-Za-z0-9_]+)\/select$/, async (request, match) => {
    let params = request.params;
    let db = await DatabaseConnection.connect(match[1], request.params.token);
    return await db.select(match[2], JSON.parse(params.where || '{}'), params);
});

// POST /api/rds/<dbname>/<table>/insert?token=<token>
LambdaRequests.post(/^\/api\/rds\/([A-Za-z0-9_]+)\/([A-Za-z0-9_]+)\/insert$/, async (request, match) => {
    let object = request.json();
    let db = await DatabaseConnection.connect(match[1], request.params.token);
    return await db.insert(match[2], object);
});

// POST /api/rds/<dbname>/<table>/update?token=<token>
LambdaRequests.post(/^\/api\/rds\/([A-Za-z0-9_]+)\/([A-Za-z0-9_]+)\/update$/, async (request, match) => {
    let data = request.json();
    if (data.object === undefined || data.where === undefined) throw new Error("object or where must be defined!");
    let db = await DatabaseConnection.connect(match[1], request.params.token);
    return await db.update(match[2], data.object, data.where);
});

// POST /api/rds/<dbname>/<table>/delete?token=<token>
LambdaRequests.post(/^\/api\/rds\/([A-Za-z0-9_]+)\/([A-Za-z0-9_]+)\/delete$/, async (request, match) => {
    let where = request.json();
    let db = await DatabaseConnection.connect(match[1], request.params.token);
    return await db.delete(match[2], where);
});


// POST /api/lambda/check/<sitename>?token=<token>
LambdaRequests.post(/^\/api\/lambda\/check\/([A-Za-z0-9_]+)$/, async (request, match) => {
    let name = match[1];
    let token = request.params.token;
    if (!name.match(validName)) throw new Error("Invalid name");
    let dbresult = await (await db).select("lambda_sites", {sitename: name, token: sha256(token)});
    return {ok: dbresult.length > 0};
});

// POST /api/lambda/write/<sitename>?token=<token>
LambdaRequests.post(/^\/api\/lambda\/write\/([A-Za-z0-9_]+)$/, async (request, match) => {
    let name = match[1];
    let token = request.params.token;
    if (!name.match(validName)) throw new Error("Invalid name");
    let body = request.body;
    let dbresult = await (await db).select("lambda_sites", {sitename: name, token: sha256(token)});
    if (dbresult.length > 0) {
        writeSaarLambda(name, body);
        return {ok: true};
    } else {
        throw new Error("Invalid name/token");
    }
});


// POST /api/cdn/write/<sitename>/<filename>?token=<token>
LambdaRequests.post(/^\/api\/cdn\/write\/([A-Za-z0-9_]+)\/([A-Za-z0-9_.-]+)$/, async (request, match) => {
    let name = match[1];
    let filename = match[2];
    let token = request.params.token;
    if (!name.match(validName)) throw new Error("Invalid name");
    if (filename.length > 64 || filename.length < 3 || filename.includes("..")) throw new Error("Invalid filename");
    let body = request.body;
    let dbresult = await (await db).select("lambda_sites", {sitename: name, token: sha256(token)});
    if (dbresult.length > 0) {
        writeSaarCDN(name, filename, body);
        return {ok: true};
    } else {
        throw new Error("Invalid name/token");
    }
});


LambdaRequests.get(/^\/logs$/, (request, match) => {
    let user = request.params.user;
    let log_token = request.params.token;
    if (!user.match(validName) || passwordHash(user) !== log_token) {
        return "Unauthenticated, go play elsewhere!";
    }
    // By leaving this request unhandled, drogon's websocket handler (AccessControlCtrl) can take over
    throw new HandledByServerException();
});
