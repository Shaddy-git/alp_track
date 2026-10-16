# Развёртывание alp_track

Две машины: APP (192.168.241.10), DB (192.168.241.20).

## DB-сервер
sudo bash deploy/db/01_install_postgres.sh
sudo -u postgres psql -f deploy/db/02_setup_database.sql
sudo -u postgres psql -c "ALTER USER appuser WITH PASSWORD '...';"
ADMIN_IP=<ip> sudo bash deploy/db/03_configure_network.sh

## APP-сервер
sudo bash deploy/app/01_install_runtime.sh
sudo bash deploy/app/02_deploy_app.sh
sudo cp deploy/env/app.env.example /etc/myapp/app.env
sudo nano /etc/myapp/app.env
sudo chown root:appuser /etc/myapp/app.env
sudo chmod 640 /etc/myapp/app.env
sudo -u appuser bash deploy/app/03_migrate.sh
sudo cp deploy/systemd/myapp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now myapp

## Проверка
sudo bash deploy/app/04_check.sh
