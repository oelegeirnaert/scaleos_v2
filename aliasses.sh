# source aliasses.sh
alias devup='docker compose -f docker-compose.local.yml up'
alias devbuild='docker compose -f docker-compose.local.yml build'
alias mm='docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations'
alias mi='docker compose -f docker-compose.local.yml run --rm django python manage.py migrate'
alias devshell='docker compose -f docker-compose.local.yml run --rm django python manage.py shell_plus --ipython'
alias manage='docker compose -f docker-compose.local.yml run --rm django python manage.py'

# Documentation
alias docsup="docker compose -f docker-compose.local.yml -f docker-compose.docs.yml up"
alias docsopen="chromium-browser http://localhost:9000/"

# Testing
alias devtest='docker compose -f docker-compose.local.yml run --rm django coverage run -m pytest'
alias testreport='devtest && docker compose -f docker-compose.local.yml run --rm django coverage html'

# Data
alias mkwaerboom='docker compose -f docker-compose.local.yml run --rm django python manage.py create_organization waerboom'
alias mkpersons='docker compose -f docker-compose.local.yml run --rm django python manage.py create_persons'