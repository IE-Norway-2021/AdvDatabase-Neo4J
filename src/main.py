import os
import time
import re
import json
from py2neo import Graph, Node, Relationship
from py2neo.bulk import create_nodes, create_relationships
from classes import Author, Article
from clean import cleanString
import ijson
import logging
from itertools import islice


JSON_FILE = os.environ['JSON_FILE']
CLEANED_FILE = os.environ['CLEANED_FILE']
MAX_NODES = int(os.environ['MAX_NODES'])
NEO4J_IP = os.environ['NEO4J_IP']
# JSON_FILE = "db.json"
# CLEANED_FILE = "dblpExampleCleanedTest.json"
# MAX_NODES = 10000
# NEO4J_IP = "localhost"
# create a logger to the console
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def preprocessJson(jsonFile):
    # preprocess the json file to get the nodes and the relationships. Split the json file in two arrays one for the authors and one for the papers
    authors: list[Author] = []
    articles: list[Article] = []
    # read the file as a json file. Only take the first MAX_NODES nodes
    with open(jsonFile, 'rb') as f:
        i = 0
        for record in ijson.items(f, 'item'):
            authorsArray = []
            if "authors" in record:
                # get the authors of the article
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
                    # find in authors if there is an author with the same _id, otherwise add it to the list TODO maybe optimise this
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
            # Show the progress
            if (i % 1000 == 0):
                print('\r', end='')
                print(f'Loading {round(i/MAX_NODES*100, 2)}%', end='')
            if (i == MAX_NODES):
                print('')
                break
        print('\nDone!')

        
    return authors, articles



def writeInDb(authors, articles, graph):
    # First create the nodes, then create the relationships
    # create all the authors nodes and add them to the graph. 
    print("Creating authors nodes data")
    keys_authors = ['_id', 'name']
    data_authors = []
    # create the data array for the authors
    for i in range(len(authors)):
        data_authors.append([authors[i]._id, authors[i].name])
        if (i % 1000 == 0):
            print('\r', end='')
            print(f'Loading {round(i/len(authors)*100, 2)}%', end='')
    print('')
    print("Creating authors nodes in DB")
    create_nodes(graph, data_authors,  labels={'Author'}, keys=keys_authors)
    
    # create the articles nodes and add them to the graph
    print("Creating articles nodes data")
    keys_articles = ['_id', 'title']
    data_articles = []
    # create the data array for the articles
    for i in range(len(articles)):
        data_articles.append([articles[i]._id, articles[i].title])
        if (i % 1000 == 0):
            print('\r', end='')
            print(f'Loading {round(i/len(articles)*100, 2)}%', end='')
    print('')
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
        if (i % 1000 == 0):
            print('\r', end='')
            print(f'Loading {round(i/len(articles)*100, 2)}%', end='')
    
    print('')
    print("Creating relationship AUTHORED in DB")
    stream = iter(data_authored)
    batch_size = (int)(MAX_NODES/10)
    while True:
        batch = islice(stream, batch_size)
        if batch:
            create_relationships(graph, batch, "AUTHORED", start_node_key=start_node_key_authored, end_node_key=end_node_key_authored)
        else:
            break

    # create all the relationships between the articles and the references 
    print("Creating relationship CITES...")
    start_node_key_cites = ("Article", "_id")
    end_node_key_cites = ("Article", "_id")
    data_cites = []
    for i in range(len(articles)):
        for j in range(len(articles[i].references)):
            data_cites.append((articles[i]._id, {}, articles[i].references[j]))
        if (i % 1000 == 0):
            print('\r', end='')
            print(f'Loading {round(i/len(articles)*100, 2)}%', end='')
    print('')
    print("Creating relationship CITES in DB")
    create_relationships(graph, data_cites, "CITES", start_node_key=start_node_key_cites, end_node_key=end_node_key_cites)

        
    

def main():
    
    # clean all
    print("Cleaning the json file...")
    cleanString(JSON_FILE, CLEANED_FILE, MAX_NODES)
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
    print("Number of authors in the graph: ", graph.run("MATCH (a:Author) RETURN count(a) as count;").data()[0]["count"])
    print("Number of authors in the json file: ", len(authors))
    print("Number of articles in the graph: ", graph.run("MATCH (a:Article) RETURN count(a) as count;").data()[0]["count"])
    print("Number of articles in the json file: ", len(articles))
    print("Number of authored in the graph: ", graph.run("MATCH (a:Author)-[r:AUTHORED]->(b:Article) RETURN count(r) as count;").data()[0]["count"])
    print("Number of cites in the graph: ", graph.run("MATCH (a:Article)-[r:CITES]->(b:Article) RETURN count(r) as count;").data()[0]["count"])
    

if __name__ == '__main__':  
    # path = 'db.json'
    # path = 'dblpExampleCleaned2.json'
    # print("Cleaning the json file...")
    
    # cleanString(path, 'dblpExampleCleanedTest.json', MAX_NODES)
   
    # authors, articles = preprocessJson(path)
    # print(len(authors))
    # print(len(articles))
    
    # sleep for 10 seconds to wait for neo4j to start
    print("Waiting for neo4j to start, sleeping for 15 sec...")
    time.sleep(15)
    main()
    # authors, articles = preprocessJson(CLEANED_FILE)
    # # print authors with no id
    # graph = Graph(name="neo4j", password="test", host="localhost")
    # # clean all
    # writeInDb(authors, articles, graph)
    # print("Done")
    
