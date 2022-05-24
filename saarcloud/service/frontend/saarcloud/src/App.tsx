import React from 'react';
import './App.css';
import {HashRouter as Router, Route, Switch, NavLink} from 'react-router-dom';
import {SaarRDS, SaarRDSDB} from "./SaarRDS";
import {FeaturedSites, SaarCloudHeader} from "./Components";
import {Saar3, SaarAccessLogs, SaarLambda, SaarLambdaSite} from "./SaarSites";
import {Icon} from "semantic-ui-react";

function App() {
    return (
        <Router>
            <div className="ui four item menu inverted huge">
                <NavLink activeClassName="active" exact={true} className="item" to="/"><Icon name="cloud"/> Home</NavLink>
                <NavLink activeClassName="active" className="item" to="/saarrds"><Icon name="database"/> SaarRDS</NavLink>
                <NavLink activeClassName="active" className="item" to="/saarlambda"><Icon name="server"/> SaarLambda</NavLink>
                <NavLink activeClassName="active" className="item" to="/saar3"><Icon name="hdd"/> Saar3</NavLink>
            </div>

            <div className="ui container">
                <Switch>
                    <Route exact path="/saarrds"><SaarRDS/></Route>
                    <Route path="/saarrds/:dbname/:token" component={SaarRDSDB}/>
                    <Route exact path="/saarlambda"><SaarLambda/></Route>
                    <Route path="/sites/:sitename/:token/:log_token" component={SaarLambdaSite}/>
                    <Route path="/sites/:sitename/:token/" component={SaarLambdaSite}/>
                    <Route exact path="/saar3"><Saar3/></Route>
                    <Route path="/accesslogs/:sitename/:log_token" component={SaarAccessLogs}/>
                    <Route exact path="/"><Home/></Route>
                </Switch>
            </div>
        </Router>
    );
}

function Home() {
    return (
        <div className="App">
            <SaarCloudHeader icon="cloud"/>
            <div className="ui three column stackable grid">
                <div className="column">
                    <div className="ui card">
                        <div className="content">
                            <NavLink to="/saarrds" className="header">SaarRDS</NavLink>
                            <div className="meta">
                                Relational Databases as-a-service!
                            </div>
                            <div className="description">
                                SaarRDS is the leading solution for structured data.
                                Access your data with a common SQL interface, while we manage your databases.
                                SaarRDS is not only your preferred data storage, but also natively integrated with your SaarLambda sites.
                            </div>
                        </div>
                        <div className="extra content">
                            <NavLink to="/saarrds" className="ui primary button">Rent a database!</NavLink>
                        </div>
                    </div>
                </div>
                <div className="column">
                    <div className="ui card">
                        <div className="content">
                            <NavLink to="/saarlambda" className="header">SaarLambda</NavLink>
                            <div className="meta">
                                Server-less Computation as-a-service!
                            </div>
                            <div className="description">
                                SaarLambda is the leading solution for serverless services hosted in the cloud.
                                Write your website in a common language (Javascript), and we'll host it for you!
                            </div>
                        </div>
                        <div className="extra content">
                            <NavLink to="/saarlambda" className="ui primary button">Create your project!</NavLink>
                        </div>
                    </div>
                </div>
                <div className="column">
                    <div className="ui card">
                        <div className="content">
                            <NavLink to="/saar3" className="header">Saar3</NavLink>
                            <div className="meta">
                                Asset Hosting as-a-service!
                            </div>
                            <div className="description">
                                Saar3 is the leading content delivery network, hosting static content of any type for you.
                                Combined with SaarLambda and SaarRDS, you can build modern websites living entirely in the cloud.
                            </div>
                        </div>
                        <div className="extra content">
                            <NavLink to="/saar3" className="ui primary button">Register now!</NavLink>
                        </div>
                    </div>
                </div>
            </div>

            <br/><br/>
            <h2 className="ui center aligned header">See what our customers say!</h2>
            <div className="ui segment">
                <FeaturedSites/>
            </div>
            <br/><br/>
        </div>
    );
}

export default App;
