import React from "react";
import {NavLink, Redirect} from "react-router-dom";
import {Button, Form, Label, Message} from "semantic-ui-react";
import {FeaturedSites, SaarCloudHeader} from "./Components";
import {Backend} from "./backends";
import {RouteComponentProps} from "react-router";
import {SemanticICONS} from "semantic-ui-react/dist/commonjs/generic";

type LambdaLoginState = {
    redirect?: string;
    error?: string;
}

export class SaarLambda extends React.Component<{}, LambdaLoginState> {
    title = 'SaarLambda';
    subtitle = 'Your saarländisch serverless hosting provider';
    type = 'lambda';
    icon: SemanticICONS = 'server';

    login = async (e: React.SyntheticEvent) => {
        e.preventDefault();
        this.setState({error: ""});
        const target = e.target as typeof e.target & {
            sitename: { value: string };
            token: { value: string };
        };
        try {
            if (await Backend.lambda_check(target.sitename.value, target.token.value)) {
                this.setState({redirect: `/sites/${target.sitename.value}/${target.token.value}/`});
            } else {
                this.setState({error: "Invalid credentials"});
            }
        } catch (e) {
            console.error(e);
            this.setState({error: e + ""});
        }
    }

    register = async (e: React.SyntheticEvent) => {
        e.preventDefault();
        this.setState({error: ""});
        const target = e.target as typeof e.target & {
            sitename: { value: string };
        };
        try {
            let {sitename, token, log_token} = await Backend.lambda_register(target.sitename.value);
            this.setState({redirect: `/sites/${sitename}/${token}/${log_token}`});
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
                <SaarCloudHeader title={this.title} subtitle={this.subtitle} icon={this.icon}/>

                {errormessage}

                <div className="ui two column stackable grid">
                    <div className="column">
                        <div className="ui fluid card">
                            <div className="content">
                                <span className="header">Login</span>
                                <Form className="description" onSubmit={this.login}>
                                    <Form.Field>
                                        <label>Your Site Name</label>
                                        <input name="sitename" placeholder="sitename"/>
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
                                <span className="header">Register Site</span>
                                <Form className="description" onSubmit={this.register}>
                                    <Form.Field>
                                        <label>Your Site Name</label>
                                        <input name="sitename" placeholder="site name"/>
                                    </Form.Field>
                                    <Button type="submit" className="ui primary button">Register</Button>
                                </Form>
                                <div className="ui message">Your registration will be valid for both SaarLambda and Saar3!</div>
                            </div>
                        </div>
                    </div>
                </div>

                <br/><br/>
                <h2 className="ui center aligned header">See what our customers say!</h2>
                <div className="ui segment">
                    <FeaturedSites type={this.type}/>
                </div>
                <br/><br/>
            </div>
        );
    }
}


type SaarLambdaSiteState = {
    error?: string;
    ok?: string;
};

export class SaarLambdaSite extends React.Component<RouteComponentProps<{ sitename: string, token: string, log_token: string }>, SaarLambdaSiteState> {
    constructor(props: any) {
        super(props);
        this.state = {};
    }

    uploadLambdaScript = async (e: React.SyntheticEvent) => {
        e.preventDefault();
        this.setState({error: "", ok: ""});
        const target = e.target as typeof e.target & {
            file: { files: File[] };
        };
        try {
            await Backend.lambda_write(this.props.match.params.sitename, this.props.match.params.token, target.file.files[0]);
            this.setState({error: "", ok: "Lambda script successfully uploaded"});
        } catch (e) {
            console.error(e);
            this.setState({error: e + "", ok: ""});
        }
    }

    uploadSaar3File = async (e: React.SyntheticEvent) => {
        e.preventDefault();
        this.setState({error: "", ok: ""});
        const target = e.target as typeof e.target & {
            file: { files: File[] };
            filename: { value: string };
        };
        try {
            await Backend.saar3_write(this.props.match.params.sitename, this.props.match.params.token, target.filename.value, target.file.files[0]);
            this.setState({error: "", ok: "File successfully uploaded to Saar3 CDN"});
        } catch (e) {
            console.error(e);
            this.setState({error: e + "", ok: ""});
        }
    }

    submitLogToken = async (e: React.SyntheticEvent) => {
        e.preventDefault();
        const target = e.target as typeof e.target & {
            log_token: { value: string };
        };
        this.props.match.params.log_token = target.log_token.value;
        this.setState({});
    }

