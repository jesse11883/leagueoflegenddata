//get pat-connect count
var ret = db.getCollection('pat_connection_count').aggregate(
    [
    
    {"$group" : {_id:"$count", count:{$sum:1}}},
    {"$project": { _id: 0, 
                          'friends': '$_id', "total":'$count' }},
    
    {"$sort": {"friends":1}}
    
    ]

    )
    
    ret.forEach(function(result) {
        print(result.friends+"|"+result.total);
    }
);

