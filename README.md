# D3 - Digital Data Dashboard

### Collaborators:

Justin Chambers  
Joe Ravenna  
Aaron Stewart  
Husain Tazarvi  

### Dependencies

This project uses the [PyCharm](https://www.jetbrains.com/pycharm/) IDE and [Python 3.5.2](https://www.python.org/downloads/release/python-352/) interpreter   

The interpreter can be selected from PyCharm's *Project Interpreter* page  

**Windows and Linux** 
```bash
File | Settings | Project Interpreter 
```
**OS X** 
```bash
PyCharm | Preferences | Project Interpreter
```
**Or...**
```bash
Ctrl+Alt+S  
```

### Dependency Instructions
For this project to run installation of these packages are required 

- [NumPy](http://www.numpy.org/)   
- [pandas](http://pandas.pydata.org/)  
- [Django](https://www.djangoproject.com/)
- [google-api-python-client — Google API Client Library for Python](https://pypi.python.org/pypi/google-api-python-client/)  
- [pyOpenSSL](https://pyopenssl.readthedocs.io/en/stable/)  

[Installing, Uninstalling and Upgrading Packages](https://www.jetbrains.com/help/pycharm/2016.3/installing-uninstalling-and-upgrading-packages.html)

### PyCharm Run/Debug Configuration for Django Server:_

- Run > Edit Configurations... :
    - Click '+' to add a new configuration
    - Select 'Django Server'
    - Name: 'D3'
    - In the Configuration tab:
        - Check 'Run browser'
        - Browser link: 'http://127.0.0.1:8000/dashboard'
        - Environment variables:
            - Two environment variables should be set:
            - Click '...' to open the editor
            - Click '+' to add a name and value pair (if name/value pairs are not there already).
                - Name: 'DJANGO_SETTINGS_MODULE', Value: 'd3site.settings'
                - Name: 'PYTHONUNBUFFERED', Value: 1
            - Make sure the 'Include parent...' is checked.
            - Click 'OK' to close the editor.
        - Make sure the 'Python interpreter' is 3.5.x
    - Click 'OK' to close the Config editor
        
### PyCharm Packages

#### Configuring a Python Package in PyCharm
In order to reference a python module or package that you create, you must mark the directory as a Source Root. To do that:

1. Right-click on the module directory
2. Select 'Mark Directory As...'
3. Select 'Source Root'

#### Best Practices
When building your own python module, you need 3 things:
1. A good directory name (no capital letters, no hyphens, underscores are fine)
2. An ```__init__.py``` file (you can leave the contents of the file blank)
3. At least one other python file 

#### Referencing the Packages
Referencing these packages is relative to the python function using the import statement. For example, consider a directory organized:

```
mysite
|---> mypackage_one
      |---> __init__.py
      |---> mypackage_one.py
|---> mypackage_two
      |---> __init__.py
      |---> mypackage_two.py
|---> myapp
      |---> my_cool_script.py
```
If in ```my_cool_script.py``` I want to use some python function in ```mypackage_one```, I would use this import statement:

```python
import mypackage_one as pkg1
```
Assuming you have configured ```mypackage_one``` as instructed above, this import statement should work because the package reference is one level up from the calling file.# dashboard-dev-python-orig
# dash-py-original
# dashboard-development-python
