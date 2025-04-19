echo "
################################################################################################################################
# AppCreation File: application
#
# Install Command:
# curl http://localhost:8000/utils/app/create/software/application/ -o app_software.sh  && bash app_software.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 28th March 2025 17:43
#
################################################################################################################################
"
docker compose -f docker-compose.local.yml run --rm django python manage.py startapp software &&
sudo chown -R $USER software/ &&
DIRECTORY="scaleos/software"
if [ -d "$DIRECTORY" ]; then
echo "$DIRECTORY does exist."
return
fi
mv software scaleos/software
echo "
# NEXT STEPS:
# software/apps.py # prefix name with scaleos like: name = 'scaleos.software'
# settings/base.py # add app to LOCAL_APPS
"
