# source aliasses.sh

# Quick Dev
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
alias generate_test_report='docker compose -f docker-compose.local.yml run --rm django coverage html'
alias devtest='docker compose -f docker-compose.local.yml run --rm django coverage run -m pytest'
alias open_test_report='chromium-browser http://127.0.0.1:5500/htmlcov/index.html'
alias testreport='devtest && generate_test_report && open_test_report'

# Data
alias mkwaerboom='docker compose -f docker-compose.local.yml run --rm django python manage.py create_organization waerboom'
alias mkpersons='docker compose -f docker-compose.local.yml run --rm django python manage.py create_persons'

#i18n
alias devtrans='manage makemessages -a'
alias devtranscompile="manage compilemessages"