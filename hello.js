const MongoClient = require('mongodb').MongoClient;
MongoClient.connect('mongodb+srv://dbadmin:mahesh123@cluster0.lijkf.mongodb.net/sample_airbnb?retryWrites=true&w=majority', function(err, client) {
    if (err) throw err;

    let db = client.db('users');
    db.collection('usersCollection').find().toArray(function(err, result) {
        if (err) throw err;
        console.log(result[0]);
        client.close();
    });
});