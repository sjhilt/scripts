#####################################################
# Script to pull the history of an IP address via
# the shodan API. This just dumps out the raw JSON
#  Author: Stephen Hilt
#####################################################
import shodan
import sys
import click
import os


SHODAN_CONFIG_DIR = '~/.shodan/'

def get_api_key():
    shodan_dir = os.path.expanduser(SHODAN_CONFIG_DIR)
    keyfile = shodan_dir + '/api_key'
    
    # If the file doesn't yet exist let the user know that they need to
    # initialize the shodan cli
    if not os.path.exists(keyfile):
        raise click.ClickException('Please run "shodan init <api key>" before using this command')
    
    # Make sure it is a read-only file
    os.chmod(keyfile, 0o600)

    with open(keyfile, 'r') as fin:
        return fin.read().strip()

    raise click.ClickException('Please run "shodan init <api key>" before using this command')


# Make this your API Key from accounts.shodan.io
API_KEY = get_api_key()
#API_KEY = "YOUR KEY HERE"

# Input validation for one argument (IP address)
if len(sys.argv) == 1:
	print 'Usage: %s <host>' % sys.argv[0]
	sys.exit(1)
try:
  # Pull the first argument for the IP address 
  # to look up the history of
	ip = sys.argv[1] 
	# Setup the API to communicate to
	api = shodan.Shodan(API_KEY)
	# pull the information about the host, and the history 
	# this is done by setting the history to True
	host = api.host(ip, history=True)
	# Display raw results, this is where more parsing 
	# could be done depending on your output needs
        # General info
        click.echo(click.style(ip, fg='green'))
        if len(host['hostnames']) > 0:
            click.echo('{:25s}{}'.format('Hostnames:', ';'.join(host['hostnames'])))

        if 'city' in host and host['city']:
            click.echo('{:25s}{}'.format('City:', host['city']))

        if 'country_name' in host and host['country_name']:
            click.echo('{:25s}{}'.format('Country:', host['country_name']))

        if 'os' in host and host['os']:
            click.echo('{:25s}{}'.format('Operating System:', host['os']))

        if 'org' in host and host['org']:
            click.echo('{:25s}{}'.format('Organization:', host['org']))

        click.echo('{:25s}{}'.format('Number of open ports:', len(host['ports'])))

        # Output the vulnerabilities the host has
        if 'vulns' in host and len(host['vulns']) > 0:
            vulns = []
            for vuln in host['vulns']:
                if vuln.startswith('!'):
                    continue
                if vuln.upper() == 'CVE-2014-0160':
                    vulns.append(click.style('Heartbleed', fg='red'))
                else:
                    vulns.append(click.style(vuln, fg='red'))

            if len(vulns) > 0:
                click.echo('{:25s}'.format('Vulnerabilities:'), nl=False)

                for vuln in vulns:
                    click.echo(vuln + '\t', nl=False)

                click.echo('')

        click.echo('')

        click.echo('Ports:')
        for banner in sorted(host['data'], key=lambda k: k['port']):
            product = ''
            version = ''
            if 'product' in banner:
                product = banner['product']
            if 'version' in banner:
                version = '({})'.format(banner['version'])

            click.echo(click.style('{:>7d} '.format(banner['port']), fg='cyan'), nl=False)
            click.echo("{} {} {}".format(banner['timestamp'], banner.get('product', ''), version))

            if 'ssl' in banner:
                if 'versions' in banner['ssl']:
                    click.echo('\t|-- SSL Versions: {}'.format(', '.join([version for version in sorted(banner['ssl']['versions']) if not version.startswith('-')])))
                if 'dhparams' in banner['ssl']:
                    click.echo('\t|-- Diffie-Hellman Parameters:')
                    click.echo('\t\t{:15s}{}\n\t\t{:15s}{}'.format('Bits:', banner['ssl']['dhparams']['bits'], 'Generator:', banner['ssl']['dhparams']['generator']))
                    if 'fingerprint' in banner['ssl']['dhparams']:
                        click.echo('\t\t{:15s}{}'.format('Fingerprint:', banner['ssl']['dhparams']['fingerprint']))
            start = banner['data'].find('Fingerprint: ')
            if start > 0:
                start += len('Fingerprint: ')
                fingerprint = banner['data'][start:start+47]
                click.echo('\t|--\n\t|-- SSH Fingerprint: {}'.format(fingerprint))


except Exception, e:
    print 'Error: %s' % e
    sys.exit(1)
