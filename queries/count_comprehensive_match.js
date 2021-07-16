db.getCollection('pat_match_unified').aggregate([
    {
        $group:{
            "_id": { matchid : "$matchid" },
            "players": {$sum: 1}
        }
    },
    {
        $project:{
            "_id": 0,
            matchid: "$_id.matchid",
            players: "$players"
        }
    },
    {
        $match:{
            players: 10
        }
    },
     { $group: { _id: null, myCount: { $sum: 1 } } },
       { $project: { _id: 0 } }
    
    ])