REM Requires modelviz.py - http://unicoders.org/code/django/trunk/utils/
modelviz.py vgdb > models.dot
REM Requires Graphviz - http://www.graphviz.org/
dot models.dot -Tpng -o models.png