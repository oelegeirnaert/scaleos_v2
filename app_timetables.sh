echo "
################################################################################################################################
# AppCreation File: timetable
#
# Install Command:
# curl http://localhost:8000/utils/app/create/timetables/timetable/ -o app_timetables.sh  && bash app_timetables.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 22nd May 2025 09:44
#
################################################################################################################################
"
docker compose -f docker-compose.local.yml run --rm django python manage.py startapp timetables &&
sudo chown -R $USER timetables/ &&
DIRECTORY="scaleos/timetables"
if [ -d "$DIRECTORY" ]; then
echo "$DIRECTORY does exist."
return
fi
mv timetables scaleos/timetables
echo "
# NEXT STEPS:
# timetables/apps.py # prefix name with scaleos like: name = 'scaleos.timetables'
# settings/base.py # add app to LOCAL_APPS
"
