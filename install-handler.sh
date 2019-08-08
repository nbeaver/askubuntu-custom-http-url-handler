#! /usr/bin/env sh
MIMETYPE1="x-scheme-handler/http"
MIMETYPE2="x-scheme-handler/https"
DESKTOP_FILEPATH=http-url-handler.desktop
DESKTOP_FILENAME=$(basename "${DESKTOP_FILEPATH}")
apps="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
if ! test -d "${apps}"
then
    mkdir -p "${apps}"
fi
desktop-file-install --dir="${apps}" "${DESKTOP_FILEPATH}"
xdg-mime default "${DESKTOP_FILENAME}" "${MIMETYPE1}"
xdg-mime default "${DESKTOP_FILENAME}" "${MIMETYPE2}"
if command gio 2> /dev/null
then
    gio mime "${MIMETYPE1}" "${DESKTOP_FILENAME}"
    gio mime "${MIMETYPE2}" "${DESKTOP_FILENAME}"
fi
# For applications that read mimeinfo.cache instead of mimeapps.list:
update-desktop-database "${apps}"
