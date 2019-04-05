# Shopping Catalog
##### The 2nd project (Item Catalog)
This web application  about shopping which collect all clothes for all ages (Men , Women , Kids) that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Project Requirements

#### JSON
  - The project implements a JSON endpoint that serves the same information as displayed in the HTML endpoints for an arbitrary item in the catalog.

#### CRUD Operations
- Website reads category and item information from a database.
- Website includes a form allowing users to add new items and correctly processes submitted forms.
- Website does include a form to edit/update a current record in the database table and correctly processes submitted forms.
- Website does include a function to delete a current record.

#### Authentication and Authorization
- Create, delete and update operations do consider authorization status prior to execution.
- Page implements a third-party authentication & authorization service (like Google Accounts or Mozilla Persona) instead of implementing its own authentication & authorization spec.
- Make sure there is a 'Login' and 'Logout' button/link in the project. The aesthetics of this button/link is up to the discretion of the student.

#### Code Quality
- Code is ready for personal review and neatly formatted and compliant with the Python [pycodestyle](https://www.python.org/dev/peps/pep-0008/) style guide.

#### Comments
- Comments are present and effectively explain longer code procedures.

#### Documentation
- `README.md` file includes details of all the steps required to successfully run the application.

## Dependencies 
This program requires some other software programs to run properly :

* Install Vagrant and VirtualBox.
* Install Python editor for writing code.
* Install PostgreSql for create database.


## Running Code
* Go to the **Vagrant** folder using the command `cd /vagrant`  
* Clone this project using command
```bash
git clone https://github.com/esraayounis/Catalog-beta.git
```
* Launch the Vagrant VM (vagrant up) by using the command `vagrant up`.
* After finishing downloading, now run `vagrant ssh` to login to your VM.
* Write your Flask application locally in the vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM) by using `cd /vagrant/catalog`.
* Run the **catalog_database.py** file to setup the database using this command `python catalog_database.py`.
* Now you can run the application using command `python project.py`
* Access and test your application by visiting http://localhost:8000 locally.

## Application Pages
| Root | Result |
| :-- | :------------- |
| http://localhost:8000  | The home Page which consist of **Categories** that contains all Categories in the database , **Latest Items** that contains the last items added to database. |
| http://localhost:8000/login | Login page, you can login with your _facebook account_ **or** _Google account._ |
| http://localhost/categories/<category_id> http://localhost/categories/<category_id>/items | Displays the items page for the category of id number <category_id> |
| http://localhost/categories/<category_id>/items/<item_id> | Displays a page contains the name, image and description for the item has id number <item_id>  |
| http://localhost:8000/<category_id>/items/<item_id>/edit | *(Login Required)* Displays a page helps you to edit the item of id <item_id> |
| http://localhost:8000/<category_id>/items/<item_id>/delete | *(Login Required)* Displays a page helps you to delete the item of id <item_id> |
| http://localhost:8000/addItem | *(Login Required)* Displays a page helps to create a new item |

## API Endpoints
This application provides a JSON API.

| Request | Response |
| :----- | :------------------------------------------- |
| http://localhost/json/categories | JSON Object includes all of the Categories in the DB. |
| http://localhost/json/categories/<int:category_id> | JSON Object includes details for the category of specific category <category_id> |
| http://localhost/json/categories/<int:category_id>/items | JSON Object includes all items in the category of id number <category_id> |
| http://localhost/json/categories/<category_id>/items/<item_id> | JSON Object includes details of the item of specific item <item_id> |


