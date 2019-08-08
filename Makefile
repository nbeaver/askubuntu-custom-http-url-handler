quick-test :
	./http_url_handler.py 'https://askubuntu.com/questions/1161752/how-can-i-configure-a-domain-specific-default-browser'
	./http_url_handler.py 'https://superuser.com/questions/688063/is-there-a-way-to-redirect-certain-urls-to-specific-web-browsers-in-linux/'

install-desktop-file :
	desktop-file-install --dir="$(HOME)/.local/share/applications" 'http-url-handler.desktop'