    render() {
        let errormessage: any = "";
        if (this.state && this.state.error) {
            errormessage = <Message error={true}>{this.state.error}</Message>;
        }
        let okmessage: any = "";
        if (this.state && this.state.ok) {
            okmessage = <Message success={true}>{this.state.ok}</Message>;
        }

        const logurl = window.location.origin + "/logs?user=" + encodeURIComponent(this.props.match.params.sitename) + "&token=" + encodeURIComponent(this.props.match.params.log_token);
        let baseUrl = window.location.hostname === 'localhost' ? '127.0.0.1' : window.location.hostname;
        if (baseUrl.match(/\d+\.\d+\.\d+\.\d+/)) {
            baseUrl += '.nip.io';
        }
        if (window.location.port && window.location.port !== "80") {
            baseUrl += ':' + window.location.port;
        }
        baseUrl = "http://" + this.props.match.params.sitename + "." + baseUrl + "/";

        return <div>
            <SaarCloudHeader title="SaarLambda & Saar3" subtitle="Your saarländisch serverless cloud hosting & content delivery network"/>
            <h3 className="ui center aligned header">Site &quot;{this.props.match.params.sitename}&quot;</h3>

            <div className="ui segment">
                <form className="ui form">
                    <div className="field">
                        <label>Your Site Name / URL:</label>
                        <input readOnly className="monospace" value={this.props.match.params.sitename}/>
                    </div>
                    <div className="field">
                        <a href={baseUrl} target="_blank" rel="noreferrer">{baseUrl}</a>
                    </div>
                    <div className="field">
                        <label>Your Token (please save):</label>
                        <input readOnly className="monospace" value={this.props.match.params.token}/>
                    </div>
                    {this.props.match.params.log_token &&
                    <div className="field">
                        <label>Your Access Log Token (please save):</label>
                        <input readOnly className="monospace" value={this.props.match.params.log_token}/>
                    </div>
                    }
                    {this.props.match.params.log_token &&
                    <div className="field">
                        <label>Access log endpoint:</label>
                        <input readOnly className="monospace" value={logurl}/>
                    </div>
                    }
                    {this.props.match.params.log_token &&
                    <div className="field">
                        <NavLink to={"/accesslogs/" + this.props.match.params.sitename + "/" + this.props.match.params.log_token}>See Access Logs in real-time</NavLink>
                    </div>
                    }
                </form>
            </div>

            {!this.props.match.params.log_token && <div className="ui segment">
                <form className="ui form" onSubmit={this.submitLogToken}>
                    <div className="field">
                        <label>Your Access Log Token:</label>
                        <input name="log_token" className="monospace" placeholder="Please enter your log token"/>
                    </div>
                    <button className="ui button primary" type="submit">Submit</button>
                </form>
            </div>}

            <br/>{errormessage}{okmessage}<br/>
            <div className="ui segment">
                <h3 className="ui center aligned header">Upload SaarLambda Script</h3>
                <p>Upload a javascript file that will later respond to requests to your site.</p>
                <form className="ui form" onSubmit={this.uploadLambdaScript}>
                    <Form.Field>
                        <input type="file" name="file"/>
                    </Form.Field>
                    <button className="ui button primary" type="submit">Upload!</button>
                </form>
            </div>

            <br/><br/>

            <div className="ui segment">
                <h3 className="ui center aligned header">Upload Saar3 File</h3>
                <p>Upload static files that will be served whenever your SaarLambda script does not respond.</p>
                <form className="ui form" onSubmit={this.uploadSaar3File}>
                    <Form.Field>
                        <label>Filename</label>
                        <div className="ui labeled input">
                            <div className="ui label">{baseUrl}</div>
                            <input type="text" name="filename" minLength={3} maxLength={64}/>
                        </div>
                    </Form.Field>
                    <Form.Field>
                        <input type="file" name="file"/>
                    </Form.Field>
                    <button className="ui button primary" type="submit">Upload!</button>
                </form>
            </div>

            <br/>
        </div>;
    }
}





export class Saar3 extends SaarLambda{
    title = 'Saar3';
    subtitle = 'Your saarländisch content delivery network';
    type = 'cdn';
    icon: SemanticICONS = 'hdd';
}


type SaarAccessLogsState = {
    logs?: string[];
    error?: string;
    connected?: boolean;
};

export class SaarAccessLogs extends React.Component<RouteComponentProps<{ sitename: string, log_token: string }>, SaarAccessLogsState> {
    private socket: WebSocket|null = null;

    constructor(props: any) {
        super(props);
        this.state = {logs: [], connected: false};
    }

    componentDidMount() {
        let url = window.location.origin.replace('http://', 'ws://') + '/logs';
        url += '?user=' + encodeURIComponent(this.props.match.params.sitename);
        url += '&token=' + encodeURIComponent(this.props.match.params.log_token);
        this.socket = new WebSocket(url);
        this.socket.onmessage = (event) => {
            let date = new Date().toLocaleString();
            this.setState((oldState, _) => {
                return {logs: [...oldState.logs!!, date + " | " + event.data]};
            });
        };
        this.socket.onerror = (error) => {
            console.log("ERROR", error);
        }
        this.socket.onclose = (event) => {
            this.setState({connected: false});
        };
        this.socket.onopen = (event) => {
            this.setState({connected: true});
        }
    }

    componentWillUnmount() {
        this.socket?.close();
    }

    render() {
        console.log(this.state);
        return (<div>
            <SaarCloudHeader title="SaarLambda & Saar3" subtitle={"Access Logs - " + this.props.match.params.sitename}/>

            <p>Access log entries for site <code>{this.props.match.params.sitename}</code> will appear here in real time.</p>
            <div className="ui segment">
                <div className="ui list">
                    {this.state.logs?.map(log => <div className="item"><code>{log}</code></div>)}
                </div>
            </div>
            <br/>
            {this.state.connected && <Label className="ui green label"><div className="ui active mini inline inverted indeterminate loader"/>&nbsp;connected</Label>}
            {!this.state.connected && <Label>disconnected</Label>}
        </div>);
    }
}