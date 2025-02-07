echo "
################################################################################################################################
# AppCreation File: reservation
#
# Install Command:
# curl http://localhost:8000/utils/app/create/reservations/reservation/ -o app_reservations.sh  && bash app_reservations.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 7th February 2025 20:24
#
################################################################################################################################
"

docker compose -f docker-compose.local.yml run --rm django python manage.py startapp reservations &&
sudo chown -R $USER reservations/ &&

DIRECTORY="scaleos/reservations"
if [ -d "$DIRECTORY" ]; then
  echo "$DIRECTORY does exist."
  return
fi

mv reservations scaleos/reservations

echo "
# NEXT STEPS:
# reservations/apps.py # prefix name with scaleos like: name = 'scaleos.reservations'
# settings/base.py # add app to LOCAL_APPS
"