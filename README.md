# redmsg-logger
Services to log RedMsg messages to various backends

## Initial Setup

If you've just cloned the repo, you'll need to build your virtualenv:
```bash
./build-venv.sh
```

Then to configure the scripts:
```bash
cp config.yaml.example config.yaml
```
Edit the `config.yaml` file with your RedMsg and database info.

## Running in console

After the initial setup, run from the current directory:
```bash
source venv/bin/activate
redmsg-logger
```

## Running in a service

For a service called `redmsg-logger.service` with this repo cloned at `/opt/redmsg-logger`, place the following in `/etc/systemd/system/redmsg-logger.service`:
```
[Unit]
Description=RedMsg Logger
After=network.target

[Service]
WorkingDirectory=/opt/redmsg-logger
ExecStart=/bin/bash -c "source /opt/redmsg-logger/venv/bin/activate; exec /opt/redmsg-logger/venv/bin/redmsg-logger --config /opt/redmsg-logger/config.yaml"
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then run:
```bash
systemctl enable redmsg-logger.service
systemctl start redmsg-logger.service
```
