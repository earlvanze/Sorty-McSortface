var fbadmin = require('firebase-admin')
var serviceAccount = require('./firebase_private_key.json')

var status = process.argv[2];

fbadmin.initializeApp({
    credential: fbadmin.credential.cert(serviceAccount),
    databaseURL: 'https://sorty-mcsortface.firebaseio.com/'
})

var ref = fbadmin.database().ref('/');

ref.update({'status': status}, (response) => {
    fbadmin.database().goOffline();
    fbadmin.app().delete();
});
