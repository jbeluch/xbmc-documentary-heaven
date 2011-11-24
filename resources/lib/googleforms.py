from urllib import urlopen, urlencode


def _post(url, data):
    '''Makes a POST request to the given url with the data payload.'''
    conn = urlopen(url, data)
    resp = conn.read()
    conn.close()
    return resp


def report_broken_url(url):
    '''Submits a google form via a POST request.'''
    form_url = 'https://docs.google.com/spreadsheet/formResponse?formkey=dDJWY3hOZEtWVlYwNWJZUUVGUjd3cnc6MQ&ifq'
    params = {'entry.0.single': url, 'pageNumber': 0, 'backupCache': '',
              'submit': 'Submit'}
    return _post(form_url, urlencode(params))
