echo "
################################################################################################################################
# AppCreation File: building
#
# Install Command:
# curl http://localhost:8000/utils/app/create/buildings/building/ -o app_buildings.sh  && bash app_buildings.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 27th March 2025 07:37
#
################################################################################################################################
"
docker compose -f docker-compose.local.yml run --rm django python manage.py startapp buildings &&
sudo chown -R $USER buildings/ &&
DIRECTORY="scaleos/buildings"
if [ -d "$DIRECTORY" ]; then
echo "$DIRECTORY does exist."
return
fi
mv buildings scaleos/buildings
echo "
# NEXT STEPS:
# buildings/apps.py # prefix name with scaleos like: name = 'scaleos.buildings'
# settings/base.py # add app to LOCAL_APPS
"
