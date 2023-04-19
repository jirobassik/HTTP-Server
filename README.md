# Server
HTTP server(only socket)\
Valid methods: POST, GET, OPTIONS, DELETE

## Terminal commands:
### Server:
- Run server: python server_cli.py start_server
- Stop server: python server_cli.py stop_server

### Client:
- Client CLI request: python client_cli.py cli_request -m GET -u /view/t200.html -h Content-Type:text/html -h Content-Length:162 -b view.html
- Client request from file: python client_cli.py file_request client_req.txt
