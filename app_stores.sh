echo "
################################################################################################################################
# AppCreation File: store
#
# Install Command:
# curl http://localhost:8000/utils/app/create/stores/store/ -o app_stores.sh  && bash app_stores.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 14th May 2025 08:08
#
################################################################################################################################
"
docker compose -f docker-compose.local.yml run --rm django python manage.py startapp stores &&
sudo chown -R $USER stores/ &&
DIRECTORY="scaleos/stores"
if [ -d "$DIRECTORY" ]; then
echo "$DIRECTORY does exist."
return
fi
mv stores scaleos/stores
echo "
# NEXT STEPS:
# stores/apps.py # prefix name with scaleos like: name = 'scaleos.stores'
# settings/base.py # add app to LOCAL_APPS
"
