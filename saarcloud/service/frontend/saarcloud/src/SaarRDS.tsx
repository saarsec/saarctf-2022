import React from "react";
import {Backend} from "./backends";
import {Redirect} from "react-router-dom";
import {Button, Form, Message} from "semantic-ui-react";
import {RouteComponentProps} from "react-router";
import {FeaturedSites, SaarCloudHeader} from "./Components";

type RDSLoginState = {
    redirect?: string;
    error?: string;
}

export class SaarRDS extends React.Component<{}, RDSLoginState> {
    login = async (e: React.SyntheticEvent) => {
        e.preventDefault();
        this.setState({error: ""});
        const target = e.target as typeof e.target & {
            dbname: { value: string };
            token: { value: string };
        };
        try {
            await Backend.rds_exec(target.dbname.value, target.token.value, 'SELECT 1;');
            this.setState({redirect: `/saarrds/${target.dbname.value}/${target.token.value}`});
        } catch (e) {
            console.error(e);
            this.setState({error: e + ""});
        }
    }

    register = async (e: React.SyntheticEvent) => {
        e.preventDefault();
        this.setState({error: ""});
        const target = e.target as typeof e.target & {
            dbname: { value: string };
        };
        try {
            let {dbname, token} = await Backend.rds_register(target.dbname.value);
            this.setState({redirect: `/saarrds/${dbname}/${token}`});
        } catch (e) {
            console.error(e);
            this.setState({error: e + ""});
        }
    }

    render() {
        if (this.state && this.state.redirect) {
            return <Redirect to={this.state.redirect}/>
        }
        let errormessage: any = "";
        if (this.state && this.state.error) {
            errormessage = <Message error={true}>{this.state.error}</Message>;
        }
        return (
            <div>
                <SaarCloudHeader title="SaarRDS" subtitle="Your saarländisch relational database system in the cloud" icon="database"/>

                {errormessage}

                <div className="ui two column stackable grid">
                    <div className="column">
                        <div className="ui fluid card">
                            <div className="content">
                                <span className="header">Connect to Database</span>
                                <Form className="description" onSubmit={this.login}>
                                    <Form.Field>
                                        <label>Your SaarRDS Database Name</label>
                                        <input name="dbname" placeholder="database name"/>
                                    </Form.Field>
                                    <Form.Field>
                                        <label>Your Access Token</label>
                                        <input name="token" type="password"/>
                                    </Form.Field>
                                    <Button type="submit" className="ui primary button">Login</Button>
                                </Form>
                            </div>
                        </div>
                    </div>

                    <div className="column">
                        <div className="ui fluid card">
                            <div className="content">
                                <span className="header">Create Database</span>
                                <Form className="description" onSubmit={this.register}>
                                    <Form.Field>
                                        <label>Your SaarRDS Database Name</label>
                                        <input name="dbname" placeholder="database name"/>
                                    </Form.Field>
                                    <Button type="submit" className="ui primary button">Register</Button>
                                </Form>
                            </div>
                        </div>
                    </div>
                </div>

                <br/><br/>
                <h2 className="ui center aligned header">See what our customers say!</h2>
                <div className="ui segment">
                    <FeaturedSites type="rds"/>
                </div>
                <br/><br/>
            </div>
        );
    }
}

type SaarRDSDBState = {
    tables?: { name: string; type: string; }[];
    error?: string;
    data?: any[] | null;
    sql?: string;
}

export class SaarRDSDB extends React.Component<RouteComponentProps<{ dbname: string, token: string }>, SaarRDSDBState> {
    constructor(props: any) {
        super(props);
        this.state = {tables: [], data: null, error: "", sql: ""};
    }

    componentDidMount() {
        Backend.rds_exec(this.props.match.params.dbname, this.props.match.params.token, "SELECT * FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'").then(result => {
            console.log(result);
            this.setState({tables: result});
        });
    }

    sqlexec = async (e: React.SyntheticEvent) => {
        e.preventDefault();
        await this.runsql(this.state.sql as string);
    }

    runsql = async(sql: string) => {
        this.setState({error: ""});
        try {
            let data = await Backend.rds_exec(this.props.match.params.dbname, this.props.match.params.token, sql);
            this.setState({data: data});
        } catch (e) {
            console.error(e);
            this.setState({error: e + ""});
        }
    }

    select = async (tblname: string) => {
        this.setState({sql: "SELECT * FROM " + tblname});
        await this.runsql("SELECT * FROM " + tblname);
    }

    render() {
        let errormessage: any = "";
        if (this.state && this.state.error) {
            errormessage = <Message error={true}>{this.state.error}</Message>;
        }
        let data: any = "";
        if (this.state.data !== null) {
            if (this.state.data?.length) {
                let headers = Object.keys(this.state.data[0]);
                data = <table className="ui celled table">
                    <thead><tr>{headers.map(k => <th>{k}</th>)}</tr></thead>
                    <tbody>
                    {this.state.data.map(line => <tr>{headers.map(k => <td>{line[k] === null ? <i>NULL</i> : line[k]}</td>)}</tr>)}
                    </tbody>
                </table>
            } else {
                data = <i>0 rows returned</i>;
            }
        }
        const apibase = window.location.origin + "/api/rds/" + this.props.match.params.dbname;
        const apisuffix = "?token=" + encodeURIComponent(this.props.match.params.token);

        return (<div>
            <SaarCloudHeader title="SaarRDS" subtitle="Your saarländisch relational database system in the cloud" icon="database"/>
            <h3 className="ui center aligned header">Database &quot;{this.props.match.params.dbname}&quot;</h3>

            <div className="ui segment">
                <form className="ui form">
                    <div className="field">
                        <label>Your Database Name:</label>
                        <input readOnly className="monospace" value={this.props.match.params.dbname}/>
                    </div>
                    <div className="field">
                        <label>Your Access Token (please save):</label>
                        <input readOnly className="monospace" value={this.props.match.params.token}/>
                    </div>

                    <div className="field">
                        <label>API endpoints:</label>
                        <input readOnly className="monospace" value={"POST " + apibase + apisuffix}/>
                        <input readOnly className="monospace" value={"GET " + apibase + "/<table>/select" + apisuffix}/>
                        <input readOnly className="monospace" value={"POST " + apibase + "/<table>/insert" + apisuffix}/>
                        <input readOnly className="monospace" value={"POST " + apibase + "/<table>/update" + apisuffix}/>
                        <input readOnly className="monospace" value={"POST " + apibase + "/<table>/delete" + apisuffix}/>
                    </div>
                </form>
            </div>
            <br/>
            <br/>

            {this.state.tables &&
            <div>
                <h3 className="ui center aligned header">Database Content</h3>
                <ul>
                    {this.state.tables.map(tbl => <li>{tbl.type}: <code>{tbl.name}</code> {tbl.type === 'table'
                        ? <button className="ui primary tertiary button" onClick={() => this.select(tbl.name)}>(see content)</button>
                        : ''}</li>)}
                    {!this.state.tables.length && <i>This database is empty. Create some tables with the SQL interface below!</i>}
                </ul>
                <br/>
                <br/>
            </div>
            }

            <div>
                <h3 className="ui center aligned header">Execute Queries</h3>
                <form className="ui form" onSubmit={this.sqlexec}>
                    <div className="field">
                        <label>SQL</label>
                        <input type="text" name="sql" placeholder="SELECT 1" value={this.state.sql} onChange={(e) => {this.setState({sql: e.target.value })}} />
                    </div>
                    <button className="ui button primary" type="submit">Execute!</button>
                </form>
                {errormessage}{data}
            </div>
            <br/>
        </div>);
    }
}