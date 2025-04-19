echo "
################################################################################################################################
# AppCreation File: device
#
# Install Command:
# curl http://localhost:8000/utils/app/create/hardware/device/ -o app_hardware.sh  && bash app_hardware.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 28th March 2025 17:41
#
################################################################################################################################
"
docker compose -f docker-compose.local.yml run --rm django python manage.py startapp hardware &&
sudo chown -R $USER hardware/ &&
DIRECTORY="scaleos/hardware"
if [ -d "$DIRECTORY" ]; then
echo "$DIRECTORY does exist."
return
fi
mv hardware scaleos/hardware
echo "
# NEXT STEPS:
# hardware/apps.py # prefix name with scaleos like: name = 'scaleos.hardware'
# settings/base.py # add app to LOCAL_APPS
"
