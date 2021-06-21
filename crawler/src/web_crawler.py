import sys
import lxml.html
import urllib.request
from urllib.parse import urlparse
from collections import deque

def build_link_url(protocol, domain, path, query):
    parsed_link = protocol + "://" + domain + path
    if bool(query):
        parsed_link = parsed_link + "?" + query
    return parsed_link

def parse_link_url(current_url_details, link):
    link_details = urlparse(link)
    is_absolute = bool(link_details.netloc)
    parsed_link = ""
    domain = ""
    if is_absolute:
        domain = link_details.netloc
        protocol = link_details.scheme if bool(link_details.scheme) else "https"
        parsed_link = build_link_url(protocol, 
                                     domain, 
                                     link_details.path, 
                                     link_details.query)
    else:
        domain = current_url_details.netloc
        parsed_link = build_link_url(current_url_details.scheme, 
                                     domain,
                                     link_details.path,
                                     link_details.query)
    return {"link": parsed_link,
            "domain": domain}

def get_page_links(current_url):
    try:
        connection = urllib.request.urlopen(current_url)
    except:
        return []# broken link
    dom =  lxml.html.fromstring(connection.read())
    ans = []
    current_url_details = urlparse(current_url)
    for link in dom.xpath('//a/@href'):
        ans.append(parse_link_url(current_url_details, link))
    return ans

def get_page_rank(current_domain, parsed_links):
    if not bool(parsed_links):
        return 0
    current_domain_counter = 0
    for link in parsed_links:
        if link["domain"] == current_domain:
            current_domain_counter += 1
    return current_domain_counter / len(parsed_links)

def append_to_file(urls):
    with open("result.tsv", "a") as myfile:
        for url,info in urls.items():
            myfile.write("{}\t{}\t{}".format(url,info["depth"],info["rank"]))
            myfile.write("\n")

def init_result_file():
    with open('result.tsv', 'w') as myfile:
        myfile.write("url" + "\t" + "depth" + "\t" + "rank")
        myfile.write("\n")

def process_page(current_url, queue, cache):
    cache.add(current_url)
    parsed_links = get_page_links(current_url)
    current_domain = urlparse(current_url).netloc
    rank = get_page_rank(current_domain, parsed_links)
    return rank, parsed_links

def main(root, depth):
    urls = {}
    cache = set()
    queue = deque([root])
    batch_size = 10
    init_result_file()
    #BFS until we reach the given depth
    for iteration in range(depth):
        n = len(queue)
        for i in range(n):# on each iteration we only want to process the urls we enqueued in the last one
            url = queue.popleft()
            if url not in cache:#if its not in cache its new and we need to process it
                rank, parsed_links = process_page(url, queue, cache)
                urls[url] = {"rank": rank, "depth": iteration + 1}
            if iteration < depth - 1:#if we havent reached depth add to queue
                queue.extend([link["link"] for link in parsed_links if link["link"] not in cache])
            if len(urls) == batch_size:# write in batches to minimize IO
                append_to_file(urls)
                urls = {}
    append_to_file(urls)

if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))