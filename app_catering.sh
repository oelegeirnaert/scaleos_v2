echo "
################################################################################################################################
# AppCreation File: caterer
#
# Install Command:
# curl http://localhost:8000/utils/app/create/catering/caterer/ -o app_catering.sh  && bash app_catering.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 20th May 2025 07:25
#
################################################################################################################################
"
docker compose -f docker-compose.local.yml run --rm django python manage.py startapp catering &&
sudo chown -R $USER catering/ &&
DIRECTORY="scaleos/catering"
if [ -d "$DIRECTORY" ]; then
echo "$DIRECTORY does exist."
return
fi
mv catering scaleos/catering
echo "
# NEXT STEPS:
# catering/apps.py # prefix name with scaleos like: name = 'scaleos.catering'
# settings/base.py # add app to LOCAL_APPS
"
