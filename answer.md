Note that there is a difference between the `text/html` mimetype
(this is opening actual HTML files)
and the `x-scheme-handler/http` mimetype
(this is an HTTP URL).
I assume you want to customize how external applications open HTTP/HTTPS URLs,
since you mention domains.
(Note that this is for external applications.
Customizing how a particular *browser* handles an HTTP URL
is a different thing altogether.)

One tricky thing about custom URL handlers
is that there are at least four files the associations might be stored in,
depending on the application / library the application uses:

- `~/.config/mimeapps.list` (the right place to make changes)
- `~/.local/share/application/mimeapps.list` (the deprecated location)
- `~/.local/share/application/default.list` (the older deprecated location)
- `~/.local/share/applications/mimeinfo.cache` (the cache)

I've been doing some [work on custom URL handlers](https://github.com/nbeaver/thunderlink-install-guide)
lately, so I've adapted some of that for this purpose.
Here are the instructions:

0. Check the currently registered file for the protocols.
   Here's what they look like for me:

        $ gio mime x-scheme-handler/http
        Default application for “x-scheme-handler/http”: firefox.desktop
        Registered applications:
                firefox.desktop
                chromium-browser.desktop
        Recommended applications:
                firefox.desktop
                chromium-browser.desktop
        $ gio mime x-scheme-handler/https
        Default application for “x-scheme-handler/https”: firefox.desktop
        Registered applications:
                firefox.desktop
                chromium-browser.desktop
        Recommended applications:
                firefox.desktop
                chromium-browser.desktop

