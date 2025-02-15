#!/bin/bash

# Set variables
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FACT_APP_DIR="/tmp/fact_app"
BACKUP_FILE="fact_app_backup_${TIMESTAMP}.zip"
FTP_HOST="172.18.0.11"
FTP_USER="ftpuser"
FTP_PASS="ftpuserpassword"

# Create a timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Zip the contents of /tmp/fact_app
zip -r "${FACT_APP_DIR}/${BACKUP_FILE}" "${FACT_APP_DIR}"

# Use lftp to transfer the file
lftp -c "open ftp://${FTP_USER}:${FTP_PASS}@${FTP_HOST}; \
         put ${FACT_APP_DIR}/${BACKUP_FILE}; \
         quit"

# Remove the local zip file
rm "${FACT_APP_DIR}/${BACKUP_FILE}"

# Clear the contents of /tmp/fact_app
rm -rf ${FACT_APP_DIR}/*

# Recreate necessary directories
mkdir -p ${FACT_APP_DIR}/uploads ${FACT_APP_DIR}/downloads
chown -R flask_app:flask_app /tmp/fact_app
chmod -R 755 /tmp/fact_app