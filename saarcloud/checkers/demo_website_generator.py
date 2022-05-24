import sys

try:
    from .website_generator import gen_website_cdn, gen_website_lambda, gen_website_rds, SaarCloudSession, fill_rds_site_with_demo_data, set_demo_site
except ImportError:
    from website_generator import gen_website_cdn, gen_website_lambda, gen_website_rds, SaarCloudSession, fill_rds_site_with_demo_data, set_demo_site


class Team:
    def __init__(self, ip):
        self.ip = ip


def main():
    set_demo_site()
    team = Team(sys.argv[1])
    session = SaarCloudSession(team)

    website = gen_website_cdn('demo1', 'SAAR{demo1}', 1337)
    response = session.post('/api/register/cdn', json={'username': website.username})
    token = response.json()['token']
    session.upload_cdn_files(website, token)
    session.post('/api/feature', json={'username': website.username, 'feature': 'cdn'})
    print('Stored demo1')

    website = gen_website_lambda('demo2', 'SAAR{demo2}', 1337)
    response = session.post('/api/register/lambda', json={'username': website.username})
    token = response.json()['token']
    session.upload_lambda_script(website, token)
    session.upload_cdn_files(website, token)
    session.post('/api/feature', json={'username': website.username, 'feature': 'lambda'})
    print('Stored demo2')

    website = gen_website_rds('demo3', 'SAAR{demo3}', 1337)
    response = session.post('/api/register/rds', json={'username': website.rds_name})
    token1 = response.json()['token']
    website.lambda_script = website.lambda_script.replace('<dbtoken>', token1)
    session.upload_rds_sql(website, token1)
    response = session.post('/api/register/lambda', json={'username': website.username})
    token2 = response.json()['token']
    session.upload_lambda_script(website, token2)
    session.upload_cdn_files(website, token2)
    fill_rds_site_with_demo_data(SaarCloudSession(team, 'demo3'), website)
    session.post('/api/feature', json={'username': website.username, 'feature': 'rds'})
    print('Stored demo3')


if __name__ == '__main__':
    main()