0. Write a [script that parses the URLs and launches the appropriate browser](https://github.com/nbeaver/askubuntu-custom-http-url-handler/blob/2df6569ef641120d69b4d14aa40086be9d93dd7a/http_url_handler.py).

   I prefer to use Python,
   since it has libraries to parse URLs and send errors to syslog.

        #! /usr/bin/env python3
        
        import subprocess
        import logging
        import argparse
        import syslog
        import sys
        
        try :
            from urllib.parse import urlparse
        except ImportError:
            from urlparse import urlparse
        import os.path
        
        def http_url(url):
            if url.startswith('http://'):
                return url
            if url.startswith('https://'):
                return url
            else:
                syslog.syslog(syslog.LOG_ERR, sys.argv[0] + ": not an HTTP/HTTPS URL: '{}'".format(url))
                raise argparse.ArgumentTypeError(
                    "not an HTTP/HTTPS URL: '{}'".format(url))
        
        if __name__ == '__main__':
            parser = argparse.ArgumentParser(
                description='Handler for http/https URLs.'
            )
            parser.add_argument(
                '-v',
                '--verbose',
                help='More verbose logging',
                dest="loglevel",
                default=logging.WARNING,
                action="store_const",
                const=logging.INFO,
            )
            parser.add_argument(
                '-d',
                '--debug',
                help='Enable debugging logs',
                action="store_const",
                dest="loglevel",
                const=logging.DEBUG,
            )
            parser.add_argument(
                'url',
                type=http_url,
                help="URL starting with 'http://' or 'https://'",
            )
            args = parser.parse_args()
            logging.basicConfig(level=args.loglevel)
            logging.debug("args.url = '{}'".format(args.url))
            parsed = urlparse(args.url)
            if parsed.hostname == 'askubuntu.com':
                browser = 'firefox'
            else:
                browser = 'chromium-browser'
            logging.info("browser = '{}'".format(browser))
            cmd = [browser, args.url]
            try :
                status = subprocess.check_call(cmd)
            except subprocess.CalledProcessError:
                syslog.syslog(syslog.LOG_ERR, sys.argv[0] + "could not open URL with browser '{}': {}".format(browser, args.url))
                raise

   Adapt the script to your liking,
   particularly the executable for `brave` (I haven't used it, so I don't know)
   and the hostname in the `if parsed.hostname` part.

0. Test the script.

   This should open with Firefox:
       
        $ ./http_url_handler.py 'https://askubuntu.com/questions/1161752/how-can-i-configure-a-domain-specific-default-browser'

   This should open with Chromium:

        $ ./http_url_handler.py 'https://superuser.com/questions/688063/is-there-a-way-to-redirect-certain-urls-to-specific-web-browsers-in-linux/'

0. Add the script to your `$PATH` so the desktop file can find it.

   I use a `bin` directory like this:

        $ mkdir ~/bin/

   and add this to `~/.profile`
   (note [you will need to log out and log in again to see changes](https://askubuntu.com/questions/59126/reload-bashs-profile-without-logging-out-and-back-in-again)):

        PATH="$HOME/local/bin:$PATH"

   and finally either copy or symlink the script to `~/bin`:

        $ ln -s $PWD/http_url_handler.py ~/bin/

   If you did this properly, you should see this:

        $ type -a http_url_handler.py 
        http_url_handler.py is /home/nathaniel/bin/http_url_handler.py

   not this:

        $ type -a http_url_handler.py 
        bash: type: http_url_handler.py: not found

0. Test the script.

   This should open in Chromium:

        $ http_url_handler.py 'https://superuser.com/questions/688063/is-there-a-way-to-redirect-certain-urls-to-specific-web-browsers-in-linux'

   This should open in Firefox:

        $ http_url_handler.py 'https://askubuntu.com/questions/1161752/how-can-i-configure-a-domain-specific-default-browser'

0. Install the desktop file. Here's the [one I used](https://github.com/nbeaver/askubuntu-custom-http-url-handler/blob/2df6569ef641120d69b4d14aa40086be9d93dd7a/http-url-handler.desktop):

        [Desktop Entry]
        Name=HTTP URL handler
        Comment=Open an HTTP/HTTPS URL with a particular browser
        TryExec=http_url_handler.py
        Exec=http_url_handler.py %u
        X-MultipleArgs=false
        Type=Application
        Terminal=false
        MimeType=x-scheme-handler/http

   Either via `desktop-file-install`:

        $ desktop-file-install --dir=$HOME/.local/share/applications/ http-url-handler.desktop

   or manually copy the `http-url-handler.desktop` file
   to the proper directory,
   which should be ``~/.local/share/applications/``:

        $ cp http-url-handler.desktop ~/.local/share/applications/

   These are the most important lines in the desktop file:

        Exec=http_url_handler.py %u
        MimeType=x-scheme-handler/http

0. Register the desktop file with the
   `x-scheme-handler/http` and `x-scheme-handler/https` mimetypes.

        $ gio mime x-scheme-handler/http  http-url-handler.desktop
        Set http-url-handler.desktop as the default for x-scheme-handler/http
        $ gio mime x-scheme-handler/https http-url-handler.desktop
        Set http-url-handler.desktop as the default for x-scheme-handler/https

   All this really does is change lines in `~/.config/mimeapps.list`
   under the `[Default Applications]` group
   so that instead of this:

        x-scheme-handler/http=firefox.desktop
        x-scheme-handler/https=firefox.desktop

   it says this:

        x-scheme-handler/http=http-url-handler.desktop
        x-scheme-handler/https=http-url-handler.desktop

   You can also add it under the `[Added Associations]` group
   with a text editor so it looks something like this:

        x-scheme-handler/http=http-url-handler.desktop;firefox.desktop;chromium-browser.desktop
        x-scheme-handler/https=http-url-handler.desktop;firefox.desktop;chromium-browser.desktop

   Some older applications use `~/.local/share/application/mimeapps.list`,
   but this is [officially deprecated](https://standards.freedesktop.org/mime-apps-spec/1.0.1/ar01s02.html).
   However, the `xdg-mime` command uses this location anyway:

        $ xdg-mime default http-url-handler.desktop x-scheme-handler/http
        $ xdg-mime default http-url-handler.desktop x-scheme-handler/https

   There is also an [even older deprecated file](https://lists.freedesktop.org/archives/xdg/2014-February/013177.html)
   called `defaults.list`
   that is still used by some applications.
   Edit this file with a text editor:
   
        $ edit ~/.local/share/applications/defaults.list
   
   and manually add these lines:
   
        x-scheme-handler/http=http-url-handler.desktop
        x-scheme-handler/https=http-url-handler.desktop
   
   under the "[Default Applications]" group.

0. Check if it was successfully registered.

        $ gio mime x-scheme-handler/http
        Default application for “x-scheme-handler/http”: http-url-handler.desktop
        Registered applications:
                firefox.desktop
                chromium-browser.desktop
        Recommended applications:
                firefox.desktop
                chromium-browser.desktop
        $ gio mime x-scheme-handler/https
        Default application for “x-scheme-handler/https”: http-url-handler.desktop
        Registered applications:
                firefox.desktop
                chromium-browser.desktop
        Recommended applications:
                firefox.desktop
                chromium-browser.desktop

   If you also added to the `[Added Associations]` group,
   it will look like something like this:

        $ gio mime x-scheme-handler/http
        Default application for “x-scheme-handler/http”: http-url-handler.desktop
        Registered applications:
                http-url-handler.desktop
                firefox.desktop
                chromium-browser.desktop
        Recommended applications:
                http-url-handler.desktop
                firefox.desktop
                chromium-browser.desktop
        $ gio mime x-scheme-handler/https
        Default application for “x-scheme-handler/https”: http-url-handler.desktop
        Registered applications:
                http-url-handler.desktop
                firefox.desktop
                chromium-browser.desktop
        Recommended applications:
                http-url-handler.desktop
                firefox.desktop
                chromium-browser.desktop

   Check `xdg-mime` also.

        $ xdg-mime query default x-scheme-handler/http
        http-url-handler.desktop
        $ xdg-mime query default x-scheme-handler/https
        http-url-handler.desktop

0. Test some URLs.

   This should open in Chromium:

        $ gio open 'https://superuser.com/questions/688063/is-there-a-way-to-redirect-certain-urls-to-specific-web-browsers-in-linux'

   This should open in Firefox:

        $ gio open 'https://askubuntu.com/questions/1161752/how-can-i-configure-a-domain-specific-default-browser'

   Now test the same URLs with `xdg-open`:

        $ xdg-open 'https://superuser.com/questions/688063/is-there-a-way-to-redirect-certain-urls-to-specific-web-browsers-in-linux/'

        $ xdg-open 'https://askubuntu.com/questions/1161752/how-can-i-configure-a-domain-specific-default-browser'

0. Update the mimeinfo cache.

   Some applications read `~/.local/share/applications/mimeinfo.cache`
   instead of `~/.config/mimeapps.list`.
   So update the cache:

        $ update-desktop-database ~/.local/share/applications/

For convenience, the files are on Github here:

<https://github.com/nbeaver/askubuntu-custom-http-url-handler>
