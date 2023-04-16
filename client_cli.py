import click
from client.client import Client
from client.client_error import ClientError
from server.util import substring

client = Client.default_connection()


@click.group()
def client_cli():
    pass


# --------------------------------------------------------------------------

@click.command(name='file_request', )
@click.argument('file_name')
def req_file(file_name):
    try:
        file_mes = client.request_from_file(file_name)
        client.connect_server_file(file_mes)
    except ClientError as cle:
        print(cle)


@click.command(name='cli_request')
@click.option("--method", "-m", default="GET", help="HTTP request method")
@click.option("--url", "-u", required=True, help="URL to send the request to")
@click.option("--version", "-v", required=True, default="HTTP/1.1", help="HTTP version")
@click.option("--headers", "-h", multiple=True, help="HTTP headers (use multiple times for multiple headers)")
@click.option("--body", "-b", help="HTTP request body (path to file")
def cli_request(method, url, version, headers, body):
    headers_dict = dict(header.split(":") for header in headers) if headers else {}
    read_file = None
    if body:
        read_file = substring.read_file_byte('client/post_files', f"/{body}")
    client.connect_server_cli(method, url, headers_dict, body=read_file, version=version)


# --------------------------------------------------------------------------

client_cli.add_command(req_file)
client_cli.add_command(cli_request)

if __name__ == '__main__':
    client_cli()
