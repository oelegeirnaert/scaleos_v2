echo "
################################################################################################################################
# AppCreation File: event
#
# Install Command:
# curl http://localhost:8000/utils/app/create/events/event/ -o app_events.sh  && bash app_events.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 7th February 2025 13:55
#
################################################################################################################################
"

docker compose -f docker-compose.local.yml run --rm django python manage.py startapp events &&
sudo chown -R $USER events/ &&

DIRECTORY="scaleos/events"
if [ -d "$DIRECTORY" ]; then
  echo "$DIRECTORY does exist."
  return
fi

mv events scaleos/events

echo "
# NEXT STEPS:
# events/apps.py # prefix name with scaleos like: name = 'scaleos.events'
# settings/base.py # add app to LOCAL_APPS
"