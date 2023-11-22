set -ex

ps xuf | egrep "run_server|gunicorn" | egrep -v "vim|grep" | awk '{print $2}' | xargs kill
