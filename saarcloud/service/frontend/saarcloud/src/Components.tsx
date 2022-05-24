import React from "react";
import {Backend, FeaturedSite} from "./backends";
import {Icon} from "semantic-ui-react";
import {SemanticICONS} from "semantic-ui-react/dist/commonjs/generic";

export function SaarCloudHeader(props: { title?: string, subtitle?: string, icon?: SemanticICONS }) {
    return (<div>
        <h1 className="ui center aligned header">{props.icon && <Icon name={props.icon}/>} {props.title || 'SaarCloud'}</h1>
        <h2 className="ui center aligned header">{props.subtitle || 'Hosting on saarländisch clouds'}</h2>
    </div>);
}

const CompanyIcons = ['wechat', 'korvue', 'leanpub', 'lastfm', 'viadeo square', 'apple', 'strava', 'blogger b', 'stack exchange', 'yelp', 'studiovinari', 'youtube square', 'get pocket', 'js square', 'telegram plane', 'algolia', 'empire', 'themeisle', 'modx', 'rocketchat', 'pied piper alternate', 'vimeo v', 'youtube', 'gulp', 'npm', 'deviantart', 'cc visa', 'node', 'dropbox', 'dribbble', 'codiepie', 'mizuni', 'gg', 'git square', 'drupal', 'digg', 'vimeo square', 'hips', 'behance square', 'angellist', 'gofore', 'hotjar', 'telegram', 'amilia', 'glide g', 'facebook', 'ember', 'android', 'angrycreative', 'blackberry', 'aviato', 'adversal', 'cc apple pay', 'mix', 'js', 'pied piper', 'css3', 'sass', 'wpexplorer', 'steam', 'freebsd', 'laravel', 'medapps', 'medium', 'cc stripe', 'superpowers', 'contao', 'fonticons', 'opencart', 'weixin', 'font awesome', 'microsoft', 'osi', 'slack', 'buromobelexperte', 'periscope', 'flipboard', 'affiliatetheme', 'cc jcb', 'mixcloud', 'twitch', 'product hunt', 'behance', 'uikit', 'whmcs', 'slack hash', 'btc', 'audible', 'expeditedssl', 'typo3', 'tumblr square', 'fort awesome', 'earlybirds', '500px', 'erlang', 'cpanel', 'houzz', 'fort awesome alternate', 'firefox', 'hacker news square', 'hooli', 'app store ios', 'flickr', 'vine', 'deskpro', 'sellsy', 'playstation', 'reddit', 'accusoft', 'viber', 'html5', 'whatsapp', 'google plus g', 'gratipay', 'facebook messenger', 'shirtsinbulk', 'envira', 'blogger', 'patreon', 'jenkins', 'bimobject', 'css3 alternate', 'renren', 'pushed', 'vk', 'wordpress simple', 'gitkraken', 'python', 'wpforms', 'cc paypal', 'php', 'palfed', 'slideshare', 'react', 'dribbble square', 'google', 'tumblr', 'autoprefixer', 'linode', 'y combinator', 'snapchat ghost', 'viadeo', 'ns8', 'viacoin', 'deploydog', 'google drive', 'google plus', 'gitter', 'adn', 'linux', 'paypal', 'imdb', 'edge', 'yahoo', 'reddit square', 'stumbleupon circle', 'github alternate', 'font awesome flag', 'node js', 'skyatlas', 'tencent weibo', 'xing', 'whatsapp square', 'staylinked', 'creative commons', 'scribd', 'gripfire', 'delicious', 'cloudsmith', 'twitter square', 'maxcdn', 'wikipedia w', 'apper', 'foursquare', 'yandex', 'vnv', 'phabricator', 'xbox', 'bitbucket', 'rockrms', 'phoenix framework', 'git', 'tripadvisor', 'bitcoin', 'lyft', 'gitlab', 'hire a helper', 'app store', 'weibo', 'facebook f', 'stripe s', 'napster', 'resolving', 'bandcamp', 'buysellads', 'discord', 'cloudversify', 'sellcast', 'joomla', 'grunt', 'dyalog', 'odnoklassniki', 'servicestack', 'bluetooth', 'bity', 'steam square', 'avianex', 'internet explorer', 'google wallet', 'twitter', 'first order', 'sistrix', 'supple', 'nutritionix', 'page4', 'reddit alien', 'vuejs', 'keycdn', 'itunes note', 'pied piper pp', 'black tie', 'dashcube', 'ravelry', 'simplybuilt', 'draft2digital', 'elementor', 'lastfm square', 'pagelines', 'steam symbol', 'uber', 'github square', 'etsy', 'soundcloud', 'yandex international', 'uniregistry', 'fly', 'opera', 'openid', 'bluetooth b', 'google play', 'jsfiddle', 'stumbleupon', 'font awesome alternate', 'linkedin', 'vaadin', 'asymmetrik', 'goodreads', 'free code camp', 'angular', 'kickstarter k', 'forumbee', 'qq', 'schlix', 'optin monster', 'rebel', 'cc diners club', 'replyd', 'stripe', 'searchengin', 'hacker news', 'itunes', 'quora', 'docker', 'ioxhost', 'meetup', 'untappd', 'cc discover', 'pinterest p', 'wpbeginner', 'ussunnah', 'vimeo', 'hubspot', 'd and d', 'pinterest', 'kickstarter', 'skype', 'joget', 'quinscape', 'rendact', 'instagram', 'glide', 'monero', 'windows', 'github', 'medrt', 'cloudscale', 'cc mastercard', 'linechat', 'xing square', 'dochub', 'sticker mule', 'digital ocean', 'google plus square', 'nintendo switch', 'trello', 'speakap', 'usb', 'safari', 'cc amazon pay', 'redriver', 'odnoklassniki square', 'codepen', 'chrome', 'apple pay', 'medium m', 'yoast', 'cc amex', 'pinterest square', 'grav', 'linkedin alternate', 'amazon pay', 'cuttlefish', 'discourse', 'snapchat square', 'accessible icon', 'less', 'firstdraft', 'gg circle', 'spotify', 'wordpress', 'magento', 'stack overflow', 'ethereum', 'goodreads g', 'connectdevelop', 'facebook square', 'amazon', 'fonticons fi', 'centercode', 'aws', 'snapchat'];
const CompanyColors = ['black', 'teal', 'violet', 'grey', 'black', 'violet', 'olive', 'black', 'red', 'teal', 'purple', 'blue', 'brown', 'pink', 'purple', 'black', 'black', 'brown', 'blue', 'blue', 'black', 'pink', 'red', 'black', 'orange', 'black', 'purple', 'green', 'brown', 'violet', 'green', 'red', 'purple', 'blue', 'brown', 'purple', 'pink', 'brown', 'violet', 'black', 'black', 'olive', 'black', 'green', 'red', 'grey', 'olive', 'green', 'yellow', 'black', 'black', 'grey', 'violet', 'black', 'yellow', 'orange', 'yellow', 'black', 'black', 'brown', 'violet', 'purple', 'orange', 'red', 'violet', 'blue', 'black', 'blue', 'teal', 'green', 'violet', 'green', 'black', 'violet', 'red'];
const CompanySuggestions = [
    '10/10 would buy again',
    'SaarCloud finally delivers the performance and security we need for our business',
    'By choosing SaarCloud as our preferred cloud provider, we improved our productivity by 20%',
    'We built our main platform on SaarCloud, getting rid of our in-house data center',
    'After migration to SaarCloud, our IT costs dropped by 200%',
    'Using SaarCloud, we provide secure and reliable remote access to our employees',
    'To meet the demands of an increasingly cloud-centric market, we rely on SaarCloud for our IT',
    'We use optimized SaarCloud infrastructure, saving $25,000 monthly',
    'We deliver our SaaS solution from the world\'s leading cloud platform',
    'To deliver modern, API-driven solutions to our customers, we have chosen SaarCloud as our technology partner',
    'By using SaarCloud storage and computation services, we could save 80% on the cost of our IT operations',
    'Combining artificial intelligence, blockchain and SaarCloud, we will soon be your leading partner for world domination',
    'SaarCloud provides an incredible level of scalability',
    'We migrated our legacy on-premise system to dynamic, serverless hosting by SaarCloud, reducing costs and doubling innovation speed',
    'We increased productivity and streamlined inventory management by building an integrated inventory management application on SaarCloud',
    'By developing a powerful pipeline on SaarCloud, we provide our service 20x faster than traditional methods',
    'SaarCloud powers our business for years now',
    'By migrating to the cloud, we achived 20% annual growth',
];
const Features: any = {
    rds: "SaarRDS",
    lambda: "SaarLambda",
    cdn: "Saar3"
}

