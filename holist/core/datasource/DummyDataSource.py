from holist.core.Document import Document
import string
import random
test = """Enter the Wu-Tang (36 Chambers) is the debut album of American hip hop group Wu-Tang Clan, released November 9, 1993, on Loud Records and distributed through RCA Records. Recording sessions for the album took place during 1992 to 1993 at Firehouse Studio in New York City, and it was mastered at The Hit Factory. The album's title originates from the martial arts film The 36th Chamber of Shaolin (1978). The group's de facto leader RZA, also known as Prince Rakeem, produced the album entirely, utilizing heavy, eerie beats and a sound largely based on martial-arts movie clips and soul music samples.
The distinctive sound of Enter the Wu-Tang (36 Chambers) created a blueprint for hardcore hip hop during the 1990s and helped return New York City hip hop to national prominence. Its sound also became hugely influential in modern hip hop production, while the group members' explicit, humorous, and free-associative lyrics have served as a template for many subsequent hip hop records. Serving as a landmark record in the era of hip hop known as the East Coast Renaissance, its influence helped lead the way for several other East Coast hip hop artists, including Nas, The Notorious B.I.G., Mobb Deep, and Jay-Z.
Despite its raw, underground sound, the album had surprising chart success, peaking at number 41 on the US Billboard 200 chart. By 1995, it was certified platinum by the Recording Industry Association of America for shipments of one million copies in the United States. Initially receiving positive reviews from most music critics, Enter the Wu-Tang (36 Chambers) is regarded by some music writers as one of the most significant albums of the 1990s, as well as one of the greatest hip hop albums of all time. In 2003, the album was ranked number 386 on Rolling Stone magazine's list of the 500 greatest albums of all time."""
test = test.lower()
test = test.translate(string.maketrans("",""), string.punctuation)
test = test.split(" ")

class DummyDataSource(object):
    def getDocuments(self): #generates random documents
        return (Document(" ".join([random.choice(test) for w in range(50)])) for x in range(1000))
    def isStatic(self):
        return True