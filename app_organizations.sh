echo "
################################################################################################################################
# AppCreation File: organization
#
# Install Command:
# curl http://localhost:8000/utils/app/create/organizations/organization/ -o app_organizations.sh  && bash app_organizations.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 7th February 2025 11:22
#
################################################################################################################################
"

docker compose -f docker-compose.local.yml run --rm django python manage.py startapp organizations &&
sudo chown -R $USER organizations/ &&

DIRECTORY="scaleos/organizations"
if [ -d "$DIRECTORY" ]; then
  echo "$DIRECTORY does exist."
  return
fi

mv organizations scaleos/organizations

echo "
# NEXT STEPS:
# organizations/apps.py # prefix name with scaleos like: name = 'scaleos.organizations'
# settings/base.py # add app to LOCAL_APPS
"
