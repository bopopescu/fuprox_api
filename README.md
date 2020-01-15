### fuprox
#### Installing Requirements and Running App 
Navigate to the directory fuporx-master
Installing requirements from the file provided</br>
Finally, run the python file</br>

````
cd fuporx-master
pip install -r requirements.txt
python api.py
````
##
### Choosing the database of choice
### MySQL  
open `__init__.py` then select

edit `app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://<USERNAME>:<PASSWORD>@localhost:3306/<TABLENAME>"`</br>

default tablename 'fuprox'

### SQlite
Add the following lines
```buildoutcfg
basedir  = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+os.path.join(basedir,"db.sqlite")
```
and remove the existsing 
`app.config["SQLALCHEMY_DATABASE_URI"] = "mysql ...`
##
### Creating a database 
Mysql :
```
create database fuprox 
```

### Seeding the tables
open teminal || python terminal
</br>
Mysql && sqlite 
```buildoutcfg
python 
from api import db
db.create_all()
quit()
``` 


### Endpoints 
https://documenter.getpostman.com/view/5359261/SWEE1Ep9?version=latest
