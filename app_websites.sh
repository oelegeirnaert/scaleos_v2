echo "
################################################################################################################################
# AppCreation File: website
#
# Install Command:
# curl http://localhost:8000/utils/app/create/websites/website/ -o app_websites.sh  && bash app_websites.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 5th May 2025 10:35
#
################################################################################################################################
"
docker compose -f docker-compose.local.yml run --rm django python manage.py startapp websites &&
sudo chown -R $USER websites/ &&
DIRECTORY="scaleos/websites"
if [ -d "$DIRECTORY" ]; then
echo "$DIRECTORY does exist."
return
fi
mv websites scaleos/websites
echo "
# NEXT STEPS:
# websites/apps.py # prefix name with scaleos like: name = 'scaleos.websites'
# settings/base.py # add app to LOCAL_APPS
"