type FeaturedState = {
    sites: FeaturedSite[];
};

export class FeaturedSites extends React.Component<{type?: string}, FeaturedState> {
    private baseUrl: string;

    constructor(props: any) {
        super(props);
        this.state = {sites: []};
        this.baseUrl = window.location.hostname === 'localhost' ? '127.1.0.1' : window.location.hostname;
        if (this.baseUrl.match(/\d+\.\d+\.\d+\.\d+/)) {
            this.baseUrl += '.nip.io';
        }
        if (window.location.port && window.location.port !== "80") {
            this.baseUrl += ':' + window.location.port;
        }
    }

    componentDidMount() {
        Backend.get_featured().then(result => {
            let data: FeaturedSite[] = this.props.type ? (result as any)[this.props.type] : [...result.rds, ...result.lambda, ...result.cdn];
            data.sort((a, b) => b.id - a.id);
            this.setState({sites: data});
        });
    }

    urlOfSite(name: string): string {
        return "http://" + name + "." + this.baseUrl + "/";
    }

    render() {
        return <div className="ui relaxed divided list">
            {this.state.sites.map(site => <div className="item">
                <i className={"large middle aligned icon " + CompanyIcons[site.id % CompanyIcons.length] + ' ' + CompanyColors[site.id % CompanyColors.length]}/>
                <div className="content">
                    <span className="header">
                        <a href={this.urlOfSite(site.name)} target="_blank" rel="noreferrer">{site.name}</a>
                        <span style={{fontWeight: "normal"}}> uses </span>
                        {Features[site.feature]}
                    </span>
                    <div className="description">{CompanySuggestions[site.id % CompanySuggestions.length]}</div>
                </div>
            </div>)}
        </div>;
    }
}
