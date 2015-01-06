* template is kept separately as two html files; one boilerplate and one for every work order created
* HTML creating / string functions are kept in dispatcher/rendering.py
* Filesystem / folder functions are kept in dispatcher/filesystem.py
* XML functions are kept in dispatcher/parsing.py
* dispatcher.py is gone and replaced by dispatcher/__init__.py::main which is as brief as possible
* it all still builds using setup.py sdist and setup.py develop
