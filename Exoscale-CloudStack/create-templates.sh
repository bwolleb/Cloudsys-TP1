#!/bin/sh

if [ -z "$1" ]; then
    echo "Usage: ./create-templates.sh <web server snapshot id> <database server snapshot id>"
    echo "List of snapshots: "
    exo compute instance snapshot list
    exit
fi

if [ -z "$2" ]; then
    echo "Usage: ./create-templates.sh <web server snapshot id> <database server snapshot id>"
    echo "List of snapshots: "
    exo compute instance snapshot list
    exit
fi

echo Creating webserver template...

# TODO: Replace exo vm by exo compute as exo vm are deprecated
SNAPSHOT_ID=$1
TEMPLATE_ID=$(exo vm snapshot show --output-template {{.TemplateID}} ${SNAPSHOT_ID})
BOOTMODE=$(exo vm template show --output-template {{.BootMode}} ${TEMPLATE_ID})
exo compute instance-template register \
    wordpress-template-automated \
    --zone ch-dk-2 \
    --from-snapshot $SNAPSHOT_ID \
    --description "Wordpress template from snapshot" \
    --boot-mode $BOOTMODE

echo Creating database template...

SNAPSHOT_ID=$2
TEMPLATE_ID=$(exo vm snapshot show --output-template {{.TemplateID}} ${SNAPSHOT_ID})
BOOTMODE=$(exo vm template show --output-template {{.BootMode}} ${TEMPLATE_ID})
exo compute instance-template register \
    database-template-automated \
    --zone ch-dk-2 \
    --from-snapshot $SNAPSHOT_ID \
    --description "Database template from snapshot" \
    --boot-mode $BOOTMODE