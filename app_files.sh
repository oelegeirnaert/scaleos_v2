echo "
################################################################################################################################
# AppCreation File: file
#
# Install Command:
# curl http://localhost:8000/utils/app/create/files/file/ -o app_files.sh  && bash app_files.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 14th May 2025 09:19
#
################################################################################################################################
"
docker compose -f docker-compose.local.yml run --rm django python manage.py startapp files &&
sudo chown -R $USER files/ &&
DIRECTORY="scaleos/files"
if [ -d "$DIRECTORY" ]; then
echo "$DIRECTORY does exist."
return
fi
mv files scaleos/files
echo "
# NEXT STEPS:
# files/apps.py # prefix name with scaleos like: name = 'scaleos.files'
# settings/base.py # add app to LOCAL_APPS
"
