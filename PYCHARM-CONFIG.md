## PyCharm Run/Debug Configuration for Django Server:_

1. Run > Edit Configurations... :
    1. Click '+' to add a new configuration
    2. Select 'Django Server'
    3. Name: 'D3'
    4. In the Configuration tab:
        1. Check 'Run browser'
        2. Browser link: 'http://127.0.0.1:8000/dashboard'
        3. Environment variables:
            - Two environment variables should be set:
            1. Click '...' to open the editor
            2. Click '+' to add a name and value pair (if name/value pairs are not there already).
                1. Name: 'DJANGO_SETTINGS_MODULE', Value: 'd3site.settings'
                2. Name: 'PYTHONUNBUFFERED', Value: 1
            3. Make sure the 'Include parent...' is checked.
            4. Click 'OK' to close the editor.
        4. Make sure the 'Python interpreter' is 3.5.x
        5. Click 'OK' to close the Config editor
        
## PyCharm Packages

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
Assuming you have configured ```mypackage_one``` as instructed above, this import statement should work because the package reference is one level up from the calling file.