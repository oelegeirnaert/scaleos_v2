echo "
################################################################################################################################
# AppCreation File: person
#
# Install Command:
# curl http://localhost:8000/utils/app/create/hr/person/ -o app_hr.sh  && bash app_hr.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 7th February 2025 16:10
#
################################################################################################################################
"

docker compose -f docker-compose.local.yml run --rm django python manage.py startapp hr &&
sudo chown -R $USER hr/ &&

DIRECTORY="scaleos/hr"
if [ -d "$DIRECTORY" ]; then
  echo "$DIRECTORY does exist."
  return
fi

mv hr scaleos/hr

echo "
# NEXT STEPS:
# hr/apps.py # prefix name with scaleos like: name = 'scaleos.hr'
# settings/base.py # add app to LOCAL_APPS
"