# source aliasses.sh
alias devup='docker compose -f docker-compose.local.yml up'
alias devbuild='docker compose -f docker-compose.local.yml build'
alias devtest='docker compose -f docker-compose.local.yml run --rm django coverage run -m pytest'
alias mm='docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations'
alias mi='docker compose -f docker-compose.local.yml run --rm django python manage.py migrate'
alias manage='docker compose -f docker-compose.local.yml run --rm django python manage.py'
