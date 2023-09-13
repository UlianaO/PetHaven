from flask import Flask, flash, url_for, request, session, g, render_template
import sqlite3
import os
from database import get_database
# from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db_name = 'crudapplication.db'


@app.teardown_appcontext
def close_database(error):
    if hasattr(g, 'crudapplication_db'):
        g.crudapplication_db.close()


def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        blobPic = file.read()
        return blobPic

################## REGISTRATION #####################################################

def get_current_user():
    user = None
    if 'user' in session:
        user = session['user']
        db = get_database()
        user_cursor = db.execute('select * from Users where email = ?', [user])
        user = user_cursor.fetchone()
    return user


#  adopt = register. you only get registered if you adopt.
@app.route('/adopt/<int:pid>', methods=['POST', 'GET'])
def adopt(pid):
    db = get_database()
    cur_user = get_current_user()
    pet_cursor = db.execute('SELECT * from Pets where pid = ?', [pid])
    single_pet = pet_cursor.fetchone()

    if request.method == 'POST':

        # STORE into Applicants
        name = request.form.get('name')
        dob = request.form.get('dob')
        phone = request.form.get('phone')
        address = request.form.get('address')
        employment = request.form.get('employment')
        reason = request.form.get('reason')
        db = get_database()


        ###########  NEED TO CHECK IF APPLICANT EXISTS before inserting ###########

        ###########################################################################

        #  if email is already in the database --> user has an account --> user should be in Applicants
        '''
        check_cursor = db.execute('SELECT email FROM Users WHERE id = (SELECT id FROM Applicants)')
        duplicates = check_cursor.fetchall()
        if duplicates:
            return redirect(url_for('login'))

        #  if user does not exist --> applicant does not exist
        else:
        '''
        db.execute('INSERT INTO Applicants(pet, name, dob, phone, address, employment, reason)'
                    'values(?,?,?,?,?,?,?)', [pid, name, dob, phone, address, employment, reason])
        db.commit()
            
        db = get_database()

            # change the status of the animal to pre-adopted
        db.execute('UPDATE Pets set status = ? where pid = ?', ['pre-adopted', pid])
        db.commit()

            # REGISTER user so they can see the status of the application
        email = request.form['email']
        password = request.form['password']

        '''
            user_cursor = db.execute('SELECT * FROM Users where email = ?', [email])
            existing = user_cursor.fetchone()

            if existing:
                return redirect(url_for('login'))
        '''
            #encode password
        hashed_password = generate_password_hash(password)

        db.execute("INSERT INTO Users (email, password) values "
                    "( ?,?)", [email, hashed_password])
        db.commit()
        return redirect(url_for('index'))

    return render_template('adoptionapplication.html', single_pet=single_pet, user=cur_user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    db = get_database()  # created in database.py
    cur_user = get_current_user()
    error = None
    privilage = 'low'
    if request.method == 'POST':
        email = request.form['email']  # 'name' refers to name attribute of html
        password = request.form['password']
        user_cursor = db.execute("SELECT * FROM Users WHERE email = ?", [email])
        user = user_cursor.fetchone()
        
        if user:
            if check_password_hash(user['password'], password):  # user`s column password with inserted password
                session['user'] = user['email']  # if log in is succesful, his username(stored in db) will be stored in session object user(pass this username to all html pages)
                db = get_database()
                user_privilage = db.execute("SELECT privilage FROM Users WHERE email = ?", [email])
                privilage = user_privilage.fetchone()
                
                db.execute("UPDATE Users SET status = 'active' WHERE email = ?", [email]);
                db.commit()
                return redirect(url_for('index'))
            else:
                error = 'Error login'
        else:
            error = 'Username and Password don`t match'
        
        
    return render_template('login.html', errorlogin=error, user=cur_user, privilage = privilage)


@app.route('/logout')
def logout():
    # user becomes None, remove from session
    session.pop('user', None)
    db = get_database()
    db.execute("UPDATE Users SET status = 'inactive' ");
    db.commit()

    return redirect(url_for('index'))
#####################################################################################################################

@app.route('/')
def index():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute('SELECT * FROM Pets')
    all_pets = pet_cursor.fetchall()

    return render_template('index.html', all_pets=all_pets, filterType='any', user=cur_user)

@app.route('/home')
def home():
    cur_user = get_current_user()
    return render_template('index.html', user=cur_user)


@app.route('/myaccount')
def myaccount():
    cur_user = get_current_user()
    db = get_database()
    user_privilage = db.execute("SELECT * FROM Users WHERE (privilage = 'admin' AND status = 'active') ")
    privilage = user_privilage.fetchall()
        
    if cur_user:
            return render_template('myaccount.html', user=cur_user, privilage = privilage)
    else:
        return redirect(url_for('login'))

# ----------------------------------------------- Filter Types -----------------------------------------------#

# Filter by stay (shortest to longest stay)
@app.route('/shortestStay')
def filter_Longest_Stay():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute('SELECT * FROM Pets ORDER BY dateofintake DESC')
    shortestStayOrderPets = pet_cursor.fetchall()
    return render_template('index.html', user=cur_user, shortestStayOrderPets=shortestStayOrderPets, filterType='shortToLongStay')


# Filter by stay (longest to shortest stay)
@app.route('/longestStay')
def filter_Shortest_Stay():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute('SELECT * FROM Pets ORDER BY dateofintake')
    longestStayOrderPets = pet_cursor.fetchall()
    return render_template('index.html', user=cur_user, longestStayOrderPets=longestStayOrderPets, filterType='longToShortStay')


# Filter by age (youngest to oldest)
@app.route('/youngestPets')
def filter_Youngest():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute('SELECT * FROM Pets ORDER BY dob DESC')
    youngestOrderPets = pet_cursor.fetchall()
    return render_template('index.html', user=cur_user, youngestOrderPets=youngestOrderPets, filterType='youngToOld')


# Filter by age (oldest to youngest)
@app.route('/oldestPets')
def filter_Oldest():
    db = get_database()
    cur_user = get_current_user()
    pet_cursor = db.execute('SELECT * FROM Pets ORDER BY dob')
    oldestOrderPets = pet_cursor.fetchall()
    return render_template('index.html', user=cur_user, oldestOrderPets=oldestOrderPets, filterType='oldToYoung')


# Filter by sex (female)
@app.route('/femalePets')
def filter_female():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute('SELECT * FROM Pets WHERE sex = \'F\'')
    femalePets = pet_cursor.fetchall()
    return render_template('index.html', user=cur_user, femalePets=femalePets, filterType='female')


# Filter by sex (male)
@app.route('/malePets')
def filter_male():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute('SELECT * FROM Pets WHERE sex = \'M\'')
    malePets = pet_cursor.fetchall()
    return render_template('index.html', user=cur_user, malePets=malePets, filterType='male')


# Filter by type (dog)
# NOTE: Type might not be correct
@app.route('/dogs')
def filter_dogs():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute('SELECT * FROM Pets WHERE type = \'Dog\'')
    dogs = pet_cursor.fetchall()
    return render_template('index.html', user=cur_user, dogs=dogs, filterType='dogs')


# Filter by type (cat)
# NOTE: Type might not be correct
@app.route('/cats')
def filter_cats():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute('SELECT * FROM Pets WHERE type = \'Cat\'')
    cats = pet_cursor.fetchall()
    return render_template('index.html', user=cur_user, cats=cats, filterType='cats')


# Filter by type (other)
# NOTE: Type might not be correct
@app.route('/otherPets')
def filter_otherPets():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute('SELECT * FROM Pets WHERE type = \'Other\'')
    otherPets = pet_cursor.fetchall()
    return render_template('index.html',user=cur_user,otherPets=otherPets, filterType='otherPets')


# Filter by age: baby (0-1)
@app.route('/babyPets')
def filter_babyPets():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute(
        'SELECT * FROM Pets WHERE strftime(\'%Y.%m%d\', \'now\') - strftime(\'%Y.%m%d\', dob) > 0 AND strftime(\'%Y.%m%d\', \'now\') - strftime(\'%Y.%m%d\', dob) < 1')
    babyPets = pet_cursor.fetchall()
    return render_template('index.html', user=cur_user, babyPets=babyPets, filterType='babyPets')


# Filter by age: young (1-3)
@app.route('/youngPets')
def filter_youngPets():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute(
        'SELECT * FROM Pets WHERE strftime(\'%Y.%m%d\', \'now\') - strftime(\'%Y.%m%d\', dob) >= 1 AND strftime(\'%Y.%m%d\', \'now\') - strftime(\'%Y.%m%d\', dob) < 3')
    youngPets = pet_cursor.fetchall()
    return render_template('index.html', user=cur_user, youngPets=youngPets, filterType='youngPets')


# Filter by age: adult (3-5)
@app.route('/adultPets')
def filter_adultPets():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute(
        'SELECT * FROM Pets WHERE strftime(\'%Y.%m%d\', \'now\') - strftime(\'%Y.%m%d\', dob) >= 3 AND strftime(\'%Y.%m%d\', \'now\') - strftime(\'%Y.%m%d\', dob) < 5')
    adultPets = pet_cursor.fetchall()
    return render_template('index.html', user=cur_user, adultPets=adultPets, filterType='adultPets')


# Filter by age: senior (5+)
@app.route('/seniorPets')
def filter_seniorPets():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute('SELECT * FROM Pets WHERE strftime(\'%Y.%m%d\', \'now\') - strftime(\'%Y.%m%d\', dob) >= 5')
    seniorPets = pet_cursor.fetchall()
    return render_template('index.html', user=cur_user, seniorPets=seniorPets, filterType='seniorPets')


# -----------------------------------------------------------------------------------------------------------#

# when people apply to adopt or volunteer, they get registered in the system
# because they need to see the status of the application.
# have to add a 'type' attribute for the users: volunteer application or adoption application.
# if approved -->

"""
@app.route('/managepets')
def managepets():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute('SELECT * from Pets')
    all_pets = pet_cursor.fetchall()
    numInQueue = numberOfPets()
    return render_template('managepets.html', user=cur_user, all_pets=all_pets, numInQueue=numInQueue)
"""
# Changes to the original function above, this will allow the user to input a name for the pet and search for it
@app.route('/managepets', methods=['POST', 'GET'])
def managepets():
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute('SELECT * from Pets')
    all_pets = pet_cursor.fetchall()
    numInQueue = numberOfPets()
    user_privilage = db.execute("SELECT * FROM Users WHERE (privilage = 'admin' AND status = 'active')")
    privilage = user_privilage.fetchall()
    kennel_amt_cursor = db.execute("SELECT count(*) from Kennels WHERE status = 'empty'")
    kennel_amt = kennel_amt_cursor.fetchone()

    all_kennels = db.execute("SELECT * from Kennels where status = 'empty'")
    all_kennels = all_kennels.fetchall()
    # If the user types a name or letter into the searchbox, finds animal with that name or which starts with that name/letter
    if request.method == 'POST':
        petName = request.form['searchName']
        cursor = db.execute('SELECT * FROM Pets WHERE pname LIKE ?', (petName + '%',))
        all_pets = cursor.fetchall()

    return render_template('managepets.html', all_kennels=all_kennels, kennel_amt=kennel_amt, user=cur_user, all_pets=all_pets, numInQueue=numInQueue, privilage = privilage)

@app.route('/decline/<int:id>', methods=['POST', 'GET'])
def decline(id):
    cur_user = get_current_user()
    db = get_database()

    # if application is declined, status changes to declined.
    # animal is back to available.

    db.execute("UPDATE Applicants SET status = 'declined' WHERE id = ?", [id])
    db.commit()
    db = get_database()
    db.execute("UPDATE Pets SET status = 'available' WHERE pid = (SELECT pet FROM Applicants WHERE id = ?)", [id]);
    db.commit()
    return redirect(url_for('manageapplications', user=cur_user))

@app.route('/approve/<int:id>', methods=['POST', 'GET'])
def approve(id):
    cur_user = get_current_user()
    db = get_database()

    # if application is approved, pet status - adopted, application - approved.

    db.execute("UPDATE Applicants SET status = 'approved' WHERE id = ?", [id])
    db.commit()
    db = get_database()
    db.execute("UPDATE Pets SET status = 'adopted' WHERE pid = (SELECT pet FROM Applicants WHERE id = ?)", [id]);
    db.commit()

    db = get_database()
    db.execute("update Kennels set status = 'empty' where id in (select kennel_id from Pets where status = 'adopted')")
    db.execute("update Pets set kennel_id = NULL where status = 'adopted'")
    #db = get_database()
    #db.execute("UPDATE Users SET privilage = 'admin' WHERE id = ?", [id]);
    #db.commit()

    # Add applicant to Adopter table, will not allow duplicate Adopters + pets combination (same adopter can adopt different pets though)
    #db.execute('INSERT INTO Adopters (id, pid, name, phone, address, employment, dob, dateOfAdoption) SELECT id, pet, name, phone, address, employment, dob, CURRENT_DATE FROM Applicants WHERE id = ? AND NOT EXISTS (SELECT id, pid FROM Adopters A WHERE id = A.id AND pid = A.pid)', [id])
    
    # Add applicant to Adopter table
    db.execute('INSERT INTO Adopters (id, pid, name, phone, address, employment, dob, dateOfAdoption) SELECT id, pet, name, phone, address, employment, dob, CURRENT_DATE FROM Applicants WHERE id = ?', [id])
    db.commit()
    
    # Remove applicant from Applicant table, checks if added to adopters table first
    #db.execute("DELETE FROM Applicants WHERE id = ? AND EXISTS (SELECT * FROM Adopters A WHERE A.id = id)", [id])
    #db.commit()

    return redirect(url_for('manageapplications', user=cur_user))


# Get the total number of pets
def numberOfPets():
    db = get_database()
    pet_cursor = db.execute('SELECT COUNT(*) FROM Pets')
    if pet_cursor != None:
        num = pet_cursor.fetchone()
        numPets = num[0]
    else:
        numPets = 0
    return numPets

app.config['UPLOAD_FOLDER'] = "static\images"

@app.route('/add', methods=['POST'])
def add():
    db = get_database()
    cur_user = get_current_user()
    if request.method == 'POST':
        name = request.form['name']
        sex = request.form['sex']
        dob = request.form['dob']
        dateofintake = request.form['dateofintake']
        description = request.form['description']
        type = request.form.get('type')
        image = request.files['image']

        if image.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(filepath)
        # WORKS PERFECTLY 6/27
        empty_cursor = db.execute(" select id from Kennels where status = 'empty'")
        empty_kennel = empty_cursor.fetchone()
        if empty_kennel:
            db.execute("insert into Pets (kennel_id, pname, sex, dob, dateofintake, description, type, image)"
                   "values (( select id from Kennels where status = 'empty' limit 1), ?,?,?,?,?,?,?)", [name, sex, dob, dateofintake, description, type, image.filename])
            db.execute("update Kennels set status = 'busy' where id in (select kennel_id from Pets)")
            db.commit()
            flash("Pet Added Successfully")
        else:
            flash("I`m sorry, there are no more kennels, a pet can not be added at this time.")

        return redirect(url_for('managepets'))


@app.route('/update', methods=['GET', 'POST'])
def update():
    cur_user = get_current_user()
    db = get_database()
    if request.method == 'POST':
        pid = request.form.get('pid')
        name = request.form.get('name')
        sex = request.form.get('sex')
        dob = request.form.get('dob')
        dateofintake = request.form.get('dateofintake')
        description = request.form.get('description')
        image = request.files['image']

        print(image.filename)

        if image.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(filepath)
            db.execute('UPDATE Pets SET pname = ?, sex = ?, dob = ?, dateofintake = ?, description = ?, image = ?'
                       'WHERE pid = ?', [name, sex, dob, dateofintake, description, image.filename, pid])
            db.commit()

        if image.filename == '':
            db.execute('UPDATE Pets SET pname = ?, sex = ?, dob = ?, dateofintake = ?, description = ? '
                       'WHERE pid = ?', [name, sex, dob, dateofintake, description, pid])
            db.commit()

        flash('Pet updated successfully!')

        return redirect(url_for('managepets'))


# simple delete, default HTTP method = GET
@app.route('/delete/<pid>/', methods=['POST', 'GET'])
def delete(pid):
    cur_user = get_current_user()
    db = get_database()
    # update status of the kennel
    # delete
    db.execute('DELETE FROM Pets WHERE pid = ?', [pid])
    db.execute("UPDATE Kennels set status = 'empty' where ID NOT IN ( SELECT kennel_id FROM Pets ) ")
    db.commit()

    flash("Deleted successfully!")

    return redirect(url_for('managepets'))


@app.route('/petprofile/<int:pid>')
def petprofile(pid):
    cur_user = get_current_user()
    db = get_database()
    pet_cursor = db.execute('SELECT * from Pets WHERE pid = ?', [pid])
    single_pet = pet_cursor.fetchone()
    # Check if it's the pets birthday today, if so get their age
    isBirthdayToday = isBirthday(single_pet)
    if isBirthdayToday == True:
        petAge, suffix = getAge(single_pet)
    else:
        petAge = 0
        suffix = ""

    return render_template('pet-profile.html', user=cur_user, single_pet=single_pet, isBirthdayToday=isBirthdayToday, petAge=petAge, suffix=suffix)


# Check if it's the pet's birthday when the user clicks on a pet
def isBirthday(pet):
    db = get_database()
    # There wasn't DATE_PART in sqlite3 so I had to use strftime instead
    petCursor = db.execute(
        f'SELECT * FROM Pets WHERE strftime(\'%d%m\', dob) = strftime(\'%d%m\', \'now\') AND pid = ?', (pet[0],))
    birthdayPet = petCursor.fetchone()
    if birthdayPet != None:
        return True
    else:
        return False


# Get the pet's age
def getAge(pet):
    db = get_database()
    # Used cast to turn the age into an int since it would be a float otherwise
    petCursor = db.execute(
        f'SELECT CAST(strftime(\'%Y.%m%d\', \'now\') - strftime(\'%Y.%m%d\', dob) AS int) FROM Pets WHERE pid = ?',
        (pet[0],))
    age = petCursor.fetchone()

    # Add 'th'/'nd'/'st'/'rd' at end (ex. 3rd or 14th birthday)
    if (age[0] == 1 or ((age[0] % 10) - 1 == 0)  and age[0] != 11):
        suffix = "st"
    elif (age[0] == 2 or ((age[0] % 10) - 2 == 0) and age[0] != 12):
        suffix = "nd"
    elif (age[0] == 3 or ((age[0] % 10) - 3 == 0) and age[0] != 13):
        suffix = "rd"
    else:
        suffix = "th"

    return age, suffix


@app.route('/volunteer')
def volunteer():
    cur_user = get_current_user()
    db = get_database()
    user_privilage = db.execute("SELECT * FROM Users WHERE (privilage = 'admin' AND status = 'active') ")
    privilage = user_privilage.fetchall()
    return render_template('volunteerapplication.html', user=cur_user, privilage = privilage)


@app.route('/managevolunteers')
def managevolunteers():
    db = get_database()
    user_privilage = db.execute("SELECT * FROM Users WHERE (privilage = 'admin' AND status = 'active')")
    privilage = user_privilage.fetchall()
    cur_user = get_current_user()
    nameOfApplicantPet = db.execute("Select pname From Pets Where pid in (Select pet From Applicants WHERE id in (Select id From Users ORDER BY id DESC LIMIT 1))")
    ApplicantPet = nameOfApplicantPet.fetchone()
    nameOfApplicant = db.execute("SELECT name FROM Applicants WHERE id IN ( SELECT id FROM Users ORDER BY id DESC LIMIT 1)")
    Applicant = nameOfApplicant.fetchone()
    
    return render_template('managevolunteers.html', user=cur_user, privilage = privilage, ApplicantPet =ApplicantPet, Applicant = Applicant)


@app.route('/manageapplications')
def manageapplications():
    cur_user = get_current_user()
    db = get_database()
    #appl_cursor = db.execute('SELECT * FROM Applicants')
    appl_cursor = db.execute('SELECT * FROM Applicants WHERE status = \'pending\'')
    allApplicants = appl_cursor.fetchall()
    numInQueue = numberOfApplicants('pending')
    pet_cursor = db.execute('SELECT pname, pid FROM Pets INNER JOIN Applicants where pet = pid')
    user_privilage = db.execute("SELECT * FROM Users WHERE (privilage = 'admin' AND status = 'active') ")
    privilage = user_privilage.fetchall()
    allPets = pet_cursor.fetchall()
    return render_template('manageapplications.html', numInQueue=numInQueue, allApplicants=allApplicants,
                           allPets=allPets, user=cur_user, privilage = privilage)

# Get denied applications
@app.route('/manageapplications/denied')
def getDeniedApplicants():
    cur_user = get_current_user()
    db = get_database()
    cursor = db.execute('SELECT * FROM Applicants WHERE status = \'declined\'')
    allApplicants = cursor.fetchall()
    numInQueue = numberOfApplicants('declined')
    pet_cursor = db.execute('SELECT pname, pid FROM Pets INNER JOIN Applicants where pet = pid')
    allPets = pet_cursor.fetchall()

    # Added this
    user_privilage = db.execute("SELECT * FROM Users WHERE (privilage = 'admin' AND status = 'active') ")
    privilage = user_privilage.fetchall()
    return render_template('manageapplications.html', numInQueue=numInQueue, user=cur_user, allApplicants=allApplicants, allPets=allPets, privilage=privilage)

@app.route('/status/')
def status():
    db = get_database()
    cur_user = get_current_user()
    cursor = db.execute('Select name From Applicants Where id in (Select id From Users WHERE status = "active")')
    user_name = cursor.fetchone()
    pet_cursor = db.execute('Select pname From Pets Where pid in (Select pet From Applicants WHERE id in (Select id From Users WHERE status = "active") )')
    pet_name = pet_cursor.fetchone()
    user_privilage = db.execute("SELECT * FROM Users WHERE (privilage = 'admin' AND status = 'active')")
    privilage = user_privilage.fetchall()
    # get name of the pet they applied for
    # pet_cursor = db.execute('SELECT pname from Pets WHERE pid IN ( SELECT * FROM Applicants where pid = pet')

    # display person`s name with Hello, nameOfPerson.
    # Thank you for applying to adopt nameOfPets.
    # Here is the status of your application:
    return render_template('status.html', user_name = user_name, pet_name = pet_name, privilage = privilage)

# Manage the adopters
@app.route('/manageadopters', methods=['POST', 'GET'])
def manageAdopters():
    cur_user = get_current_user()
    db = get_database()
    #cursor = db.execute("SELECT * FROM Applicants WHERE status = 'approved'")
    #approvedApplicants = cursor.fetchall()
    user_privilage = db.execute("SELECT * FROM Users WHERE (privilage = 'admin' AND status = 'active') ")
    privilage = user_privilage.fetchall()

    # Select adopter info
    cursor = db.execute("SELECT A.id, P.pname, A.name, A.phone, A.employment, A.dob, A.dateOfAdoption FROM Adopters A, Pets P WHERE A.pid = P.pid")
    allAdopters = cursor.fetchall()
    numInQueue = numAdopters()

    # If searching for name of adopter or pet
    if request.method == 'POST':
        findNames = request.form['searchNames']
        cursor = db.execute("SELECT A.id, P.pname, A.name, A.phone, A.employment, A.dob, A.dateOfAdoption FROM Adopters A, Pets P WHERE A.pid = P.pid AND (P.pname LIKE :f OR A.name LIKE :f)", {"f": findNames + '%'})

        allAdopters = cursor.fetchall()

    # Remove
    #remove_add_adopters()
    
    return render_template('manageadopters.html', user=cur_user, allAdopters=allAdopters, numInQueue=numInQueue, privilage = privilage)

# Get the total number of adopters
def numAdopters():
    db = get_database()
    cursor = db.execute("SELECT COUNT(*) FROM Adopters")
    if cursor != None:
        num = cursor.fetchone()
        numAdopters = num[0]
    else:
        numAdopters = 0
    return numAdopters

# Count number of applicants based on status (pending, approved, or declined)
def numberOfApplicants(status):
    db = get_database()
    pet_cursor = db.execute('SELECT COUNT(*) FROM Applicants WHERE status = ?', (status,))
    if pet_cursor != None:
        num = pet_cursor.fetchone()
        numApplicants = num[0]
    else:
        numApplicants = 0
    return numApplicants

"""
# If reseting (can remove this function later)
# I used this to add all of the existing approved applicants to Adopters database + removing the from Applicants table
# Will only need to run once
def remove_add_adopters():
    db = get_database()
    # Add applicants to Adopter table, will not allow duplicate Adopters + pets combination (same adopter can adopt different pets though)
    db.execute('INSERT INTO Adopters (id, pid, name, phone, address, employment, dob, dateOfAdoption) SELECT id, pet, name, phone, address, employment, dob, CURRENT_DATE FROM Applicants WHERE status = \'approved\'')
    db.commit()
    
    # Remove applicant from Applicant table
    #db.execute("DELETE FROM Applicants WHERE status = \'approved\'")
    #db.commit()
"""

if __name__ == "__main__":
    app.run(debug=True)
