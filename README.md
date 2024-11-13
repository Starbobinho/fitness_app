# fitness_app
Web app to track your evolution and organize workouts from gym

In this app i tried to implement 3 design patterns in differents models.

In workout.py was implemented the Factory Method pattern.

In user.py was implemented the Facade Method pattern.

In goals.py was implemented the Template Method pattern.

To install into your machine just clone the repository with:

git clone https://github.com/Starbobinho/fitness_app

Activate the venv with:

. venv/Scripts/activate

And use the command:

flask run

If by anything goes wrong, delete the venv in your machine, create a new one and use the following commands line:

pip install Flask

pip install requests

Again, if still missing something in your machine here's the list of all librarys installed in my venv (Package_name==Version):

blinker==1.8.2
certifi==2024.7.4
charset-normalizer==3.3.2
click==8.1.7
colorama==0.4.6
Flask==3.0.3
idna==3.8
itsdangerous==2.2.0
Jinja2==3.1.4
MarkupSafe==2.1.5
requests==2.32.3
urllib3==2.2.2
Werkzeug==3.0.4