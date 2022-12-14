import os
import time
from py2neo import Graph
from py2neo.bulk import create_nodes, create_relationships
from classes import Author, Article
from clean import cleanString
import ijson
import datetime
import tracemalloc

JSON_FILE = os.environ['JSON_FILE']
CLEANED_FILE = os.environ['CLEANED_FILE']
MAX_NODES = int(os.environ['MAX_NODES'])
NEO4J_IP = os.environ['NEO4J_IP']

# Debug tests
# JSON_FILE = "db.json"
# CLEANED_FILE = "dblpExampleCleanedTest.json"
# MAX_NODES = 10000
# NEO4J_IP = "localhost"


def preprocessJson(jsonFile):
    """Preprocess the json file to get all the authors and articles
    jsonFile: str
    return: list[Author], list[Article]
    """
    authors: list[Author] = []
    articles: list[Article] = []
    with open(jsonFile, 'rb') as f:
        i = 0
        for record in ijson.items(f, 'item'):
            authorsArray = []
            if "authors" in record:
                tmp = record["authors"]
                # go through all the authors
                for j in range(len(tmp)):
                    _id, name = "", ""
                    if ("_id" in tmp[j]):
                        _id = tmp[j]["_id"]
                        if (_id == '' or _id == ""):
                            continue
                    else:
                        continue
                    if ("name" in tmp[j]):
                        name = tmp[j]["name"]
                    author = Author(_id, name)
                    authorsArray.append(author._id)
                    # TODO could be optimized by using a set instead of a list
                    if (not any(author._id == a._id for a in authors)):
                        authors.append(author)
            # extract articles
            tmp = record
            _id, title, references = "", "", [] 
            if ("title" in tmp ):
                title = tmp["title"]
            if ("_id" in tmp):
                _id = tmp["_id"]
            if ("references" in tmp):
                references = tmp["references"]
            article = Article(_id, title, authorsArray, references)
            articles.append(article)
            i += 1
            if (i == MAX_NODES):
                break
        print('Done!')
    return authors, articles



def writeInDb(authors, articles, graph):
    """Write the data in the database
    authors: list[Author]
    articles: list[Article]
    graph: Graph
    """
    # create all the authors nodes and add them to the graph. 
    print("Creating authors nodes data")
    keys_authors = ['_id', 'name']
    data_authors = []
    # create the data array for the authors
    for i in range(len(authors)):
        data_authors.append([authors[i]._id, authors[i].name])
    print("Creating authors nodes in DB")
    create_nodes(graph, data_authors,  labels={'Author'}, keys=keys_authors)
    
    # create the articles nodes and add them to the graph
    print("Creating articles nodes data")
    keys_articles = ['_id', 'title']
    data_articles = []
    # create the data array for the articles
    for i in range(len(articles)):
        data_articles.append([articles[i]._id, articles[i].title])
    print("Creating articles nodes in DB")
    create_nodes(graph, data_articles,  labels={'Article'}, keys=keys_articles)

    # create the relationships between the articles and the authored : AUTHORED
    print("Creating relationship AUTHORED...")
    start_node_key_authored = ("Author", "_id")
    end_node_key_authored = ("Article", "_id")
    data_authored = []

    for i in range(len(articles)):
        for j in range(len(articles[i].authors)):
            data_authored.append((articles[i].authors[j], {}, articles[i]._id))
    print("Creating relationship AUTHORED in DB")
    create_relationships(graph, data_authored, "AUTHORED", start_node_key=start_node_key_authored, end_node_key=end_node_key_authored)

    # create all the relationships between the articles and the references 
    print("Creating relationship CITES...")
    start_node_key_cites = ("Article", "_id")
    end_node_key_cites = ("Article", "_id")
    data_cites = []
    for i in range(len(articles)):
        for j in range(len(articles[i].references)):
            data_cites.append((articles[i]._id, {}, articles[i].references[j]))
    print("Creating relationship CITES in DB")
    create_relationships(graph, data_cites, "CITES", start_node_key=start_node_key_cites, end_node_key=end_node_key_cites)

        
    

def main():
    tracemalloc.start()
    start = time.time()
    # clean all
    print("Cleaning the json file...")
    cleanString(JSON_FILE, CLEANED_FILE, MAX_NODES)
    print("Cleaning done!")
    # connect to the graph
    print("Connecting to the graph...")
    graph = Graph(name="neo4j", password="test", host=NEO4J_IP)
    graph.run("MATCH (n) DETACH DELETE n")
    # preprocess the json file
    print("Preprocessing the json file...")
    authors, articles = preprocessJson(CLEANED_FILE)
    # write the nodes and the relationships in the graph
    print("Writing in the graph...")
    writeInDb(authors, articles, graph)
    end = time.time()
    current, peak = tracemalloc.get_traced_memory()
    print("Number of authors in the graph: ", graph.run("MATCH (a:Author) RETURN count(a) as count;").data()[0]["count"])
    print("Number of articles in the graph: ", graph.run("MATCH (a:Article) RETURN count(a) as count;").data()[0]["count"])
    print("Number of authored in the graph: ", graph.run("MATCH (a:Author)-[r:AUTHORED]->(b:Article) RETURN count(r) as count;").data()[0]["count"])
    print("Number of cites in the graph: ", graph.run("MATCH (a:Article)-[r:CITES]->(b:Article) RETURN count(r) as count;").data()[0]["count"])
    print("Time taken: ", str(datetime.timedelta(seconds=end-start)))
    print(f"Performance test result : (number of article = {MAX_NODES}, memory in MB = {peak/10**6}, time in seconds = {end-start})")
    tracemalloc.stop()

    

if __name__ == '__main__':  
    # sleep for 10 seconds to wait for neo4j to start
    print("Waiting for neo4j to start, sleeping for 15 sec...")
    time.sleep(15)
    main()

    # Debug tests
    # path = 'db.json'
    # print("Cleaning the json file...")
    # cleanString(path, 'dblpExampleCleaned2.json', MAX_NODES)
    # authors, articles = preprocessJson(path)
    # print(len(authors))
    # print(len(articles))
    # authors, articles = preprocessJson(CLEANED_FILE)
    # # print authors with no id
    # graph = Graph(name="neo4j", password="test", host="localhost")
    # # clean all
    # writeInDb(authors, articles, graph)
    # print("Done")
    
