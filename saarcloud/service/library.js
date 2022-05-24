function debug() {
    let location = (new Error()).stack.toString().split('\n')[2].trimLeft();
    let date = (new Date()).toISOString().substr(0, 19).replace('T', ' ');
    let new_arguments = [date, location, "|"]
    for (let arg of arguments) {
        new_arguments.push(typeof arg === 'object' ? JSON.stringify(arg) : arg);
    }
    println.apply(this, new_arguments);
}

function deepdebug(x) {
    if (x === undefined) {
        println(typeof (x));
    } else {
        println(JSON.stringify({
            type: typeof (x),
            keys: Object.keys(x),
            properties: Object.getOwnPropertyNames(x),
            value: x === undefined ? 'undefined' : x
        }, null, 2));
    }
}

class DatabaseConnection {

    constructor(name) {
        this.name = name;
    }

    static async connect(name, token) {
        if (!await SaarRDSInterface.authorize(name, token))
            throw new Error("Invalid credentials!");
        return new DatabaseConnection(name);
    }

    static escape(x) {
        if (x === null || x === undefined) return 'NULL';
        if (typeof x === 'number' || typeof x === 'boolean') return '' + x;
        if (typeof x === 'object') x = JSON.stringify(x);
        return "'" + x.toString().replace("'", "''") + "'";
    }

    static escapeConditions(conditions) {
        if (conditions) {
            let sqlConditions = [];
            for (let key of Object.keys(conditions)) {
                let value = conditions[key];
                if (key === '_') sqlConditions.push(value);
                else if (key.includes(' ')) sqlConditions.push(`${key} ${DatabaseConnection.escape(value)}`);
                else if (value === null) sqlConditions.push(`${key} IS ${DatabaseConnection.escape(value)}`);
                else sqlConditions.push(`${key} = ${DatabaseConnection.escape(value)}`);
            }
            if (sqlConditions.length > 0)
                return ` WHERE ${sqlConditions.join(' AND ')}`;
        }
        return '';
    }

    async exec(sql) {
        return await SaarRDSInterface.execSQL(this.name, sql);
    }

    async select(table, where = {}, options = {limit: null, offset: null, order: null}) {
        let sql = `SELECT * FROM ${table}`;
        sql += DatabaseConnection.escapeConditions(where);
        if (options.order) sql += ` ORDER BY ${options.order}`;
        if (options.limit) sql += ` LIMIT ${options.limit}`;
        if (options.offset) sql += ` OFFSET ${options.offset}`;
        return await this.exec(sql);
    }

    async insert(table, object) {
        let keys = [];
        let values = [];
        for (let key of Object.keys(object)) {
            keys.push(key);
            values.push(DatabaseConnection.escape(object[key]));
        }
        let sql = `INSERT INTO ${table} (${keys.join(',')}) VALUES (${values.join(',')});`;
        return await this.exec(sql);
    }

    async update(table, modify, where) {
        let set = [];
        for (let key of Object.keys(modify)) {
            set.push(`${key} = ${DatabaseConnection.escape(modify[key])}`);
        }
        let sql = `UPDATE ${table} SET ${set.join(', ')} ${DatabaseConnection.escapeConditions(where)};`;
        return await this.exec(sql);
    }

    async delete(table, where) {
        let sql = `DELETE FROM ${table} ${DatabaseConnection.escapeConditions(where)};`;
        return await this.exec(sql);
    }
}

const ContentType = {
    CT_NONE: 0,
    CT_APPLICATION_JSON: 1,
    CT_TEXT_PLAIN: 2,
    CT_TEXT_HTML: 3,
    CT_APPLICATION_X_FORM: 4,
    CT_APPLICATION_X_JAVASCRIPT: 5,
    CT_TEXT_CSS: 6,
    CT_TEXT_XML: 7,
    CT_APPLICATION_XML: 8,
    CT_TEXT_XSL: 9,
    CT_APPLICATION_WASM: 10,
    CT_APPLICATION_OCTET_STREAM: 11,
    CT_APPLICATION_X_FONT_TRUETYPE: 12,
    CT_APPLICATION_X_FONT_OPENTYPE: 13,
    CT_APPLICATION_FONT_WOFF: 14,
    CT_APPLICATION_FONT_WOFF2: 15,
    CT_APPLICATION_VND_MS_FONTOBJ: 16,
    CT_APPLICATION_PDF: 17,
    CT_IMAGE_SVG_XML: 18,
    CT_IMAGE_PNG: 19,
    CT_IMAGE_WEBP: 20,
};

function makeJSONResponse(data, status) {
    let response = new HTTPResponse();
    if (status) response.setStatusCode(status);
    response.setContentType(ContentType.CT_APPLICATION_JSON);
    response.setBody(JSON.stringify(data));
    return response;
}

function makeErrorResponse(data, status) {
    let response = new HTTPResponse();
    response.setStatusCode(status || 500);
    response.setBody("Error: " + data);
    return response;
}

function wrapRequest(request) {
    request.json = function () {
        return JSON.parse(this.body);
    };
    request.params = new Proxy({}, {
        get: (obj, name) => {
            if (obj[name] === undefined) {
                for (let coo of request.query.split('&')) {
                    let pos = coo.indexOf('=');
                    if (pos < 0) continue;
                    let key = coo.substr(0, pos).trimLeft();
                    let value = coo.substr(pos+1);
                    if (decodeURIComponent(key.replace(/\+/g, '%20')) == name) {
                        obj[name] = decodeURIComponent(value.replace(/\+/g, '%20'));
                        break;
                    }
                }
            }
            return obj[name];
        }
    });
    return request;
}

const LambdaRequests = {
    handlers: {},
    register: (type, path, handler) => {
        if (!LambdaRequests.handlers[type])
            LambdaRequests.handlers[type] = [];
        LambdaRequests.handlers[type].push([path, handler]);
    },
    get: (path, handler) => {
        LambdaRequests.register('GET', path, handler);
    },
    post: (path, handler) => {
        LambdaRequests.register('POST', path, handler);
    },
};

class HandledByServerException extends Error {}

function handleLambdaRequest(request) {
    function answerWithResult(request, result) {
        if (result) {
            if (result instanceof HTTPResponse) {
                request.respond(result);
            } else if (typeof (result) !== 'string') {
                request.respond(makeJSONResponse(result));
            } else {
                let response = new HTTPResponse();
                response.setContentType(ContentType.CT_TEXT_PLAIN);
                response.setBody(result);
                request.respond(response);
            }
        } else {
            let response = new HTTPResponse();
            response.setContentType(ContentType.CT_TEXT_PLAIN);
            response.setBody("");
            request.respond(response);
        }
    }

    let handler = null;
    let match = null;
    for (let [pattern, h] of (LambdaRequests.handlers[request.type] || [])) {
        match = pattern.exec(request.path);
        if (match) {
            handler = h;
            break;
        }
    }

    if (handler) {
        try {
            let result = handler(wrapRequest(request), match);
            if (result) {
                if (result.then) {
                    result.then((result) => {
                            answerWithResult(request, result);
                        },
                        (error) => {
                            request.respond(makeErrorResponse(error));
                        });
                } else {
                    answerWithResult(request, result);
                }
            }
        } catch (e) {
            if (e instanceof HandledByServerException)
                return false;
            request.respond(makeErrorResponse(e));
        }
        return true;
    } else {
        return false;
    }
}
