import os
import time
import re
import json
from py2neo import Graph, Node, Relationship
from classes import Author, Article
from clean import cleanString, cleanString2
import ijson


# JSON_FILE = os.environ['JSON_FILE']
# CLEANED_FILE = os.environ['CLEANED_FILE']
# MAX_NODES = os.environ['MAX_NODES']
# NEO4J_IP = os.environ['NEO4J_IP']

def preprocessJson(jsonFile):
    print("Preprocessing the json file...")
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
                    if ("name" in tmp[j]):
                        name = tmp[j]["name"]
                    author = Author(_id, name)
                    authorsArray.append(author)
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
    # create all the authors nodes and add them to the graph. Use only one cypher query to add all the nodes
    print("Creating authors nodes...")
    authorsCypher = "CREATE "
    for i in range(len(authors)):
        authorsCypher += f"(a{i}:Author {{name: '{authors[i].name}', _id: '{authors[i]._id}'}})"
        if (i != len(authors) - 1):
            authorsCypher += ", "
        if (i % 1000 == 0):
            print('\r', end='')
            print(f'Loading {round(i/len(authors)*100, 2)}%', end='')
    print('')
    authorsCypher += ";"
    graph.run(authorsCypher)
    # create all the articles nodes and add them to the graph. Use only one cypher query to add all the nodes
    print("Creating articles nodes...")
    articlesCypher = "CREATE "
    for i in range(len(articles)):
        articlesCypher += f"(a{i}:Article {{title: '{articles[i].title}', _id: '{articles[i]._id}'}})"
        if (i != len(articles) - 1):
            articlesCypher += ", "
        if (i % 1000 == 0):
            print('\r', end='')
            print(f'Loading {round(i/len(articles)*100, 2)}%', end='')
    print('')
    articlesCypher += ";"
    graph.run(articlesCypher)

    # create all the relationships between the articles and the authors. TODO optimise this
    print("Creating relationship AUTHORED...") 
    for i in range(len(articles)):
        for j in range(len(articles[i].authors)):
            graph.run(f"MATCH (a:Article {{_id: '{articles[i]._id}'}}), (b:Author {{_id: '{articles[i].authors[j]._id}'}}) CREATE (a)<-[:AUTHORED]-(b);")
        if (i % 1000 == 0):
            print('\r', end='')
            print(f'Loading {round(i/len(articles)*100, 2)}%', end='')
    print('')
    # create all the relationships between the articles and the references TODO optimise this
    print("Creating relationship CITES...")
    for i in range(len(articles)):
        for j in range(len(articles[i].references)):
            graph.run(f"MATCH (a:Article {{_id: '{articles[i]._id}'}}), (b:Article {{_id: '{articles[i].references[j]}'}}) CREATE (a)-[:CITES]->(b);")
        if (i % 1000 == 0):
            print('\r', end='')
            print(f'Loading {round(i/len(articles)*100, 2)}%', end='')
    print('')

        
    

def main():
    # clean all
    cleanString2(JSON_FILE, CLEANED_FILE)
    # connect to the graph
    graph = Graph(name="neo4j", password="test", host=NEO4J_IP)
    # preprocess the json file
    authors, articles = preprocessJson(CLEANED_FILE)
    # write the nodes and the relationships in the graph
    writeInDb(authors, articles, graph)
    

if __name__ == '__main__':  
    path = 'dblpExample.json'
    # path = 'dblpExampleCleaned2.json'
    # print("Cleaning the json file...")
    
    cleanString2(path, 'dblpExampleCleaned.json')
    # graph = Graph(name="neo4j", password="test", host="localhost")
    # # clean all
    # graph.run("MATCH (n) DETACH DELETE n")
    # authors, articles = preprocessJson(path)
    # print(len(authors))
    # print(len(articles))
    # writeInDb(authors, articles, graph)
    # print("Done")
    # sleep for 10 seconds to wait for neo4j to start
    # time.sleep(15)
    # main()