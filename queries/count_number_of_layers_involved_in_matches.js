db.getCollection('pat_match_unified').aggregate([
    {
        $group:{
            "_id": { uid : "$uid" },
            "matches": {$sum: 1}
        }
    },
    {
        $project:{
            "_id": 0,
            uid: "$_id.uid",
            matches: "$matches"
        }
    },
     { $group: { _id: null, myCount: { $sum: 1 } } },
       { $project: { _id: 0 } }
    
    ], {allowDiskUse:true})