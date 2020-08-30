# source ./venv/bin/activate
flask run &
cd app/static
npm run dev_build &
npm run dev_run &
cd -