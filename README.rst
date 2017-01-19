==================
    Test Bank
==================

Thank you very much for your interest in my application. This is my interpretation of the technical test of Growth Street. Please let me know if anything does not work as expected.

:License: BSD


Getting started
----------------

* I use Python 3.6 compiled from source. The first step is to create a virtual environment preferable outside of the project::

    $ cd ~/your-path/virtual/
    $ python -m venv name_of_virtual
    $ source name_of_virtual/bin/activate

* Then, cd to the root folder of the project. Note that I've set the database to sqlite in local and test. This is strongly discouraged when using PostgreSQL in production (as it should be) but that way you don't need to set up a PostgreSQL server::

    $ cd path/to/project
    $ pip install -r requirements/local.txt
    $ pip install -r requirements/test.txt
    $ python manage.py makemigrations
    $ python manage.py migrate
    $ python manage.py test --settings=config.settings.test

* To create a **superuser account**, use this command::

    $ python manage.py createsuperuser

The admin panel is accessible at http://localhost:8000/admin after you start the developement server. To do so::
    
    $ python manage.py runserver --settings=config.settings.local


Description
----------------

* To create a normal user account, please go to "Sign up for free" and fill out the form. Upon submission, you will find a "Verify Your E-mail Address" page. Check the console to copy the activation link in the simulated email verification message. Paste it in your favourite web browser and the user is now active.

* The home_page of the borrowing section gives a synthetic view of the businesses and loans associated to the user. To unlock this, the user first has to create a Borrower profile. To do so, s/he must provide first and last names (can't be empty), must sign the conditions and provide a valid phone number. This is verified by sending a unique code to the user (in production, SMS via Twilio (not implemented), in DEBUG this is displayed in the console). This code is calculated by the server using a cryptographic hash of the phone number sent by AJAX, there is no need to store it in db. Once submitted, modifications of these informations are not allowed (I haven't implemented the change, it would probably require to create another table to keep the different versions.)

* After successful creation of this profile, the user is redirected to the creation form for his/her first business, requiring a name, a physical address, a category. Once the first business created, the user is then redirected to the main page and can either add another business or create a new loan. Businesses without any related loan can be updated / deleted.

* Creating a new loan implies to enter an amount from 10k to 100k, a duration in days, a reason and to select the business to which it is attached. New loans have a status of 0 "pending" for review by the administrators. As long as a loan is pending, it can be cancelled by the user (soft_delete: status is set to 4 "cancelled") 


A few technical points
------------------------------

* The boilerplate has been generated using cookie-cutter and follows the 12 factor philosophy. Unlike the skeleton created with django_startapp, the settings, docs and requirements are kept separate from the source code. The settings rely on django.environ to set up values that shouldn't be version-controlled such as the different credentials and the secret_key. Defaults are included for convenience in case the .env is not found.

* The registration is handled by django_allauth. The package users was provided by cookie-cutter, I've written the 'borrowing' package.

* The popups are managed by Sweet Alert 2. As this javascript module has been recently rewritten to use ES6 features, especially Promises, it requires es6-promise.js to polyfill (included by CDN).

* All my code follows PEP8 with --max-line-length=120 as specified per Django, I tend to stick to shorter lines though.

* HTML with bootstrap v4 and font-awesome


Testing
---------

The system has been unittested quite thoroughly, using factory_boy as a fixture replacement

To run the tests::

    $ python manage.py test --settings=config.settings.test


To check the coverage and generate an HTML coverage report::

    $ coverage run manage.py test --settings=config.settings.test
    $ coverage html

Then open htmlcov/index.html


Possible Future Work
--------------------

* Create historic tables for Loan, Business and BorrowerProfile to keep track of the change

* Implement calculate_interest_rate

* Deal with other currencies

* Implement an 'Investment' model and finance the Loans with them

* Use React + Redux to build a single page app using the Django back-end as an API




