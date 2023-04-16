import click
from client.client import Client
from client.client_error import ClientError

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
        print(file_mes)
        client.connect_server(file_mes)
    except ClientError as cle:
        print(cle)


#
# @click.command(name='client_file_clear')
# def client_f_clear():
#     json_clear_valid_folders(JSON_PATH, 'valid_folders')
#     click.echo('List client folders been cleared')
#
#
# @click.command(name='client_file_view')
# def client_f_view():
#     folders_name = json_upload_key(JSON_PATH, 'valid_folders')
#     click.echo(f'All client folders: {", ".join(folders_name)}')
#
#
# @click.command(name='client_file_del')
# @click.argument('folder_name')
# def client_f_del(folder_name):
#     try:
#         json_del_valid_folder(JSON_PATH, 'valid_folders', folder_name)
#         click.echo(f'Client folder "{folder_name}" delete')
#     except ValueError:
#         click.echo(f'Client folder "{folder_name}" not exist')
#
#
# # --------------------------------------------------------------------------
#
# server_ = HTTPServer.default_connection()
#
#
# @click.command(name='start_server')
# # @click.option('--interruptible', is_flag=True, default=False, help='Allow user to interrupt the program with Ctrl+C.')
# def server_start_stop():
#     try:
#         server_.start_server()
#     except KeyboardInterrupt:
#         print("Stop server")


# --------------------------------------------------------------------------

client_cli.add_command(req_file)

if __name__ == '__main__':
    client_cli()
