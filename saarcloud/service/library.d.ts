export declare function println(...args);
export declare function sha256(input: string): string;

export interface HTTPRequest {
    type: string;
    path: string;
    body: string;
    query: string;
    data: { [key: string]: string };
    cookies: { [key: string]: string };

    respond(response: HTTPResponse);

    json(): any;
    params: { [key: string]: string }
}

export interface HTTPResponse {
    setBody(body: string);

    setContentType(type: number);

    setStatusCode(code: number);
}

interface LambdaRequests {
    register(type: string, path: RegExp, handler: (request: HTTPRequest, pattern: RegExpExecArray) => any);

    get(path: RegExp, handler: (request: HTTPRequest, pattern: any) => any);

    post(path: RegExp, handler: (request: HTTPRequest, pattern: any) => any);
}

export declare const LambdaRequests: LambdaRequests;

export interface DatabaseConnection {
    static connect(name: string, token: string): Promise<DatabaseConnection>;

    exec(sql: string): Promise<Array>;

    select(table: string, where: object, options: object): Promise<Array>;

    insert(table: string, object: object): Promise<Array>;

    update(table: string, modify: object, where: object): Promise<Array>;

    delete(table: string, where: object): Promise<Array>;
}
