# google-hashcode 2018

## Pizza
* __Greedy algorithm__ which cuts a given pizza slice by slice.
* It cuts slices from top left corner to bottom right corner preferring the biggest possible.
* This approach reaches a total __score of 901.008__.

## Streaming videos
* __Greedy approach__ to find initial solution:
    1. rate each possible (video, cache) combination by latency saving potential
    2. iterate over caches and assign not cached videos in order of rating for this cache
* __Local search algorithm__ to improve initial solution

## Self-driving rides
* __Greedy algorithm__ simulating time step by step while assigning each available vehicle the best possible ride
* This approach reaches a total __score of 46.571.051__.
 