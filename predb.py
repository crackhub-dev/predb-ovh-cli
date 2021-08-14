from os import link
import requests as r
import json
import click
import urllib.parse
import time
from dl import download
from bs4 import BeautifulSoup
from dateutil import parser


__author__ = "crackhub213"

@click.group()
def main():
    """
    PreDB.ovh CLI Interface
    """
    pass

@main.command()
@click.option('--page', '-p', type=int, required=False, help="Switch between pages using the search command")
@click.argument('query')
def search(query, page):
    """Search For Scene Releases"""
    safe_q = urllib.parse.quote_plus(query)
    if page is None:
        response = r.get(f'https://predb.ovh/api/v1/?q={safe_q}').json()
        for rls in response['data']['rows']:
            click.echo(click.style(rls['name'], fg='green'))
    else:
        response = r.get(f'https://predb.ovh/api/v1/?q={safe_q}&page={page}').json()
        for rls in response['data']['rows']:
            click.echo(click.style(rls['name'], fg='green'))
@main.command()
@click.argument('release')
def info(release):
    """Show Information about specific scene release"""
    safe_q = urllib.parse.quote_plus(release)
    response = r.get(f'https://predb.ovh/api/v1/?q={safe_q}').json()
    for rls in response['data']['rows']:
        if rls['name'] == safe_q:
            click.echo(click.style(rls['name'], fg="green", bold=True))
            click.echo("Category: " + click.style(rls['cat'], fg="blue"))
            click.echo("Size: " + click.style(str(rls['size']) + str(' MB'), fg="yellow")) 
            click.echo("Files: " + click.style(rls['files'], fg="magenta"))
            preAt = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(int(rls["preAt"])))
            click.echo("Pre At: " + click.style(preAt, fg="cyan"))
            if rls['nuke'] is None:
                click.echo("Nuked? : " + click.style("Not Nuked", fg="green"))
            else:
                click.echo("Nuked? : " + click.style("Nuked", fg="red"))
                click.echo("Nuke Reason : " + click.style(rls['nuke']['reason'], fg="red"))
                click.echo("Nuke Network : " + click.style(rls['nuke']['net'], fg="red"))
                click.echo("Nuked at : " + click.style(time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(int(rls['nuke']['nukeAt']))), fg="red"))
    else:
        pass
    
@main.command()
def dump():
    """Download SQL Dumps from predb.ovh to working dir"""
    url = 'https://predb.ovh/download'
    ext = 'sql.gz'
    link_list = []
    f_list = []
    try:
        def listFD(url, ext=''):
            page = r.get(url).text
            soup = BeautifulSoup(page, 'html.parser')
            fnames = [node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
            f_list.append(fnames)
            dl_url = [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
            link_list.append(dl_url)
            q = input('Download Nuke Dump or Pre Dump? (n/p)')
            if q == "n":
                download(link_list[0][0], f_list[0][0])
                click.echo(click.style('Downloaded Nuke SQL Dump to working directory of this script.', fg="green"))
            if q == "p":
                download(link_list[0][1], f_list[0][1])
                click.echo(click.style('Downloaded Pre SQL Dump to working directory of this script.', fg="green"))
        for file in listFD(url, ext):
            print(file)
    except TypeError:
        pass
@main.command()
def stats():
    """Stats about PreDB.ovh"""
    response = r.get('https://predb.ovh/api/v1/stats').json()
    click.echo(click.style('Total Releases: ' + str(response["data"]["total"]), fg="green", bold=True))
    iso_date = response['data']['date']
    date = parser.parse(iso_date)
    click.echo(click.style('Last update: ' + str(date), fg="blue", bold=True))
    ms = response['data']['time'] * 1000
    click.echo(click.style('Average Search Duration: ' + str(round(ms)) + 'ms', fg="yellow", bold=True))

    


if __name__ == "__main__":
    main()