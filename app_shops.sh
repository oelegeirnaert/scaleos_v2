echo "
################################################################################################################################
# AppCreation File: shop
#
# Install Command:
# curl http://localhost:8000/utils/app/create/shops/shop/ -o app_shops.sh  && bash app_shops.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 14th May 2025 07:32
#
################################################################################################################################
"
docker compose -f docker-compose.local.yml run --rm django python manage.py startapp shops &&
sudo chown -R $USER shops/ &&
DIRECTORY="scaleos/shops"
if [ -d "$DIRECTORY" ]; then
echo "$DIRECTORY does exist."
return
fi
mv shops scaleos/shops
echo "
# NEXT STEPS:
# shops/apps.py # prefix name with scaleos like: name = 'scaleos.shops'
# settings/base.py # add app to LOCAL_APPS
"
