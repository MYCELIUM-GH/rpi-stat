# Raspberry Pi Status Display

Small script to show different info on SSD1306 display connected to RPI5.
One day I desided to make small status screen for my RPI. Initially I used 3D printed 10" server rack, but because it feels a bit lonely - I've wrote this script and printed custom shelf.

## Preparations

Connections - W.I.P

Required libs - W.I.P

For spotify integration you have to create new web app here: https://developer.spotify.com/dashboard/ and set the following environment variables:

```sh
export SPOTIPY_CLIENT_ID='change_me'
export SPOTIPY_CLIENT_SECRET='change_me'
export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8888/'
```

## Additional

If you wish to create new daemon for autostarting this app - simply create new service like this:
`/etc/systemd/system/change_me.service`

It should look like this:

```ini
[Unit]
Description=change_me
After=network.target

[Service]
User=change_me

WorkingDirectory=/home/change_me_to_your_dir

# IMPORTANT: add your actual spotify credentials here
Environment="SPOTIPY_CLIENT_ID=change_me"
Environment="SPOTIPY_CLIENT_SECRET=change_me"
Environment="SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/"

# replace the path with the exact path to your venv's python executable
ExecStart=/home/change_me_to_your_dir/venv/bin/python /home/change_me_to_your_dir/stats.py

Restart=always

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```
