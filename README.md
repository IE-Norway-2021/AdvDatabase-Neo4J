# Description of the graph : 

- Nodes : Articles and Authors : 
  - Articles : 
    - "_id" : id of the article
    - "title" : title of the article
    - "venue" : où a été publié l'article
      - "_id" : id of the venue
      - "type" : type of the venue. A changer l'encodage
      - "raw" : raw name of the venue
      - "raw_zh" : raw name of the venue v2
    - "year" : année de publication. A changer l'encodage
    - "keywords" : list of keywords related to article. Pas toujours renseigné
    - "fos" : list of fields of study related to article
    - "n_citation" : number of citations. A changer l'encodage
    - "page_start" : page start
    - "page_end" : page end
    - "lang" : language
    - "volume" : volume
    - "issue" : issue
    - "issn" : issn
    - "isbn" : isbn
    - "doi" : doi
    - "pdf" : pdf
    - "url" : list of urls
    - "abstract" : abstract
  - Authors : 
    - "_id" : id of the author
    - "name" : name of the author
    - "org" : organization of the author. Pas toujours renseigné
    - "orgid" : organization id of the author. Pas toujours renseigné
- Relathionships : Cite and Authored : 
  - Cite : from one article to the one cited
  - Authored : from the author to the article

"CREATE (a0:Article {title: 'charlie's lab', _id: '53e99809b7602d970201fa36'}), (a1:Article {title: 'Genes.', _id: '53e99785b7602d9701f405f5'}), (a2:Article {title: '3GIO.', _id: '53e99784b7602d9701f3e3f5'}), (a3:Article {title: 'The relationship between canopy parameters and spectrum of winter wheat under different irrigations in Hebei Province.', _id: '53e99784b7602d9701f3e133'});"

MATCH (a0:Article), (a1:Article), (a2:Article), (a3:Article), (b0:Author), (b1:Author), (b2:Author), (b3:Author), (b4:Author), (b5:Author), (b6:Author), (b7:Author) 

WHERE a0._id = '53f4670cdabfaeb22f540094' OR a1._id = '54057888dabfae91d3fe730e' OR a1._id = '53f45728dabfaec09f209538' OR a1._id = '53f48a96dabfaeb1a7cd1cc5' OR a3._id = '53f45728dabfaec09f209538' OR a3._id = '5601754345cedb3395e59457' OR a3._id = '53f38438dabfae4b34a08928' OR a3._id = '5601754345cedb3395e5945a' OR a3._id = '53f43d25dabfaeecd6995149' 

CREATE (a0)<-[:AUTHORED]-(b0), (a1)<-[:AUTHORED]-(b0), (a1)<-[:AUTHORED]-(b1), (a1)<-[:AUTHORED]-(b2), (a3)<-[:AUTHORED]-(b0), (a3)<-[:AUTHORED]-(b1), (a3)<-[:AUTHORED]-(b2), (a3)<-[:AUTHORED]-(b3), (a3)<-[:AUTHORED]-(b4);