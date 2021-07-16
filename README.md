# league of legend data
The goal of the data downloading is to get the comprehensive set of friendships of the each concerned player. 
The process should be:
1. For each player, we get all the matches it played.
2. From each match we get for this player, we extract all the players.
3. We then calculate the friendship of this particular player.
4. Then for all the players who are in same match we extracted, we repeat from step 1.

A player's data is comprehensive when we have all the matches it plays.
A match's data is comprefhensive when we have all the players's friendship count, which requires all the matches these players has played.

Each player normally play hundreds of matches, the above algorithm will cause quick explosion of the number of matches and players we need to download. In order to quickly get comprehensive set of matches and players, we should first download the matches that has smllest number of missing players. The pat_match_unified should be the one that can provide this.