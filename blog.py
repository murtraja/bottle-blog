from bottle import route, get, post, template, request
import bottle, os
from pymongo import MongoClient
DBNAME = 'TE3146db'
USERNAME = 'TE3146'
PASSWORD = 'TE3146'
HOSTNAME = \
'localhost'
# '192.168.4.91'
PORT = '27017'

redirect_message = ''
choose_new_username=''
connection_string= \
'mongodb://'+USERNAME+':'+PASSWORD+'@'+HOSTNAME+':'+PORT+'/'+DBNAME
# 'mongodb://TE3146:TE3146@192.168.4.91:27017/TE3146db'
# mongodb://[username:password@]host1[:port1]

@route('/')
def root():
    return template("root_template")

@get('/signup')
def signup_get():
    global choose_new_username
    msg = choose_new_username
    choose_new_username = ""
    return template('signup_template', msg = msg)

@post('/signup')
def signup_post():
    username =request.forms.get("username")
    pword = request.forms.get("password")
    
    
    connection = MongoClient(connection_string)
    col = connection[DBNAME].user
    # add the logic of checking whether the user is already present or not
    user_match = col.find({'username':username})
    leng = len(list(user_match))
    print 'length of user_match',leng
    if not leng:        
        col.insert({'username':username, 'password':pword})
        
        global redirect_message
        redirect_message = username+' available. Account created successfully!'
        return bottle.redirect("/signin")
    global choose_new_username
    choose_new_username = username+' already taken! Please choose a new username.'
    return bottle.redirect('/signup')
    
@get('/signin')
def signin_get():
    global redirect_message
    redirected = redirect_message
    redirect_message = ''
    return template('signin_template', redirected = redirected)

@post('/signin')
def signin_post():
    username =request.forms.get("username")
    pword = request.forms.get("password")
    
    
    connection = MongoClient(connection_string)
    col = connection[DBNAME].user
    users = col.find()
    for user in users:
        if user['username']==username and user['password']==pword:
            return bottle.redirect('/blog')
    global redirect_message
    redirect_message = 'User and password mismatch'
    return bottle.redirect('/signin')

@get('/blog')
def blog_get():
    connection = MongoClient(connection_string)
    col = connection[DBNAME].blog
    blogs = col.find()
    

    global redirect_message
    redirected = redirect_message
    redirect_message = ''

    return template('blog_template', blogs= blogs, redirected = redirected)

@post('/blog')
def blog_post():
    blog_title = request.forms.get('title')
    blog_content = request.forms.get("content")
    file_post = request.files.get('image_file')
    blogmap = {'title':blog_title, 'content':blog_content}
    print "file_post:", file_post
    if file_post:
        fname,ext = os.path.splitext(file_post.filename)
        fobj = file_post.file
        print 'fname:',fname,"ext:",ext
        print 'fileobject:',fobj
        # print 'file contents:'
        fcontents = fobj.read()
        # print fcontents
        print 'totalbytes:',len(fcontents)
        fenc = fcontents.encode('base64')
        blogmap.update({'image':fenc})

    connection = MongoClient(connection_string)
    col = connection[DBNAME].blog

    col.insert_one(blogmap)

    global redirect_message
    redirect_message = 'blog '+blog_title+' added!'
    return bottle.redirect('/blog')   




bottle.debug(True)
bottle.run(host='localhost', port = 7860)