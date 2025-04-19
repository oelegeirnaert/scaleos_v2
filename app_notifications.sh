echo "
################################################################################################################################
# AppCreation File: notification
#
# Install Command:
# curl http://localhost:8000/utils/app/create/notifications/notification/ -o app_notifications.sh  && bash app_notifications.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 17th March 2025 10:13
#
################################################################################################################################
"
docker compose -f docker-compose.local.yml run --rm django python manage.py startapp notifications &&
sudo chown -R $USER notifications/ &&
DIRECTORY="scaleos/notifications"
if [ -d "$DIRECTORY" ]; then
echo "$DIRECTORY does exist."
return
fi
mv notifications scaleos/notifications
echo "
# NEXT STEPS:
# notifications/apps.py # prefix name with scaleos like: name = 'scaleos.notifications'
# settings/base.py # add app to LOCAL_APPS
"
