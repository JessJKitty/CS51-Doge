#!/usr/bin/env python

import cgi
import cgitb; cgitb.enable()  # for troubleshooting


print "Content-type: text/html"

print

print """
<html>

<head><title>Sample CGI Script</title></head>

<body>

  <h3> Sample CGI Script </h3>
"""

form = cgi.FieldStorage()
message = form.getvalue("message", "(no message)")

try:

    import pickle
    from Doge_response import doge_response
    from Iteration import init_normalize
    all_POS = pickle.load (open("pos.p", "r"))
    POS_basefreqs = init_normalize(all_POS)

    word_POS_freqs = pickle.load (open("words.p", "r"))
    transition_probs = pickle.load (open("combos.p", "r"))

    response = doge_response(message, word_POS_freqs, transition_probs)

    print """
      <p>You: %s</p>
      <p>Doge: %s </p>

      <p>form

      <form method="post" action="play.cgi">
        <p>message: <input type="text" name="message"/></p>
      </form>

    </body>

    </html>""" % (cgi.escape(message), response)

except:
    #pass
    import sys, traceback
    traceback.print_exc(file=sys.stdout)

