# 6320 Project
6320 Fall 2021 with Prof. Mithun Balakrishna Course Project

Running the project:
* cd venv/Scripts
* activate
* pip install numpy
* pip install nltk
* pip install pywsd
* pip install -U pip setuptools wheel
* pip install -U spacy
* python -m spacy download en_core_web_sm

Then, in the Python console:
* import nltk
* nltk.download('popular')
* nltk.download('book')  ??

To start running Solr:
* navigate to directory
* open powerterminal
* bin\solr.cmd start
* open servers/solr/jim_core
* delete everything

To run with provided questions:
* Name file "new_question_list.txt" in main working directory
* Run task3
* To use with task1, name file "old_question_list.txt" in main working directory