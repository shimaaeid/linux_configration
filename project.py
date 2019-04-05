from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from flask import make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from catalog_database import Base, Category, Item, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import httplib2
import json
import requests
app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('g_client_secrets.json', 'r').read())['web']['client_id']
# Create anti-forgery state token


@app.route('/login')
def showLogin():
    if 'username' in login_session:
        flash('You are already logged in.')
        return redirect('/')
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session = DBSession()
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


def getUserInfo(user_id):
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).first()
    return user


def getUserID(email):
    session = DBSession()
    try:
        user = session.query(User).filter_by(email=email).first()
        if user:
            return user.id
        else:
            return None
    except 'error':
        return None

# GOOGLE SIGN


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'g_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'
    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome,'
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px;height: 300px;border-radius: 150px;">'
    output += '"-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?'
    url += 'token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(
            json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/')
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# FACEBOOK SIGN


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(
            json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token
    app_id = json.loads(open(
        'fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open(
        'fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?'
    url += 'grant_type=fb_exchange_token&client_id=%s' % app_id
    url += '&client_secret=%s' % app_secret
    url += '&fb_exchange_token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token
        exchange we have to split the token first on commas and
        select the first index which gives us the key : value
        for the server access token then we split it on colons
        to pull out the actual token value and replace the remaining
        quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')
    url = 'https://graph.facebook.com/v2.8/me?'
    url += 'access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token
    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s'
    url += '&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]
    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;"> '
    output += ' " style = border-radius:150px;-webkit-border-radius: 150px;"> '
    output += ' " style = -moz-border-radius: 150px;"> '
    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?'
    url += 'access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['username']
    del login_session['email']
    del login_session['user_id']
    del login_session['facebook_id']
    return "you have been logged out"

# Disconnect based on provide


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()
        flash("You have successfully been logged out.")
        return redirect('/')
    else:
        flash("You were not logged in")
        return redirect('/')

# JSON APIs to view categories Information


@app.route('/json/categories')
def jsonCategories():
    session = DBSession()
    categories = session.query(Category).all()
    return jsonify(categories=[category.serialize for category in categories])


@app.route('/json/categories/<int:category_id>')
def jsonCategory(category_id):
    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).first()
    return jsonify(category=[category.serialize])


@app.route('/json/categories/<int:category_id>/items')
def jsonCategoryItems(category_id):
    session = DBSession()
    items = session.query(Item).filter_by(category_id=category_id)
    return jsonify(items=[item.serialize for item in items])


@app.route('/json/categories/<int:category_id>/items/<int:item_id>')
def jsonItem(category_id, item_id):
    session = DBSession()
    item = session.query(Item).filter_by(id=item_id).first()
    return jsonify(item=[item.serialize])


@app.route('/categories/new', methods=['POST'])
def addCategoryJson():
    # Add a new Item.
    session = DBSession()
    print "session created."
    name = request.json.get('name')
    description = request.json.get('description')
    user_id = request.json.get('user_id')
    category = Category(name=name, description=description, user_id=user_id)
    session.add(category)
    session.commit()
    return redirect('/', code=200)
# Show main page


@app.route('/')
@app.route('/catalog')
@app.route('/categories')
def catalog():
    session = DBSession()
    categories = session.query(Category).limit(6).all()
    latestItems = session.query(Item).all()
    if len(latestItems) > 10:
        latestItems = reversed(latestItems[len(latestItems) - 10:])
    else:
        latestItems = reversed(session.query(Item).limit(10).all())
    return render_template(
        'catalog.html', categories=categories,
        latestItems=latestItems, login_session=login_session)
# the category page for specifec 'id'


@app.route('/categories/<int:category_id>')
@app.route('/categories/<int:category_id>/items')
def category(category_id):
    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).first()
    items = session.query(Item).filter_by(category=category).all()
    categories = session.query(Category).all()
    return render_template(
        'catalog-items.html', category=category,
        categories=categories, items=items, login_session=login_session)

# Show Items


@app.route('/categories/<int:category_id>/items/<int:item_id>')
def showItems(category_id, item_id):
    session = DBSession()
    item = session.query(Item).filter_by(
        category_id=category_id, id=item_id).one()
    if item:
        return render_template(
            'item.html', item=item, login_session=login_session)
    return None


@app.route('/addItem', methods=['POST', 'GET'])
def addItem():
    if not login_session['username']:
        flash('You have to login first.')
        return redirect('/')
    session = DBSession()
    if request.method == 'GET':
        categories = session.query(Category).all()
        return render_template(
            'add_item.html', categories=categories)
    else:
        name = request.form['name']
        description = request.form['description']
        category_id = request.form['category_id']
        if not name:
            flash('No name found')
            return redirect('/addItem')
        if not description:
            flash('No description found')
            return redirect('/addItem')
        newItem = Item(
                        name=name,
                        description=description,
                        category_id=category_id,
                        user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('item added successfully')
        return redirect('/categories/' + str(newItem.category_id))


@app.route('/categories/<int:category_id>/items/<int:item_id>/edit',
           methods=['POST', 'GET'])
def editItem(category_id, item_id):
    # edit item
    if 'username' not in login_session:
        flash('You have to login first.')
        return redirect('/')
    session = DBSession()
    item = session.query(Item).filter_by(id=item_id).first()
    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category_id']:
            item.category_id = request.form['category_id']
        session.add(item)
        session.commit()
        return redirect(
            '/categories/' + str(item.category_id) + '/items/' + str(item.id))
    categories = session.query(Category).all()
    return render_template('edit_item.html', item=item, categories=categories)


@app.route('/categories/<int:category_id>/items/<int:item_id>/delete',
           methods=['POST', 'GET'])
def deleteItem(category_id, item_id):
    if 'username' not in login_session:
        flash('You have to login first.')
        return redirect('/')
    session = DBSession()
    item = session.query(Item).filter_by(id=item_id).first()
    if login_session['user_id'] != item.user_id:
        flash("You can't delete this item, create your own item")
        return redirect('/')
    if request.method == 'GET':
        return render_template('delete_item.html', item=item)
    else:
        session.delete(item)
        session.commit()
        flash('item deleted successfully.')
        return redirect('/categories/' + str(category_id))

# this route to delete something.


@app.route('/del')
def deleteCat():
    session = DBSession()
    items = session.query(Category).all()
    for item in items:
        if 'test' in item.name:
            session.delete(item)
            session.commit()
    return redirect('/categories')


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
