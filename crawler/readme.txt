Basic web crawler written in python3
====================================
* Sadly I only managed to create a working solution in the 3 hours I worked.
 I had no time to add optimizations, think of all the extreme cases and to refactor properly.
* Please consider the fact that while I do have experience in python, for the last two years I am not using it at work.
* a broken link has no links in it so its rank would be 0


- The main algorithm we are using in order to scan the web is BFS. 
we are scanning until we reach the requested depth and then we stop.

- This is a basic solution, it is not production ready and it has many limitations.
  some of those limitations are:
    - Relying on a queue data structure that is limited by ram size.
    - Writing to a file instead of DB.
    - Very basic url parsing logic.
    - Using a simple set for a cache instead of an implementation of an LRU cache (time limit)
    - This code is a bit naive and is using only the power of one core.

- General Design:
    Main algorithm:
    Using a BFS search
    - for each page:
        - get the dom of the page
        - scrape all the links of the page
        - parse the links
        - calculate the rank of the page
        - append the links to the BFS queue and move on
    
    Caching:
        Adding to the cache each new url that we parsed. Checking the cache in the following cases:
            - before starting to parse a new url
            - before adding a url to the queue
    
    Write buffer
        - We have a buffer of processed urls and we are writing the urls to the file in batches.

A much more optimal Design would have had the following optimizations:
    - LRU cache instead of a simple set (would have added if I had more time)
    - Kafka or some other distributed queuing tech.
    - write buffer that runs in a different thread/process/service (would have added if I had more time)
    - DB instead of file
    - using a multiprocess design to use more then one core of each machine (would have added if I had more time)
        process may be a thread in the actual implementation.
        - would have had a dedicated process (may be more then one) that handles a queue of messages it should write
        - would have used multiple processes that are parsing urls in parallel, each parser thread would push
        its final result to the writer queue.
        - parser processes would share the BFS queue and the cache.


