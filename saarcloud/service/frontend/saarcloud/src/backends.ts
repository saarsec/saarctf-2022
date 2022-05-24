export interface FeaturedSite {
    id: number;
    ts: any;
    name: string;
    feature: string;
}

export class BackendImpl {
    private base: string;

    constructor() {
        this.base = window.location.origin + '/api/';
    }

    async rds_register(dbname: string): Promise<{ dbname: string, token: string }> {
        let response = await fetch(this.base + 'register/rds', {method: 'POST', body: JSON.stringify({username: dbname})});
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(await response.text());
        }
    }

    async rds_exec(dbname: string, token: string, sql: string) {
        let url = this.base + `rds/${dbname}?token=${encodeURIComponent(token)}`;
        let response = await fetch(url, {method: 'POST', body: sql});
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(await response.text());
        }
    }

    async rds_select(dbname: string, token: string, table: string) {
        let url = this.base + `rds/${dbname}/${table}/select?token=${encodeURIComponent(token)}`;
        let response = await fetch(url);
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(await response.text());
        }
    }

    async lambda_register(sitename: string): Promise<{ sitename: string, token: string, log_token: string }> {
        let response = await fetch(this.base + 'register/lambda', {method: 'POST', body: JSON.stringify({username: sitename})});
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(await response.text());
        }
    }

    async lambda_check(sitename: string, token: string): Promise<boolean> {
        let response = await fetch(this.base + 'lambda/check/'+sitename+"?token="+encodeURIComponent(token), {method: 'POST'});
        if (response.ok) {
            return (await response.json())['ok'];
        } else {
            throw new Error(await response.text());
        }
    }

    async lambda_write(sitename: string, token: string, file: string|File): Promise<{ok: boolean}> {
        let response = await fetch(this.base + 'lambda/write/'+sitename+"?token="+encodeURIComponent(token),
            {method: 'POST', body: file, headers: {'Content-Type': 'text/javascript'}});
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(await response.text());
        }
    }

    async saar3_write(sitename: string, token: string, filename: string, file: string|File): Promise<{ok: boolean}> {
        let response = await fetch(this.base + 'cdn/write/'+sitename+"/"+encodeURIComponent(filename)+"?token="+encodeURIComponent(token),
            {method: 'POST', body: file, headers: {'Content-Type': 'text/javascript'}});
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(await response.text());
        }
    }

    private featureCache?: {rds: FeaturedSite[], lambda: FeaturedSite[], cdn: FeaturedSite[]};

    async get_featured(): Promise<{rds: FeaturedSite[], lambda: FeaturedSite[], cdn: FeaturedSite[]}> {
        if (this.featureCache)
            return this.featureCache;
        let response = await fetch(this.base + 'featured');
        if (response.ok) {
            return this.featureCache = await response.json();
        } else {
            throw new Error(await response.text());
        }
    }
}

export const Backend = new BackendImpl();
