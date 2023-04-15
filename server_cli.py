import click
from server.util.json_util import json_save, json_clear_valid_folders, json_upload_key, json_del_valid_folder
from server.util.conf import CLIENT_FOLDERS
from server.http_server import HTTPServer
from server.util.conf import JSON_PATH


@click.group()
def server_cli():
    pass


# --------------------------------------------------------------------------

@click.command(name='client_file_set', )
@click.option('--client_folder', '-cl_f', multiple=True, help='[OPTION] folder name')
def client_f_set(client_folder):
    if program_folders := set(client_folder).difference(CLIENT_FOLDERS):
        click.echo(f'You try added not valid folders: {", ".join(program_folders)}')
    elif program_folders := set(json_upload_key(JSON_PATH, 'valid_folders')).intersection(client_folder):
        click.echo(f'Folder already exist: {", ".join(program_folders)}')
    else:
        json_save(JSON_PATH, client_folder, 'valid_folders')
        click.echo('Client folders added')


@click.command(name='client_file_clear')
def client_f_clear():
    json_clear_valid_folders(JSON_PATH, 'valid_folders')
    click.echo('List client folders been cleared')


@click.command(name='client_file_view')
def client_f_view():
    folders_name = json_upload_key(JSON_PATH, 'valid_folders')
    click.echo(f'All client folders: {", ".join(folders_name)}')


@click.command(name='client_file_del')
@click.argument('folder_name')
def client_f_del(folder_name):
    try:
        json_del_valid_folder(JSON_PATH, 'valid_folders', folder_name)
        click.echo(f'Client folder "{folder_name}" delete')
    except ValueError:
        click.echo(f'Client folder "{folder_name}" not exist')


# --------------------------------------------------------------------------

server_ = HTTPServer.default_connection()


@click.command(name='start_server')
# @click.option('--interruptible', is_flag=True, default=False, help='Allow user to interrupt the program with Ctrl+C.')
def server_start_stop():
    try:
        server_.start_server()
    except KeyboardInterrupt:
        print("Stop server")


# --------------------------------------------------------------------------

server_cli.add_command(client_f_set)
server_cli.add_command(client_f_del)
server_cli.add_command(client_f_view)
server_cli.add_command(client_f_clear)
server_cli.add_command(server_start_stop)

if __name__ == '__main__':
    server_cli()
