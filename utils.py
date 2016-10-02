from flask import session


def perform_login(id, email, username):
	try:
		session['uid'] = id
		session['email'] = email
		session['username'] = username

		print "User:",username,"logged in."
	except Exception as e:
		print 'Cannot login:',e
		return False
	else:
		return True
