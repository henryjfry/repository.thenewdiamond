#!/bin/sh
cd /home/osmc/repository.thenewdiamond
python /home/osmc/repository.thenewdiamond/prepare_zips.py
python /home/osmc/repository.thenewdiamond/prepare_diamond.py
python /home/osmc/repository.thenewdiamond/_repo_xml_generator.py
