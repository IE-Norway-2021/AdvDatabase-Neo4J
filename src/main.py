import os
import time
import re
import json
from py2neo import Graph, Node, Relationship
from classes import Author, Article

# JSON_FILE = os.environ['JSON_FILE']
# CLEANED_FILE = os.environ['CLEANED_FILE']
# MAX_NODES = os.environ['MAX_NODES']
# NEO4J_IP = os.environ['NEO4J_IP']

def cleanString(jsonFile):
    # clean the string. Open the file as needed since it is too big to load into memory
    with open(jsonFile, 'r', encoding='utf-8') as f:
        with open('dblpExampleCleaned2.json', 'w', encoding='utf-8') as f2:
            length = f.seek(0, os.SEEK_END)
            i = 0
            for line in f:
                # regex to find all NumberInt(...) and replace it with the number inside of the parenthesis
                line = re.sub(r'NumberInt\((\d+)\)', r'\1', line)
                # remove all \\" in the string
                line = line.replace('\\"', '')
                # remove all \ in the string
                line = line.replace('\\', '')
                # escape all the ' in the string
                line = line.replace("'", "\\\\'")
                f2.write(line)
                # Show the progress
                if (i % 100000 == 0):
                    print('\r', end='')
                    print(f'Loading {round(i/length*100, 2)}%', end='')
                i +=1


def preprocessJson(jsonFile):
    # preprocess the json file to get the nodes and the relationships. Split the json file in two arrays one for the authors and one for the papers
    authors: list[Author] = []
    articles: list[Article] = []
    # read the file as a json file. Only take the first MAX_NODES nodes
    with open(jsonFile, 'r', encoding="utf-8") as f:
        # load the json file as a dictionary
        jsonDict = json.load(f)
        # go through the array
        for i in range(len(jsonDict)):
            authorsArray = []
            if "authors" in jsonDict[i]:
                # get the authors of the article
                tmp = jsonDict[i]["authors"]
                # go through all the authors
                for j in range(len(tmp)):
                    _id, name = "", ""
                    if ("_id" in tmp[j]):
                        _id = tmp[j]["_id"]
                    if ("name" in tmp[j]):
                        name = tmp[j]["name"]
                    author = Author(_id, name)
                    authorsArray.append(author)
                    # find in authors if there is an author with the same _id, otherwise add it to the list
                    if (not any(author._id == a._id for a in authors)):
                        authors.append(author)
            # extract articles
            tmp = jsonDict[i]
            _id, title, references = "", "", [] 
            if ("title" in tmp ):
                title = tmp["title"]
            if ("_id" in tmp):
                _id = tmp["_id"]
            if ("references" in tmp):
                references = tmp["references"]
            article = Article(_id, title, authorsArray, references)
            articles.append(article)

        
    return authors, articles




def writeInDb(authors, articles, graph):
    # First create the nodes, then create the relationships
    # create all the authors nodes and add them to the graph. Use only one cypher query to add all the nodes
    authorsCypher = "CREATE "
    for i in range(len(authors)):
        authorsCypher += f"(a{i}:Author {{name: '{authors[i].name}', _id: '{authors[i]._id}'}})"
        if (i != len(authors) - 1):
            authorsCypher += ", "
    authorsCypher += ";"
    graph.run(authorsCypher)
    # create all the articles nodes and add them to the graph. Use only one cypher query to add all the nodes
    articlesCypher = "CREATE "
    for i in range(len(articles)):
        articlesCypher += f"(a{i}:Article {{title: '{articles[i].title}', _id: '{articles[i]._id}'}})"
        if (i != len(articles) - 1):
            articlesCypher += ", "
    articlesCypher += ";"
    graph.run(articlesCypher)
    # create all the relationships between the articles and the authors. 
    for i in range(len(articles)):
        for j in range(len(articles[i].authors)):
            graph.run(f"MATCH (a:Article {{_id: '{articles[i]._id}'}}), (b:Author {{_id: '{articles[i].authors[j]._id}'}}) CREATE (a)<-[:AUTHORED]-(b);")
    # create all the relationships between the articles and the references
    for i in range(len(articles)):
        for j in range(len(articles[i].references)):
            graph.run(f"MATCH (a:Article {{_id: '{articles[i]._id}'}}), (b:Article {{_id: '{articles[i].references[j]}'}}) CREATE (a)-[:CITES]->(b);")

        
    

def main():
    # connect to the graph
    graph = Graph(name="neo4j", password="root", host=NEO4J_IP, secure=True)
    # preprocess the json file
    authors, articles = preprocessJson(JSON_FILE)
    # write the nodes and the relationships in the graph
    writeInDb(authors, articles, graph)
    

if __name__ == '__main__':  
    path = 'db.json'
    print("Cleaning the json file...")
    cleanString(path)
    graph = Graph(name="neo4j", password="test", host="localhost")
    # clean all
    graph.run("MATCH (n) DETACH DELETE n")
    print("Preprocessing the json file...")
    authors, articles = preprocessJson('dblpExampleCleaned2.json')
    writeInDb(authors, articles, graph)
    
    # sleep for 10 seconds to wait for neo4j to start
    #time.sleep(10)
    #main()