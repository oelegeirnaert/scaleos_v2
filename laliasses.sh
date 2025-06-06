# source for LOCAL aliasses.sh

# Quick Dev
alias mm='python manage.py makemigrations'
alias mi='python manage.py migrate'
alias devshell='python manage.py shell_plus --ipython'
alias devruff='ruff check . --fix'

# Documentation
alias docsbuild="docker compose -f docker-compose.docs.yml build"
alias docsup="docker compose -f docker-compose.docs.yml up -d"
alias docsopen="docsup && google-chrome http://localhost:9000/ &"

# Testing
alias generate_test_report='coverage html'
alias devtest='coverage run -m pytest'
alias open_test_report='google-chrome http://127.0.0.1:5500/htmlcov/index.html'
alias testreport='devtest && generate_test_report && open_test_report'

# Data
alias mkwaerboom='python manage.py create_organization waerboom'
alias mkscaleos='python manage.py create_organization scaleos'
alias mklanec='python manage.py create_organization lane_consulting'
alias mkpersons='python manage.py create_persons'

#i18n
alias devtrans='manage makemessages -a --extension=html,txt,email,py'
alias devtranscompile="manage compilemessages"

# WebPages
alias wpmail="google-chrome http://localhost:8025 &"
alias wpflower="google-chrome http://localhost:5555 &"
alias wpdjangoadmin="google-chrome http://localhost:8000/admin &"
alias wpsite="google-chrome http://localhost:8000 &"

# Tailwind
alias tw='python manage.py tailwind watch'
