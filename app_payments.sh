echo "
################################################################################################################################
# AppCreation File: payment
#
# Install Command:
# curl http://localhost:8000/utils/app/create/payments/payment/ -o app_payments.sh  && bash app_payments.sh
#
#
# Designed by OeleGeirnaert.be
# App created: 7th February 2025 23:53
#
################################################################################################################################
"

docker compose -f docker-compose.local.yml run --rm django python manage.py startapp payments &&
sudo chown -R $USER payments/ &&

DIRECTORY="scaleos/payments"
if [ -d "$DIRECTORY" ]; then
  echo "$DIRECTORY does exist."
  return
fi

mv payments scaleos/payments

echo "
# NEXT STEPS:
# payments/apps.py # prefix name with scaleos like: name = 'scaleos.payments'
# settings/base.py # add app to LOCAL_APPS
"