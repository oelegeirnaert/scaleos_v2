echo "
################################################################################################################################
# AppCreation File: address
#
# Install Command:
# curl http://localhost:8000/utils/app/create/geography/address/ -o app_geography.sh  && bash app_geography.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 25th February 2025 19:47
#
################################################################################################################################
"
docker compose -f docker-compose.local.yml run --rm django python manage.py startapp geography &&
sudo chown -R $USER geography/ &&
DIRECTORY="scaleos/geography"
if [ -d "$DIRECTORY" ]; then
echo "$DIRECTORY does exist."
return
fi
mv geography scaleos/geography
echo "
# NEXT STEPS:
# geography/apps.py # prefix name with scaleos like: name = 'scaleos.geography'
# settings/base.py # add app to LOCAL_APPS
"
