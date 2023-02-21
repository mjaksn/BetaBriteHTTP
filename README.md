# BetaBrite HTTP API

[![Postman API tests](https://github.com/mjaksn/BetaBriteAutomation/actions/workflows/postman.yml/badge.svg)](https://github.com/mjaksn/BetaBriteHTTP/actions/workflows/postman.yml)

***⚠ Be sure to read the [security advisory](https://github.com/mjaksn/BetaBriteAPI#-hosting-this-api-introduces-significant-security-risks-) before using this code***

A simple HTTP interface for displaying and formatting messages on a BetaBrite Classic sign

## Requirements and Limitations

- Only supports MacOS and Linux
- The API host must have an RS232 serial port connection to a BetaBrite Classic sign
- The API only implements a small subset of the BetaBrite serial communication protocol
- Sending the command to write a new messages to the sign causes the sign to briefly go blank before the new message is displayed

## Running the code

- Restore the required packages

> `pip install -r requirements.txt`

- Edit `config.json` with the name of the serial port device the sign is connected to

> For example if the full serial port device path is `/dev/tty.Usb-To-Serial0` then the configuration would be 
> `{
>   "com_port": "tty.Usb-To-Serial0"
> }`

- Edit `bbapi.wsgi`, replacing `/path/to/BetaBriteAutomation` with the correct path to the code

- Run the developemnt version of the API with the command 

> `python -m flask --app app run`

- The OpenAPI documentation UI can then be viewed at [http://127.0.0.1:5000/](url)

## Non-development Deployment

Non-developemnt hosting can be done using Apache2 along with the [mod_wsgi](https://github.com/GrahamDumpleton/mod_wsgi) package

Once you have an Apache2 installed with mod_wsgi module enabled, an Apache configuration similar to the one below can be used to enable the app

```
<VirtualHost *>
    ServerName BetaBriteApiHost
    WSGIDaemonProcess app user=www-data group=www-data threads=5
    WSGIScriptAlias / /var/sites/BetaBriteAutomation/bbapi.wsgi
    <Directory /var/sites/BetaBriteAutomation>
        WSGIProcessGroup app
        WSGIApplicationGroup app
        Require all granted
    </Directory>
</VirtualHost>
```

## ⚠ Hosting this API introduces significant security risks
   
### Known Security Risks
- **Because un-sanitized, user-provided inputs are sent directly to a serial port file/device, this API could be exploited allow arbitrary command execution by a malicious API client**
- **No authentication or authorization mechanism has been implemented, so any client with network access to the API can make calls to any endpoint**

#### Suggested Mitigations

- **The bottom line is that only clients you control and/or trust completely should be able to reach the port the API is running on**
- Run the API on a single-purpose host with no other services or sensitive data present 
- Make sure the API it is not exposed on the internet
- Do not allow untrusted user-provided data input to reach the API 
- Configure a firewall to allow-list IP trusted API client IP addresses and block all other traffic to the API

